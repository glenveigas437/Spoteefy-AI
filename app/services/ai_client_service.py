"""
AI Client Service - Makes API calls to treble-clef microservice
"""

import requests
import json
import os
from typing import Dict, List, Any

class AIClientService:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.environ.get('TREBLE_CLEF_URL', 'http://localhost:3000')
        self.api_prefix = "/api/v1"
    
    def _make_request(self, endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
        """Make HTTP request to treble-clef microservice"""
        url = f"{self.base_url}{self.api_prefix}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error making request to treble-clef: {e}")
            return {"success": False, "error": str(e)}
    
    def get_recommendations(self, top_artists: List[str], top_tracks: List[str], 
                          mood: str, genre: str, language: str, limit: int = 20) -> Dict:
        """Get AI-powered recommendations from treble-clef"""
        data = {
            "top_artists": top_artists,
            "top_tracks": top_tracks,
            "mood": mood,
            "genre": genre,
            "language": language,
            "limit": limit
        }
        return self._make_request("/recommendations", method="POST", data=data)
    
    def analyze_music_taste(self, top_artists: List[str], top_tracks: List[str], recent_tracks: List[str]) -> Dict:
        data = {
            "top_artists": top_artists,
            "top_tracks": top_tracks,
            "recent_tracks": recent_tracks
        }
        return self._make_request("/analyze", method="POST", data=data)
    
    def generate_playlist_concept(self, theme: str, mood: str, genre: str, duration: int = 60) -> Dict:
        data = {
            "theme": theme,
            "mood": mood,
            "genre": genre,
            "duration": duration
        }
        return self._make_request("/playlist-concept", method="POST", data=data)
    
    def discover_music(self, seed_artists: List[str], seed_tracks: List[str], mood: str, genre: str, language: str, limit: int = 20) -> Dict:
        data = {
            "seed_artists": seed_artists,
            "seed_tracks": seed_tracks,
            "mood": mood,
            "genre": genre,
            "language": language,
            "limit": limit
        }
        return self._make_request("/discover", method="POST", data=data)
    
    def health_check(self) -> Dict:
        return self._make_request("/health", method="GET") 