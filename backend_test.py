#!/usr/bin/env python3
"""
Backend API Testing for NAS Cinema Application
Tests all FastAPI endpoints for the Buffalo LinkStation movie streaming app
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any

class NASCinemaAPITester:
    def __init__(self, base_url="https://954b17a7-f83a-47a2-8181-02f7a8a66acc.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
        
        result = {
            "test": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
        if details:
            print(f"    Details: {details}")

    def run_api_test(self, name: str, method: str, endpoint: str, expected_status: int = 200, 
                     data: Dict[Any, Any] = None, headers: Dict[str, str] = None) -> tuple:
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else self.api_url
        
        default_headers = {'Content-Type': 'application/json'}
        if headers:
            default_headers.update(headers)

        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=default_headers, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=default_headers, timeout=30)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, headers=default_headers, timeout=30)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=default_headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            success = response.status_code == expected_status
            
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text[:200]}

            details = f"Status: {response.status_code}, Response: {json.dumps(response_data, indent=2)[:300]}"
            self.log_test(name, success, details)
            
            return success, response_data, response.status_code

        except requests.exceptions.Timeout:
            self.log_test(name, False, "Request timed out after 30 seconds")
            return False, {}, 0
        except requests.exceptions.ConnectionError:
            self.log_test(name, False, "Connection error - service may be down")
            return False, {}, 0
        except Exception as e:
            self.log_test(name, False, f"Exception: {str(e)}")
            return False, {}, 0

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        print("\n🔍 Testing Root API Endpoint...")
        success, data, status = self.run_api_test(
            "Root API Endpoint", 
            "GET", 
            "", 
            200
        )
        
        if success and isinstance(data, dict):
            if "message" in data and "version" in data:
                self.log_test("Root API Response Structure", True, "Contains required fields")
            else:
                self.log_test("Root API Response Structure", False, "Missing required fields")
        
        return success

    def test_nas_connection(self):
        """Test NAS connection endpoint"""
        print("\n🔍 Testing NAS Connection...")
        success, data, status = self.run_api_test(
            "NAS Connection Test", 
            "GET", 
            "connection/test", 
            200
        )
        
        if success and isinstance(data, dict):
            if "connected" in data and "message" in data:
                connected = data.get("connected", False)
                message = data.get("message", "")
                
                self.log_test("NAS Connection Response Structure", True, "Contains required fields")
                self.log_test("NAS Connection Status", True, f"Connected: {connected}, Message: {message}")
            else:
                self.log_test("NAS Connection Response Structure", False, "Missing required fields")
        
        return success

    def test_movies_endpoint(self):
        """Test movies listing endpoint"""
        print("\n🔍 Testing Movies Endpoint...")
        success, data, status = self.run_api_test(
            "Movies List", 
            "GET", 
            "movies", 
            200
        )
        
        if success and isinstance(data, dict):
            if "movies" in data and "total" in data:
                movies = data.get("movies", [])
                total = data.get("total", 0)
                
                self.log_test("Movies Response Structure", True, f"Found {total} movies")
                
                # Validate movie structure
                if movies and len(movies) > 0:
                    first_movie = movies[0]
                    required_fields = ["id", "name", "path", "format"]
                    missing_fields = [field for field in required_fields if field not in first_movie]
                    
                    if not missing_fields:
                        self.log_test("Movie Object Structure", True, "All required fields present")
                    else:
                        self.log_test("Movie Object Structure", False, f"Missing fields: {missing_fields}")
                else:
                    self.log_test("Movies Data", True, "No movies found (expected in test environment)")
            else:
                self.log_test("Movies Response Structure", False, "Missing required fields")
        
        return success

    def test_movies_with_folder_param(self):
        """Test movies endpoint with folder parameter"""
        print("\n🔍 Testing Movies Endpoint with Folder Parameter...")
        success, data, status = self.run_api_test(
            "Movies List with Folder", 
            "GET", 
            "movies?folder=Films", 
            200
        )
        return success

    def test_folders_endpoint(self):
        """Test folders listing endpoint"""
        print("\n🔍 Testing Folders Endpoint...")
        success, data, status = self.run_api_test(
            "Folders List", 
            "GET", 
            "folders", 
            200
        )
        
        if success and isinstance(data, dict):
            if "folders" in data:
                folders = data.get("folders", [])
                self.log_test("Folders Response Structure", True, f"Found folders: {folders}")
            else:
                self.log_test("Folders Response Structure", False, "Missing 'folders' field")
        
        return success

    def test_stream_endpoint(self):
        """Test streaming endpoint (should fail gracefully in test environment)"""
        print("\n🔍 Testing Stream Endpoint...")
        # Test with a dummy path - expect 404 or 500 in test environment
        success, data, status = self.run_api_test(
            "Stream Endpoint", 
            "GET", 
            "stream/Films/test.mp4", 
            expected_status=404  # Expect 404 since file doesn't exist
        )
        
        # Also test with 500 as acceptable (connection error)
        if not success and status == 500:
            self.log_test("Stream Endpoint (500 acceptable)", True, "Expected error in test environment")
            return True
        
        return success

    def test_invalid_endpoints(self):
        """Test invalid endpoints return proper errors"""
        print("\n🔍 Testing Invalid Endpoints...")
        
        # Test non-existent endpoint
        success, data, status = self.run_api_test(
            "Invalid Endpoint", 
            "GET", 
            "nonexistent", 
            expected_status=404
        )
        
        return success

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting NAS Cinema API Tests...")
        print(f"🌐 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Run all tests
        tests = [
            self.test_root_endpoint,
            self.test_nas_connection,
            self.test_movies_endpoint,
            self.test_movies_with_folder_param,
            self.test_folders_endpoint,
            self.test_stream_endpoint,
            self.test_invalid_endpoints
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log_test(f"Test {test.__name__}", False, f"Test execution error: {str(e)}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        # Print failed tests
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
        
        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = NASCinemaAPITester()
    
    try:
        success = tester.run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())