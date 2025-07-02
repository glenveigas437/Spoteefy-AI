"""
Custom AI service for music recommendations and analysis
"""

from app.services.spotify_service import SpotifyService
from app.models.ai_model import MusicAI
from app.models.data_processor import SpotifyDataProcessor
from config.settings import Config
from app.constants import DEFAULT_LIMIT, MESSAGES
import logging

class AIService:
    """Handles AI-powered music features using custom model"""
    
    def __init__(self):
        self.spotify_service = SpotifyService()
        self.ai_model = MusicAI()
        self.data_processor = SpotifyDataProcessor()
        self.logger = logging.getLogger(__name__)
    
    def create_ai_playlist(self, theme, tracks_count=DEFAULT_LIMIT):
        """Create an AI-generated playlist based on theme"""
        try:
            # Get user's current listening data for context
            user_tracks = self.spotify_service.get_top_tracks(limit=10)
            user_artists = self.spotify_service.get_top_artists(limit=10)
            
            # Create recommendation context
            context = self.data_processor.create_recommendation_context(
                user_tracks.get('items', []),
                mood=theme.lower(),
                genre='pop'  # Default genre, could be made configurable
            )
            
            # Get AI recommendations
            recommendations = self.ai_model.get_hybrid_recommendations(
                user_id='current_user',
                seed_tracks=user_tracks.get('items', [])[:5],
                mood=theme.lower(),
                genre='pop',
                n_recommendations=tracks_count
            )
            
            if recommendations:
                # Create playlist
                playlist_name = f"AI Generated: {theme}"
                playlist_desc = f"AI-generated playlist based on theme: {theme}"
                
                playlist = self.spotify_service.create_playlist(
                    name=playlist_name,
                    description=playlist_desc
                )
                
                if playlist:
                    # Add tracks to playlist
                    track_uris = [f"spotify:track:{rec['track_id']}" for rec in recommendations]
                    self.spotify_service.add_tracks_to_playlist(playlist['id'], track_uris)
                    
                    return {
                        'success': True,
                        'playlist': playlist,
                        'recommendations': recommendations,
                        'ai_generated': True
                    }
            
            # Fallback to search-based approach
            return self._fallback_playlist_creation(theme, tracks_count)
            
        except Exception as e:
            self.logger.error(f"AI playlist creation error: {e}")
            return self._fallback_playlist_creation(theme, tracks_count)
    
    def _fallback_playlist_creation(self, theme, tracks_count):
        """Fallback playlist creation using search"""
        try:
            # Use search-based approach
            search_query = f"{theme} music"
            tracks = self.spotify_service.search_tracks(search_query, limit=tracks_count)
            
            if tracks:
                # Create playlist
                playlist_name = f"AI Generated: {theme}"
                playlist_desc = f"AI-generated playlist based on theme: {theme}"
                
                playlist = self.spotify_service.create_playlist(
                    name=playlist_name,
                    description=playlist_desc
                )
                
                if playlist:
                    # Add tracks to playlist
                    track_uris = [f"spotify:track:{track['id']}" for track in tracks]
                    self.spotify_service.add_tracks_to_playlist(playlist['id'], track_uris)
                    
                    return {
                        'success': True,
                        'playlist': playlist,
                        'tracks': tracks,
                        'ai_generated': False
                    }
            
            return {'success': False, 'error': 'Failed to create playlist'}
            
        except Exception as e:
            self.logger.error(f"Fallback playlist creation error: {e}")
            return {'success': False, 'error': str(e)}
    
    def analyze_music_taste(self, user_data):
        """Analyze user's music taste using custom AI model"""
        try:
            # Extract user data
            top_tracks = user_data.get('top_tracks', {}).get('items', [])
            top_artists = user_data.get('top_artists', {}).get('items', [])
            
            if not top_tracks and not top_artists:
                return self._basic_analysis(user_data)
            
            # Use custom AI model for analysis
            analysis = self.ai_model.analyze_user_taste(top_tracks, top_artists)
            
            # Format the analysis for display
            formatted_analysis = self._format_ai_analysis(analysis)
            
            return {
                'success': True,
                'analysis': formatted_analysis,
                'ai_generated': True,
                'raw_analysis': analysis
            }
            
        except Exception as e:
            self.logger.error(f"AI analysis error: {e}")
            return self._basic_analysis(user_data)
    
    def _format_ai_analysis(self, analysis):
        """Format AI analysis for display"""
        if 'error' in analysis:
            return analysis['error']
        
        formatted = "🎵 **Your Music Taste Analysis**\n\n"
        
        # Basic stats
        formatted += f"📊 **Listening Stats:**\n"
        formatted += f"• Total tracks analyzed: {analysis.get('total_tracks', 0)}\n"
        formatted += f"• Total artists followed: {analysis.get('total_artists', 0)}\n"
        formatted += f"• Genre diversity: {analysis.get('genre_diversity', 0)} genres\n\n"
        
        # Top genres
        if 'top_genres' in analysis and analysis['top_genres']:
            formatted += f"🎭 **Top Genres:**\n"
            for i, (genre, count) in enumerate(analysis['top_genres'][:5], 1):
                percentage = (count / analysis.get('total_artists', 1)) * 100
                formatted += f"{i}. {genre.title()} ({percentage:.1f}%)\n"
            formatted += "\n"
        
        # Feature analysis
        if 'feature_analysis' in analysis:
            fa = analysis['feature_analysis']
            formatted += f"🎼 **Musical Characteristics:**\n"
            
            if 'energy' in fa:
                energy_level = "High" if fa['energy']['mean'] > 0.7 else "Medium" if fa['energy']['mean'] > 0.4 else "Low"
                formatted += f"• Energy level: {energy_level} ({fa['energy']['mean']:.2f})\n"
            
            if 'valence' in fa:
                mood = "Positive" if fa['valence']['mean'] > 0.6 else "Neutral" if fa['valence']['mean'] > 0.4 else "Melancholic"
                formatted += f"• Overall mood: {mood} ({fa['valence']['mean']:.2f})\n"
            
            if 'danceability' in fa:
                dance_level = "High" if fa['danceability']['mean'] > 0.7 else "Medium" if fa['danceability']['mean'] > 0.4 else "Low"
                formatted += f"• Danceability: {dance_level} ({fa['danceability']['mean']:.2f})\n"
            
            if 'acousticness' in fa:
                acoustic_level = "High" if fa['acousticness']['mean'] > 0.6 else "Medium" if fa['acousticness']['mean'] > 0.3 else "Low"
                formatted += f"• Acoustic preference: {acoustic_level} ({fa['acousticness']['mean']:.2f})\n"
            
            formatted += "\n"
        
        # AI insights
        if 'insights' in analysis and analysis['insights']:
            formatted += f"🧠 **AI Insights:**\n"
            for insight in analysis['insights']:
                formatted += f"• {insight}\n"
            formatted += "\n"
        
        # Recommendations
        formatted += f"💡 **Recommendations:**\n"
        formatted += f"• Try exploring new genres to expand your musical horizons\n"
        formatted += f"• Check out similar artists to your favorites\n"
        formatted += f"• Experiment with different moods and energy levels\n"
        
        return formatted
    
    def _basic_analysis(self, user_data):
        """Basic analysis without AI"""
        top_tracks = user_data.get('top_tracks', {}).get('items', [])
        top_artists = user_data.get('top_artists', {}).get('items', [])
        
        # Simple analysis
        genres = []
        for artist in top_artists:
            genres.extend(artist.get('genres', []))
        
        unique_genres = list(set(genres))
        
        analysis = f"""
        Based on your listening data:
        
        • You have {len(top_tracks)} favorite tracks
        • You follow {len(top_artists)} top artists
        • You enjoy {len(unique_genres)} different genres
        • Top genres: {', '.join(unique_genres[:5])}
        
        Your music taste shows diversity across genres, suggesting an open-minded approach to music discovery.
        """
        
        return {
            'success': True,
            'analysis': analysis,
            'ai_generated': False
        }
    
    def get_smart_recommendations(self, user_id, mood=None, genre=None, limit=DEFAULT_LIMIT):
        """Get smart recommendations using the custom AI model"""
        try:
            # Get user's listening data
            user_tracks = self.spotify_service.get_top_tracks(limit=20)
            user_artists = self.spotify_service.get_top_artists(limit=20)
            
            # Get AI recommendations
            recommendations = self.ai_model.get_hybrid_recommendations(
                user_id=user_id,
                seed_tracks=user_tracks.get('items', [])[:5],
                mood=mood,
                genre=genre,
                n_recommendations=limit
            )
            
            return {
                'success': True,
                'recommendations': recommendations,
                'ai_generated': True
            }
            
        except Exception as e:
            self.logger.error(f"Smart recommendations error: {e}")
            return {
                'success': False,
                'error': str(e),
                'ai_generated': False
            }
    
    def train_model(self, users_data):
        """Train the AI model with user data"""
        try:
            self.logger.info("Starting model training...")
            
            # Process training data
            training_data = []
            for user_id, user_data in users_data:
                processed = self.data_processor.process_user_data(
                    user_data.get('tracks', []),
                    user_data.get('artists', [])
                )
                training_data.append((user_id, processed))
            
            # Train content-based model
            all_tracks = []
            for user_id, processed in training_data:
                all_tracks.extend(processed['tracks'])
            
            if all_tracks:
                self.ai_model.train_content_based_model(all_tracks)
            
            # Train collaborative filtering model
            user_tracks_data = []
            for user_id, processed in training_data:
                user_tracks_data.append((user_id, processed['tracks']))
            
            if user_tracks_data:
                self.ai_model.train_collaborative_model(user_tracks_data)
            
            self.logger.info("Model training completed successfully")
            return {'success': True, 'message': 'Model trained successfully'}
            
        except Exception as e:
            self.logger.error(f"Model training error: {e}")
            return {'success': False, 'error': str(e)} 