"""
Custom AI Model for Music Recommendations
"""

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import NMF
from sklearn.preprocessing import StandardScaler
import joblib
import os
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import logging

class MusicAI:
    """Custom AI model for music recommendations"""
    
    def __init__(self, model_dir='app/models/saved'):
        self.model_dir = model_dir
        self.tfidf_vectorizer = None
        self.nmf_model = None
        self.scaler = StandardScaler()
        self.track_features = {}
        self.user_profiles = {}
        self.mood_weights = self._initialize_mood_weights()
        self.genre_weights = self._initialize_genre_weights()
        
        # Ensure model directory exists
        os.makedirs(model_dir, exist_ok=True)
        
        # Load pre-trained models if they exist
        self._load_models()
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _initialize_mood_weights(self) -> Dict[str, Dict[str, float]]:
        """Initialize mood-based feature weights"""
        return {
            'energetic': {
                'energy': 0.9, 'danceability': 0.8, 'valence': 0.7, 'tempo': 0.8,
                'acousticness': -0.3, 'instrumentalness': -0.2
            },
            'chill': {
                'energy': -0.8, 'danceability': -0.6, 'valence': 0.3, 'tempo': -0.7,
                'acousticness': 0.6, 'instrumentalness': 0.5
            },
            'happy': {
                'energy': 0.7, 'danceability': 0.6, 'valence': 0.9, 'tempo': 0.5,
                'acousticness': 0.2, 'instrumentalness': -0.1
            },
            'melancholic': {
                'energy': -0.6, 'danceability': -0.5, 'valence': -0.8, 'tempo': -0.4,
                'acousticness': 0.4, 'instrumentalness': 0.3
            },
            'party': {
                'energy': 0.9, 'danceability': 0.9, 'valence': 0.8, 'tempo': 0.9,
                'acousticness': -0.5, 'instrumentalness': -0.3
            },
            'focused': {
                'energy': -0.4, 'danceability': -0.3, 'valence': 0.2, 'tempo': -0.2,
                'acousticness': 0.3, 'instrumentalness': 0.8
            },
            'romantic': {
                'energy': 0.2, 'danceability': 0.4, 'valence': 0.6, 'tempo': 0.3,
                'acousticness': 0.5, 'instrumentalness': 0.2
            },
            'workout': {
                'energy': 0.9, 'danceability': 0.8, 'valence': 0.7, 'tempo': 0.9,
                'acousticness': -0.4, 'instrumentalness': -0.2
            }
        }
    
    def _initialize_genre_weights(self) -> Dict[str, Dict[str, float]]:
        """Initialize genre-based feature weights"""
        return {
            'pop': {'valence': 0.7, 'danceability': 0.8, 'energy': 0.6},
            'rock': {'energy': 0.8, 'valence': 0.5, 'danceability': 0.4},
            'hip-hop': {'danceability': 0.8, 'energy': 0.7, 'valence': 0.6},
            'electronic': {'energy': 0.8, 'danceability': 0.9, 'valence': 0.6},
            'jazz': {'instrumentalness': 0.7, 'acousticness': 0.6, 'energy': 0.4},
            'classical': {'instrumentalness': 0.9, 'acousticness': 0.8, 'energy': 0.2},
            'country': {'acousticness': 0.7, 'valence': 0.6, 'energy': 0.5},
            'r-n-b': {'danceability': 0.7, 'valence': 0.6, 'energy': 0.5},
            'indie': {'acousticness': 0.5, 'valence': 0.5, 'energy': 0.4},
            'alternative': {'energy': 0.6, 'valence': 0.4, 'danceability': 0.5}
        }
    
    def _load_models(self):
        """Load pre-trained models from disk"""
        try:
            if os.path.exists(f"{self.model_dir}/tfidf_vectorizer.pkl"):
                self.tfidf_vectorizer = joblib.load(f"{self.model_dir}/tfidf_vectorizer.pkl")
                self.logger.info("Loaded TF-IDF vectorizer")
            
            if os.path.exists(f"{self.model_dir}/nmf_model.pkl"):
                self.nmf_model = joblib.load(f"{self.model_dir}/nmf_model.pkl")
                self.logger.info("Loaded NMF model")
                
        except Exception as e:
            self.logger.warning(f"Could not load pre-trained models: {e}")
    
    def _save_models(self):
        """Save trained models to disk"""
        try:
            if self.tfidf_vectorizer:
                joblib.dump(self.tfidf_vectorizer, f"{self.model_dir}/tfidf_vectorizer.pkl")
            
            if self.nmf_model:
                joblib.dump(self.nmf_model, f"{self.model_dir}/nmf_model.pkl")
                
            self.logger.info("Models saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving models: {e}")
    
    def extract_track_features(self, track_data: Dict) -> Dict[str, float]:
        """Extract features from track data"""
        features = {
            'popularity': track_data.get('popularity', 0) / 100.0,
            'duration_ms': track_data.get('duration_ms', 0) / 300000.0,  # Normalize to 5 minutes
            'explicit': 1.0 if track_data.get('explicit', False) else 0.0
        }
        
        # Add audio features if available
        if 'audio_features' in track_data:
            audio = track_data['audio_features']
            features.update({
                'danceability': audio.get('danceability', 0.5),
                'energy': audio.get('energy', 0.5),
                'key': audio.get('key', 0) / 11.0,  # Normalize to 0-1
                'loudness': (audio.get('loudness', -60) + 60) / 60.0,  # Normalize to 0-1
                'mode': audio.get('mode', 1),
                'speechiness': audio.get('speechiness', 0.0),
                'acousticness': audio.get('acousticness', 0.0),
                'instrumentalness': audio.get('instrumentalness', 0.0),
                'liveness': audio.get('liveness', 0.0),
                'valence': audio.get('valence', 0.5),
                'tempo': audio.get('tempo', 120) / 200.0  # Normalize to 0-1
            })
        
        return features
    
    def build_user_profile(self, user_tracks: List[Dict], user_artists: List[Dict]) -> Dict[str, float]:
        """Build user profile from listening history"""
        if not user_tracks and not user_artists:
            return {}
        
        # Extract features from user's tracks
        track_features = []
        for track in user_tracks:
            features = self.extract_track_features(track)
            track_features.append(features)
        
        # Extract genre information from artists
        genres = []
        for artist in user_artists:
            genres.extend(artist.get('genres', []))
        
        # Create user profile
        profile = {}
        
        if track_features:
            # Average track features
            feature_names = track_features[0].keys()
            for feature in feature_names:
                values = [tf[feature] for tf in track_features if feature in tf]
                if values:
                    profile[f'avg_{feature}'] = np.mean(values)
                    profile[f'std_{feature}'] = np.std(values)
        
        # Genre preferences
        if genres:
            genre_counts = {}
            for genre in genres:
                genre_counts[genre] = genre_counts.get(genre, 0) + 1
            
            # Top genres
            top_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            for i, (genre, count) in enumerate(top_genres):
                profile[f'top_genre_{i+1}'] = count / len(genres)
        
        return profile
    
    def train_content_based_model(self, tracks_data: List[Dict]):
        """Train content-based recommendation model"""
        self.logger.info("Training content-based model...")
        
        # Prepare text data for TF-IDF
        text_data = []
        for track in tracks_data:
            # Combine track name, artist names, and genres
            track_text = f"{track.get('name', '')} "
            
            artists = track.get('artists', [])
            for artist in artists:
                track_text += f"{artist.get('name', '')} "
            
            # Add album name
            album = track.get('album', {})
            track_text += f"{album.get('name', '')} "
            
            # Add genres from artists
            for artist in artists:
                if 'genres' in artist:
                    track_text += f"{' '.join(artist['genres'])} "
            
            text_data.append(track_text.strip())
        
        # Train TF-IDF vectorizer
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(text_data)
        
        # Store track features
        for i, track in enumerate(tracks_data):
            self.track_features[track['id']] = {
                'tfidf_vector': tfidf_matrix[i],
                'features': self.extract_track_features(track)
            }
        
        self.logger.info(f"Content-based model trained on {len(tracks_data)} tracks")
        self._save_models()
    
    def train_collaborative_model(self, user_tracks_data: List[Tuple[str, List[Dict]]]):
        """Train collaborative filtering model using NMF"""
        self.logger.info("Training collaborative filtering model...")
        
        # Create user-item matrix
        user_ids = []
        track_ids = set()
        
        # Collect all unique track IDs
        for user_id, tracks in user_tracks_data:
            user_ids.append(user_id)
            for track in tracks:
                track_ids.add(track['id'])
        
        track_ids = list(track_ids)
        user_item_matrix = np.zeros((len(user_ids), len(track_ids)))
        
        # Fill the matrix
        for i, (user_id, tracks) in enumerate(user_tracks_data):
            for track in tracks:
                if track['id'] in track_ids:
                    j = track_ids.index(track['id'])
                    user_item_matrix[i, j] = 1  # Binary interaction
        
        # Train NMF model
        self.nmf_model = NMF(n_components=min(20, min(user_item_matrix.shape)), random_state=42)
        self.nmf_model.fit(user_item_matrix)
        
        self.logger.info(f"Collaborative model trained on {len(user_ids)} users and {len(track_ids)} tracks")
        self._save_models()
    
    def get_content_based_recommendations(self, seed_tracks: List[Dict], n_recommendations: int = 20) -> List[Dict]:
        """Get content-based recommendations"""
        if not self.tfidf_vectorizer or not seed_tracks:
            return []
        
        # Create seed track vector
        seed_text = ""
        for track in seed_tracks:
            seed_text += f"{track.get('name', '')} "
            for artist in track.get('artists', []):
                seed_text += f"{artist.get('name', '')} "
        
        seed_vector = self.tfidf_vectorizer.transform([seed_text])
        
        # Calculate similarities
        similarities = []
        for track_id, track_data in self.track_features.items():
            similarity = cosine_similarity(seed_vector, track_data['tfidf_vector'])[0][0]
            similarities.append((track_id, similarity))
        
        # Sort by similarity and return top recommendations
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Filter out seed tracks
        seed_ids = {track['id'] for track in seed_tracks}
        recommendations = []
        for track_id, similarity in similarities:
            if track_id not in seed_ids and len(recommendations) < n_recommendations:
                recommendations.append({
                    'track_id': track_id,
                    'similarity_score': similarity,
                    'features': self.track_features[track_id]['features']
                })
        
        return recommendations
    
    def get_mood_based_recommendations(self, mood: str, genre: str, available_tracks: List[Dict]) -> List[Dict]:
        """Get mood and genre-based recommendations"""
        if not available_tracks:
            return []
        
        # Get mood and genre weights
        mood_weights = self.mood_weights.get(mood, {})
        genre_weights = self.genre_weights.get(genre, {})
        
        # Calculate scores for each track
        track_scores = []
        for track in available_tracks:
            features = self.extract_track_features(track)
            score = 0.0
            
            # Apply mood weights
            for feature, weight in mood_weights.items():
                if feature in features:
                    score += weight * features[feature]
            
            # Apply genre weights
            for feature, weight in genre_weights.items():
                if feature in features:
                    score += weight * features[feature]
            
            track_scores.append((track, score))
        
        # Sort by score and return top recommendations
        track_scores.sort(key=lambda x: x[1], reverse=True)
        
        return [track for track, score in track_scores[:20]]
    
    def get_hybrid_recommendations(self, user_id: str, seed_tracks: List[Dict], 
                                 mood: str = None, genre: str = None, 
                                 n_recommendations: int = 20) -> List[Dict]:
        """Get hybrid recommendations combining multiple approaches"""
        recommendations = []
        
        # 1. Content-based recommendations
        if seed_tracks:
            content_recs = self.get_content_based_recommendations(seed_tracks, n_recommendations//2)
            recommendations.extend(content_recs)
        
        # 2. Mood/genre-based recommendations
        if mood and genre:
            # Get available tracks (you would need to implement this based on your data)
            available_tracks = self._get_available_tracks()
            mood_recs = self.get_mood_based_recommendations(mood, genre, available_tracks)
            recommendations.extend(mood_recs)
        
        # 3. Collaborative filtering (if user has history)
        if user_id in self.user_profiles:
            collab_recs = self._get_collaborative_recommendations(user_id, n_recommendations//4)
            recommendations.extend(collab_recs)
        
        # Remove duplicates and sort by score
        unique_recs = {}
        for rec in recommendations:
            track_id = rec.get('track_id', rec.get('id'))
            if track_id not in unique_recs:
                unique_recs[track_id] = rec
        
        # Sort by similarity score or other metric
        sorted_recs = sorted(unique_recs.values(), 
                           key=lambda x: x.get('similarity_score', 0), 
                           reverse=True)
        
        return sorted_recs[:n_recommendations]
    
    def _get_available_tracks(self) -> List[Dict]:
        """Get available tracks for recommendations (placeholder)"""
        # This would be implemented based on your data source
        # For now, return tracks from track_features
        return [{'id': track_id, **track_data['features']} 
                for track_id, track_data in self.track_features.items()]
    
    def _get_collaborative_recommendations(self, user_id: str, n_recommendations: int) -> List[Dict]:
        """Get collaborative filtering recommendations"""
        # This would use the NMF model to predict user preferences
        # Placeholder implementation
        return []
    
    def analyze_user_taste(self, user_tracks: List[Dict], user_artists: List[Dict]) -> Dict:
        """Analyze user's music taste using the AI model"""
        if not user_tracks and not user_artists:
            return {'error': 'No user data available'}
        
        # Build user profile
        profile = self.build_user_profile(user_tracks, user_artists)
        
        # Analyze patterns
        analysis = {
            'total_tracks': len(user_tracks),
            'total_artists': len(user_artists),
            'profile': profile
        }
        
        # Genre analysis
        genres = []
        for artist in user_artists:
            genres.extend(artist.get('genres', []))
        
        if genres:
            genre_counts = {}
            for genre in genres:
                genre_counts[genre] = genre_counts.get(genre, 0) + 1
            
            top_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            analysis['top_genres'] = top_genres
            analysis['genre_diversity'] = len(set(genres))
        
        # Feature analysis
        if user_tracks:
            track_features = [self.extract_track_features(track) for track in user_tracks]
            
            # Calculate average features
            feature_analysis = {}
            feature_names = ['energy', 'danceability', 'valence', 'acousticness', 'instrumentalness']
            
            for feature in feature_names:
                values = [tf[feature] for tf in track_features if feature in tf]
                if values:
                    feature_analysis[feature] = {
                        'mean': np.mean(values),
                        'std': np.std(values),
                        'min': np.min(values),
                        'max': np.max(values)
                    }
            
            analysis['feature_analysis'] = feature_analysis
        
        # Generate insights
        analysis['insights'] = self._generate_insights(analysis)
        
        return analysis
    
    def _generate_insights(self, analysis: Dict) -> List[str]:
        """Generate insights from user analysis"""
        insights = []
        
        # Genre insights
        if 'top_genres' in analysis:
            top_genre = analysis['top_genres'][0][0] if analysis['top_genres'] else 'Unknown'
            insights.append(f"Your favorite genre is {top_genre}")
            
            if analysis.get('genre_diversity', 0) > 5:
                insights.append("You have diverse musical tastes across many genres")
            else:
                insights.append("You tend to focus on specific genres")
        
        # Feature insights
        if 'feature_analysis' in analysis:
            fa = analysis['feature_analysis']
            
            if fa.get('energy', {}).get('mean', 0) > 0.7:
                insights.append("You prefer high-energy, upbeat music")
            elif fa.get('energy', {}).get('mean', 0) < 0.3:
                insights.append("You enjoy more relaxed, mellow music")
            
            if fa.get('valence', {}).get('mean', 0) > 0.7:
                insights.append("You tend to listen to positive, happy music")
            elif fa.get('valence', {}).get('mean', 0) < 0.3:
                insights.append("You appreciate more melancholic, emotional music")
            
            if fa.get('instrumentalness', {}).get('mean', 0) > 0.5:
                insights.append("You enjoy instrumental and classical music")
        
        return insights 