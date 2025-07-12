import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Movie Card Component
const MovieCard = ({ movie, onPlay }) => {
  const getMovieIcon = (format) => {
    const iconMap = {
      mp4: '🎬',
      mkv: '🎞️',
      avi: '📽️',
      mov: '🎥',
      wmv: '📹',
      default: '🎬'
    };
    return iconMap[format?.toLowerCase()] || iconMap.default;
  };

  return (
    <div 
      className="movie-card bg-gray-800 rounded-lg p-4 hover:bg-gray-700 transition-all duration-300 cursor-pointer transform hover:scale-105"
      onClick={() => onPlay(movie)}
    >
      <div className="movie-icon text-6xl mb-3 text-center">
        {getMovieIcon(movie.format)}
      </div>
      <h3 className="movie-title text-white text-sm font-medium text-center truncate">
        {movie.name.replace(/\.[^/.]+$/, "")} {/* Remove extension */}
      </h3>
      <p className="movie-format text-gray-400 text-xs text-center mt-1 uppercase">
        {movie.format}
      </p>
    </div>
  );
};

// Video Player Component
const VideoPlayer = ({ movie, onClose }) => {
  const videoUrl = `${API}/stream${movie.path}`;

  return (
    <div className="video-player-overlay fixed inset-0 bg-black bg-opacity-95 z-50 flex items-center justify-center">
      <div className="video-container w-full h-full flex flex-col">
        {/* Header with close button */}
        <div className="video-header flex justify-between items-center p-4 bg-black bg-opacity-50">
          <h2 className="text-white text-xl font-semibold">
            {movie.name.replace(/\.[^/.]+$/, "")}
          </h2>
          <button 
            onClick={onClose}
            className="close-button text-white text-2xl hover:text-red-500 transition-colors"
          >
            ✕
          </button>
        </div>
        
        {/* Video player */}
        <div className="video-wrapper flex-1 flex items-center justify-center">
          <video
            src={videoUrl}
            controls
            autoPlay
            className="w-full h-full max-w-full max-h-full"
            style={{ objectFit: 'contain' }}
          >
            Votre navigateur ne supporte pas la lecture vidéo.
          </video>
        </div>
      </div>
    </div>
  );
};

// Loading Component
const LoadingSpinner = () => (
  <div className="flex items-center justify-center min-h-screen bg-gray-900">
    <div className="loading-spinner">
      <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500"></div>
      <p className="text-white mt-4">Connexion au NAS...</p>
    </div>
  </div>
);

// Error Component
const ErrorMessage = ({ message, onRetry }) => (
  <div className="flex items-center justify-center min-h-screen bg-gray-900">
    <div className="text-center">
      <div className="text-red-500 text-6xl mb-4">⚠️</div>
      <h2 className="text-white text-xl mb-4">Erreur de connexion</h2>
      <p className="text-gray-400 mb-6">{message}</p>
      <button 
        onClick={onRetry}
        className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors"
      >
        Réessayer
      </button>
    </div>
  </div>
);

// Main App Component
function App() {
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedMovie, setSelectedMovie] = useState(null);
  const [nasConnected, setNasConnected] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // Test NAS connection
  const testConnection = async () => {
    try {
      const response = await axios.get(`${API}/connection/test`);
      setNasConnected(response.data.connected);
      return response.data.connected;
    } catch (err) {
      console.error('Connection test failed:', err);
      setNasConnected(false);
      return false;
    }
  };

  // Load movies
  const loadMovies = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Test connection first
      const connected = await testConnection();
      if (!connected) {
        throw new Error('Impossible de se connecter au NAS Buffalo LinkStation');
      }

      const response = await axios.get(`${API}/movies`);
      setMovies(response.data.movies);
    } catch (err) {
      console.error('Error loading movies:', err);
      setError(err.response?.data?.detail || err.message || 'Erreur lors du chargement des films');
    } finally {
      setLoading(false);
    }
  };

  // Initial load
  useEffect(() => {
    loadMovies();
  }, []);

  // Handle movie play
  const handlePlayMovie = (movie) => {
    setSelectedMovie(movie);
  };

  // Handle close player
  const handleClosePlayer = () => {
    setSelectedMovie(null);
  };

  // Filter movies based on search
  const filteredMovies = movies.filter(movie =>
    movie.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Loading state
  if (loading) {
    return <LoadingSpinner />;
  }

  // Error state
  if (error) {
    return <ErrorMessage message={error} onRetry={loadMovies} />;
  }

  return (
    <div className="App min-h-screen bg-gray-900">
      {/* Header */}
      <header className="app-header bg-black bg-opacity-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-4">
              <h1 className="text-3xl font-bold text-white">🎬 NAS Cinema</h1>
              <div className={`status-indicator px-3 py-1 rounded-full text-sm ${
                nasConnected ? 'bg-green-600 text-white' : 'bg-red-600 text-white'
              }`}>
                {nasConnected ? '🟢 Connecté' : '🔴 Déconnecté'}
              </div>
            </div>
            <div className="nas-info text-gray-400 text-sm">
              Buffalo LS220DE • 192.168.1.152
            </div>
          </div>

          {/* Search Bar */}
          <div className="search-container max-w-md">
            <input
              type="text"
              placeholder="Rechercher un film..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-4 py-2 bg-gray-800 text-white rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none"
            />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content p-6">
        <div className="max-w-7xl mx-auto">
          {/* Movies Count */}
          <div className="movies-count mb-6">
            <h2 className="text-xl text-white font-semibold">
              {filteredMovies.length} film{filteredMovies.length !== 1 ? 's' : ''} trouvé{filteredMovies.length !== 1 ? 's' : ''}
            </h2>
          </div>

          {/* Movies Grid */}
          {filteredMovies.length === 0 ? (
            <div className="no-movies text-center py-12">
              <div className="text-gray-500 text-6xl mb-4">🎭</div>
              <h3 className="text-white text-xl mb-2">Aucun film trouvé</h3>
              <p className="text-gray-400">
                {searchTerm ? 'Essayez un autre terme de recherche' : 'Vérifiez le dossier Films sur votre NAS'}
              </p>
            </div>
          ) : (
            <div className="movies-grid grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-6">
              {filteredMovies.map((movie, index) => (
                <MovieCard 
                  key={movie.id || index} 
                  movie={movie} 
                  onPlay={handlePlayMovie}
                />
              ))}
            </div>
          )}
        </div>
      </main>

      {/* Video Player Modal */}
      {selectedMovie && (
        <VideoPlayer 
          movie={selectedMovie} 
          onClose={handleClosePlayer}
        />
      )}

      {/* Footer */}
      <footer className="footer text-center py-4 text-gray-500 text-sm">
        <p>🏠 Lecteur multimédia local • Buffalo LinkStation LS220DE</p>
      </footer>
    </div>
  );
}

export default App;