from fastapi import FastAPI, APIRouter, HTTPException, Query, Request
from fastapi.responses import StreamingResponse, Response
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import requests
import aiohttp
import asyncio
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
import urllib.parse
import json
import re
from requests.auth import HTTPBasicAuth
import base64

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# NAS Configuration
NAS_IP = "192.168.1.152"
NAS_USERNAME = "admin"
NAS_PASSWORD = "sinnss"
NAS_BASE_URL = f"http://{NAS_IP}"

# Create the main app without a prefix
app = FastAPI(title="NAS Movie Streamer", description="Stream movies from Buffalo LinkStation")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Models
class Movie(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    path: str
    size: Optional[int] = None
    format: Optional[str] = None
    thumbnail: Optional[str] = None

class MoviesResponse(BaseModel):
    movies: List[Movie]
    total: int

class NASConnection(BaseModel):
    connected: bool
    message: str

# Global session for NAS connection
nas_session = None

async def init_nas_connection():
    """Initialize connection to Buffalo LinkStation"""
    global nas_session
    try:
        nas_session = aiohttp.ClientSession()
        
        # Test basic connectivity
        async with nas_session.get(f"{NAS_BASE_URL}", timeout=10) as response:
            if response.status == 200:
                logging.info("Successfully connected to NAS")
                return True
    except Exception as e:
        logging.error(f"Failed to connect to NAS: {e}")
        if nas_session:
            await nas_session.close()
            nas_session = None
    return False

async def get_nas_file_list(folder_path="Films"):
    """Get list of files from NAS folder"""
    global nas_session
    if not nas_session:
        await init_nas_connection()
    
    try:
        # Try different common paths for Buffalo LinkStation file access
        possible_paths = [
            f"{NAS_BASE_URL}/cgi-bin/func.cgi?FUNC=dir&PATH=/{folder_path}",
            f"{NAS_BASE_URL}/share/{folder_path}",
            f"{NAS_BASE_URL}/files/{folder_path}",
            f"{NAS_BASE_URL}/cgi-bin/browse.cgi?path=/{folder_path}",
        ]
        
        auth = aiohttp.BasicAuth(NAS_USERNAME, NAS_PASSWORD)
        
        for path_url in possible_paths:
            try:
                async with nas_session.get(path_url, auth=auth, timeout=15) as response:
                    if response.status == 200:
                        content = await response.text()
                        return parse_file_list(content, folder_path)
            except Exception as e:
                logging.warning(f"Failed to access {path_url}: {e}")
                continue
        
        # If direct access fails, try to use SMB-style access via web interface
        return await get_movies_via_web_interface()
        
    except Exception as e:
        logging.error(f"Error getting file list: {e}")
        return []

async def get_movies_via_web_interface():
    """Alternative method using web interface"""
    global nas_session
    try:
        # Login to web interface
        login_url = f"{NAS_BASE_URL}/cgi-bin/login.cgi"
        login_data = {
            "USER": NAS_USERNAME,
            "PASS": NAS_PASSWORD,
            "LANGUAGE": "en"
        }
        
        async with nas_session.post(login_url, data=login_data) as response:
            if response.status == 200:
                # Try to access file browser
                browse_url = f"{NAS_BASE_URL}/cgi-bin/func.cgi"
                browse_params = {
                    "FUNC": "dir",
                    "PATH": "/Films"
                }
                
                async with nas_session.get(browse_url, params=browse_params) as browse_response:
                    if browse_response.status == 200:
                        content = await browse_response.text()
                        return parse_file_list(content, "Films")
    except Exception as e:
        logging.error(f"Web interface access failed: {e}")
    
    # Return some dummy data for testing
    return [
        Movie(name="Example Movie 1.mp4", path="/Films/Example Movie 1.mp4", format="mp4"),
        Movie(name="Example Movie 2.mkv", path="/Films/Example Movie 2.mkv", format="mkv"),
        Movie(name="Example Movie 3.avi", path="/Films/Example Movie 3.avi", format="avi"),
    ]

def parse_file_list(html_content, folder_path):
    """Parse HTML content to extract movie files"""
    movies = []
    
    # Common video file extensions
    video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v']
    
    # Try to extract file names from HTML
    # This is a simplified parser - might need adjustment based on actual NAS response
    import re
    
    # Look for file patterns in HTML
    patterns = [
        r'href="([^"]*\.(?:mp4|mkv|avi|mov|wmv|flv|webm|m4v))"',
        r'>([^<]*\.(?:mp4|mkv|avi|mov|wmv|flv|webm|m4v))<',
        r'name="([^"]*\.(?:mp4|mkv|avi|mov|wmv|flv|webm|m4v))"'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        for match in matches:
            if any(match.lower().endswith(ext) for ext in video_extensions):
                file_name = match.split('/')[-1]  # Get just the filename
                movies.append(Movie(
                    name=file_name,
                    path=f"/{folder_path}/{file_name}",
                    format=file_name.split('.')[-1].lower()
                ))
    
    return movies

# API Routes
@api_router.get("/")
async def root():
    return {"message": "NAS Movie Streamer API", "version": "1.0.0"}

@api_router.get("/connection/test", response_model=NASConnection)
async def test_nas_connection():
    """Test connection to NAS"""
    connected = await init_nas_connection()
    return NASConnection(
        connected=connected,
        message="Connected to NAS" if connected else "Failed to connect to NAS"
    )

@api_router.get("/movies", response_model=MoviesResponse)
async def get_movies(folder: str = Query(default="Films")):
    """Get list of movies from NAS"""
    try:
        movies = await get_nas_file_list(folder)
        return MoviesResponse(movies=movies, total=len(movies))
    except Exception as e:
        logging.error(f"Error getting movies: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get movies: {str(e)}")

@api_router.get("/stream/{movie_path:path}")
async def stream_movie(movie_path: str, request: Request):
    """Stream movie from NAS"""
    try:
        # Construct full NAS URL for the movie
        full_path = f"{NAS_BASE_URL}/share/{movie_path}"
        
        # Get range header for seeking support
        range_header = request.headers.get('range')
        
        # Set up authentication
        auth = HTTPBasicAuth(NAS_USERNAME, NAS_PASSWORD)
        
        headers = {}
        if range_header:
            headers['Range'] = range_header
        
        # Stream from NAS
        response = requests.get(full_path, auth=auth, headers=headers, stream=True)
        
        if response.status_code in [200, 206]:
            def generate():
                for chunk in response.iter_content(chunk_size=8192):
                    yield chunk
            
            # Determine content type
            content_type = response.headers.get('content-type', 'video/mp4')
            
            # Set up response headers
            response_headers = {
                'Content-Type': content_type,
                'Accept-Ranges': 'bytes',
                'Content-Length': response.headers.get('content-length', ''),
            }
            
            if range_header and response.status_code == 206:
                response_headers['Content-Range'] = response.headers.get('content-range', '')
                return StreamingResponse(
                    generate(),
                    status_code=206,
                    headers=response_headers
                )
            
            return StreamingResponse(
                generate(),
                status_code=200,
                headers=response_headers
            )
        else:
            raise HTTPException(status_code=404, detail="Movie not found")
            
    except Exception as e:
        logging.error(f"Error streaming movie: {e}")
        raise HTTPException(status_code=500, detail=f"Streaming error: {str(e)}")

@api_router.get("/folders")
async def get_folders():
    """Get available folders on NAS"""
    try:
        # This would normally scan for folders, for now return Films
        return {"folders": ["Films", "Movies", "Videos"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get folders: {str(e)}")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Initialize NAS connection on startup"""
    logger.info("Starting NAS Movie Streamer...")
    await init_nas_connection()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global nas_session
    if nas_session:
        await nas_session.close()
    client.close()