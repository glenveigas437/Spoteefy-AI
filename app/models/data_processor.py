"""
Data processor for Spotify data
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
import logging

class SpotifyDataProcessor:
    """Process Spotify data for AI model training"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def process_user_data(self, user_tracks: List[Dict], user_artists: List[Dict]) -> Dict:
        """Process user's listening data"""
        processed_data = {
            'tracks': [],
            'artists': [],
            'genres': [],
            'features': []
        }
        
        # Process tracks
        for track in user_tracks:
            processed_track = self._process_track(track)
            if processed_track:
                processed_data['tracks'].append(processed_track)
        
        # Process artists
        for artist in user_artists:
            processed_artist = self._process_artist(artist)
            if processed_artist:
                processed_data['artists'].append(processed_artist)
        
        # Extract genres
        genres = []
        for artist in user_artists:
            genres.extend(artist.get('genres', []))
        processed_data['genres'] = list(set(genres))
        
        # Extract audio features
        for track in user_tracks:
            if 'audio_features' in track:
                features = self._extract_audio_features(track['audio_features'])
                processed_data['features'].append(features)
        
        return processed_data
    
    def _process_track(self, track: Dict) -> Optional[Dict]:
        """Process individual track data"""
        try:
            processed = {
                'id': track.get('id'),
                'name': track.get('name', ''),
                'popularity': track.get('popularity', 0),
                'duration_ms': track.get('duration_ms', 0),
                'explicit': track.get('explicit', False),
                'artists': [artist.get('name', '') for artist in track.get('artists', [])],
                'album': track.get('album', {}).get('name', ''),
                'release_date': track.get('album', {}).get('release_date', ''),
                'genres': []
            }
            
            # Extract genres from artists
            for artist in track.get('artists', []):
                if 'genres' in artist:
                    processed['genres'].extend(artist['genres'])
            
            processed['genres'] = list(set(processed['genres']))
            
            # Add audio features if available
            if 'audio_features' in track:
                processed['audio_features'] = track['audio_features']
            
            return processed
            
        except Exception as e:
            self.logger.error(f"Error processing track {track.get('id', 'unknown')}: {e}")
            return None
    
    def _process_artist(self, artist: Dict) -> Optional[Dict]:
        """Process individual artist data"""
        try:
            processed = {
                'id': artist.get('id'),
                'name': artist.get('name', ''),
                'popularity': artist.get('popularity', 0),
                'genres': artist.get('genres', []),
                'followers': artist.get('followers', {}).get('total', 0)
            }
            
            return processed
            
        except Exception as e:
            self.logger.error(f"Error processing artist {artist.get('id', 'unknown')}: {e}")
            return None
    
    def _extract_audio_features(self, audio_features: Dict) -> Dict:
        """Extract and normalize audio features"""
        features = {
            'danceability': audio_features.get('danceability', 0.5),
            'energy': audio_features.get('energy', 0.5),
            'key': audio_features.get('key', 0),
            'loudness': audio_features.get('loudness', -60),
            'mode': audio_features.get('mode', 1),
            'speechiness': audio_features.get('speechiness', 0.0),
            'acousticness': audio_features.get('acousticness', 0.0),
            'instrumentalness': audio_features.get('instrumentalness', 0.0),
            'liveness': audio_features.get('liveness', 0.0),
            'valence': audio_features.get('valence', 0.5),
            'tempo': audio_features.get('tempo', 120.0)
        }
        
        return features
    
    def create_training_dataset(self, users_data: List[Tuple[str, Dict]]) -> pd.DataFrame:
        """Create training dataset from multiple users"""
        dataset = []
        
        for user_id, user_data in users_data:
            processed = self.process_user_data(
                user_data.get('tracks', []),
                user_data.get('artists', [])
            )
            
            # Create user features
            user_features = self._create_user_features(processed)
            user_features['user_id'] = user_id
            
            dataset.append(user_features)
        
        return pd.DataFrame(dataset)
    
    def _create_user_features(self, processed_data: Dict) -> Dict:
        """Create user-level features"""
        features = {}
        
        # Track-based features
        tracks = processed_data['tracks']
        if tracks:
            features['avg_popularity'] = np.mean([t['popularity'] for t in tracks])
            features['avg_duration'] = np.mean([t['duration_ms'] for t in tracks])
            features['explicit_ratio'] = sum(1 for t in tracks if t['explicit']) / len(tracks)
        
        # Artist-based features
        artists = processed_data['artists']
        if artists:
            features['avg_artist_popularity'] = np.mean([a['popularity'] for a in artists])
            features['avg_followers'] = np.mean([a['followers'] for a in artists])
        
        # Genre-based features
        genres = processed_data['genres']
        features['genre_diversity'] = len(genres)
        
        # Audio feature averages
        audio_features = processed_data['features']
        if audio_features:
            feature_names = ['danceability', 'energy', 'valence', 'acousticness', 'instrumentalness']
            for feature in feature_names:
                values = [f[feature] for f in audio_features if feature in f]
                if values:
                    features[f'avg_{feature}'] = np.mean(values)
                    features[f'std_{feature}'] = np.std(values)
        
        return features
    
    def create_recommendation_context(self, user_tracks: List[Dict], 
                                    mood: str = None, genre: str = None) -> Dict:
        """Create context for recommendations"""
        context = {
            'user_tracks': user_tracks,
            'mood': mood,
            'genre': genre,
            'track_features': [],
            'artist_features': []
        }
        
        # Extract features from user tracks
        for track in user_tracks:
            features = self._extract_track_features_for_context(track)
            context['track_features'].append(features)
        
        # Add mood and genre context
        if mood:
            context['mood_context'] = self._get_mood_context(mood)
        
        if genre:
            context['genre_context'] = self._get_genre_context(genre)
        
        return context
    
    def _extract_track_features_for_context(self, track: Dict) -> Dict:
        """Extract features for recommendation context"""
        features = {
            'id': track.get('id'),
            'name': track.get('name', ''),
            'artists': [artist.get('name', '') for artist in track.get('artists', [])],
            'genres': []
        }
        
        # Extract genres
        for artist in track.get('artists', []):
            if 'genres' in artist:
                features['genres'].extend(artist['genres'])
        
        features['genres'] = list(set(features['genres']))
        
        # Add audio features if available
        if 'audio_features' in track:
            features.update(self._extract_audio_features(track['audio_features']))
        
        return features
    
    def _get_mood_context(self, mood: str) -> Dict:
        """Get mood-specific context"""
        mood_contexts = {
            'energetic': {
                'target_energy': 0.8,
                'target_danceability': 0.7,
                'target_tempo': 130,
                'keywords': ['energetic', 'upbeat', 'fast', 'dynamic']
            },
            'chill': {
                'target_energy': 0.3,
                'target_danceability': 0.4,
                'target_tempo': 80,
                'keywords': ['chill', 'relaxing', 'ambient', 'calm']
            },
            'happy': {
                'target_energy': 0.7,
                'target_danceability': 0.6,
                'target_valence': 0.8,
                'keywords': ['happy', 'positive', 'uplifting', 'joyful']
            },
            'melancholic': {
                'target_energy': 0.3,
                'target_danceability': 0.3,
                'target_valence': 0.2,
                'keywords': ['melancholic', 'sad', 'emotional', 'introspective']
            },
            'party': {
                'target_energy': 0.9,
                'target_danceability': 0.9,
                'target_tempo': 140,
                'keywords': ['party', 'dance', 'club', 'festive']
            },
            'focused': {
                'target_energy': 0.4,
                'target_danceability': 0.3,
                'target_instrumentalness': 0.7,
                'keywords': ['focus', 'study', 'instrumental', 'concentration']
            },
            'romantic': {
                'target_energy': 0.4,
                'target_danceability': 0.5,
                'target_valence': 0.6,
                'keywords': ['romantic', 'love', 'intimate', 'passionate']
            },
            'workout': {
                'target_energy': 0.9,
                'target_danceability': 0.8,
                'target_tempo': 130,
                'keywords': ['workout', 'gym', 'motivation', 'intense']
            }
        }
        
        return mood_contexts.get(mood, {})
    
    def _get_genre_context(self, genre: str) -> Dict:
        """Get genre-specific context"""
        genre_contexts = {
            'pop': {
                'target_valence': 0.7,
                'target_danceability': 0.8,
                'keywords': ['pop', 'mainstream', 'catchy']
            },
            'rock': {
                'target_energy': 0.8,
                'target_valence': 0.5,
                'keywords': ['rock', 'guitar', 'powerful']
            },
            'hip-hop': {
                'target_danceability': 0.8,
                'target_energy': 0.7,
                'keywords': ['hip-hop', 'rap', 'urban']
            },
            'electronic': {
                'target_energy': 0.8,
                'target_danceability': 0.9,
                'keywords': ['electronic', 'edm', 'synthetic']
            },
            'jazz': {
                'target_instrumentalness': 0.7,
                'target_acousticness': 0.6,
                'keywords': ['jazz', 'smooth', 'sophisticated']
            },
            'classical': {
                'target_instrumentalness': 0.9,
                'target_acousticness': 0.8,
                'keywords': ['classical', 'orchestral', 'timeless']
            },
            'country': {
                'target_acousticness': 0.7,
                'target_valence': 0.6,
                'keywords': ['country', 'folk', 'authentic']
            },
            'r-n-b': {
                'target_danceability': 0.7,
                'target_valence': 0.6,
                'keywords': ['r&b', 'soul', 'smooth']
            },
            'indie': {
                'target_acousticness': 0.5,
                'target_valence': 0.5,
                'keywords': ['indie', 'alternative', 'underground']
            },
            'alternative': {
                'target_energy': 0.6,
                'target_valence': 0.4,
                'keywords': ['alternative', 'experimental', 'unique']
            }
        }
        
        return genre_contexts.get(genre, {}) 