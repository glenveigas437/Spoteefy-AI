"""
Spotify API service
"""

from spotipy import Spotify
from app.services.auth_service import AuthService
from app.constants import (
    DEFAULT_LIMIT, MAX_LIMIT, ARTIST_TOP_TRACKS_LIMIT, SIMILAR_ARTISTS_LIMIT,
    DEFAULT_TIME_RANGE, SPOTIFY, DISPLAY_LIMITS
)
import requests

class SpotifyService:
    """Handles Spotify API interactions"""
    
    def __init__(self):
        self.auth_service = AuthService()
        self.client = None
    
    def _get_client(self):
        """Get or create Spotify client"""
        if not self.client:
            token = self.auth_service.get_access_token()
            if token:
                self.client = Spotify(auth=token)
        return self.client
    
    def get_user_profile(self):
        """Get current user profile"""
        client = self._get_client()
        if client:
            return client.current_user()
        return None
    
    def get_recent_tracks(self, limit=DEFAULT_LIMIT):
        """Get user's recently played tracks"""
        client = self._get_client()
        if client:
            return client.current_user_recently_played(limit=limit)
        return []
    
    def get_top_artists(self, limit=DEFAULT_LIMIT, time_range=DEFAULT_TIME_RANGE):
        """Get user's top artists"""
        client = self._get_client()
        if client:
            return client.current_user_top_artists(limit=limit, time_range=time_range)
        return []
    
    def get_top_tracks(self, limit=DEFAULT_LIMIT, time_range=DEFAULT_TIME_RANGE):
        """Get user's top tracks"""
        client = self._get_client()
        if client:
            return client.current_user_top_tracks(limit=limit, time_range=time_range)
        return []
    
    def get_user_playlists(self, limit=MAX_LIMIT):
        """Get user's playlists"""
        client = self._get_client()
        if client:
            return client.current_user_playlists(limit=limit)
        return []
    
    def get_saved_tracks(self, limit=MAX_LIMIT):
        """Get user's saved tracks"""
        client = self._get_client()
        if client:
            return client.current_user_saved_tracks(limit=limit)
        return []
    
    def get_playlist_tracks(self, playlist_id):
        """Get tracks from a playlist"""
        client = self._get_client()
        if client:
            return client.playlist_tracks(playlist_id)
        return []
    
    def create_playlist(self, name, description="", public=True):
        """Create a new playlist"""
        client = self._get_client()
        if client:
            user_id = client.current_user()['id']
            return client.user_playlist_create(
                user=user_id,
                name=name,
                description=description,
                public=public
            )
        return None
    
    def add_tracks_to_playlist(self, playlist_id, track_uris):
        """Add tracks to a playlist"""
        client = self._get_client()
        if client:
            return client.playlist_add_items(playlist_id, track_uris)
        return None
    
    def get_music_analysis(self):
        """Get comprehensive music analysis"""
        client = self._get_client()
        if not client:
            return {}
        
        # Get top tracks and artists
        top_tracks = self.get_top_tracks(limit=DISPLAY_LIMITS["ANALYZE_TOP_TRACKS"])
        top_artists = self.get_top_artists(limit=DISPLAY_LIMITS["ANALYZE_TOP_ARTISTS"])
        
        # Analyze features without audio features (deprecated)
        analysis = {
            'top_tracks': top_tracks,
            'top_artists': top_artists,
            'stats': self._calculate_basic_stats(top_tracks, top_artists)
        }
        
        return analysis
    
    def _calculate_basic_stats(self, top_tracks, top_artists):
        """Calculate basic statistics without audio features"""
        stats = {
            'top_tracks_count': len(top_tracks.get('items', [])),
            'top_artists_count': len(top_artists.get('items', [])),
            'genre_distribution': {}
        }
        
        # Calculate genre distribution from top artists
        genres = {}
        for artist in top_artists.get('items', []):
            for genre in artist.get('genres', []):
                genres[genre] = genres.get(genre, 0) + 1
        
        stats['genre_distribution'] = dict(sorted(genres.items(), key=lambda x: x[1], reverse=True)[:DISPLAY_LIMITS["GENRE_DISTRIBUTION"]])
        
        return stats
    
    def get_user_stats(self):
        """Get user listening statistics"""
        client = self._get_client()
        if not client:
            return {}
        
        top_tracks = self.get_top_tracks(limit=MAX_LIMIT)
        top_artists = self.get_top_artists(limit=MAX_LIMIT)
        
        # Calculate genre distribution
        genres = {}
        for artist in top_artists.get('items', []):
            for genre in artist.get('genres', []):
                genres[genre] = genres.get(genre, 0) + 1
        
        return {
            'top_tracks_count': len(top_tracks.get('items', [])),
            'top_artists_count': len(top_artists.get('items', [])),
            'genre_distribution': dict(sorted(genres.items(), key=lambda x: x[1], reverse=True)[:DISPLAY_LIMITS["GENRE_DISTRIBUTION"]])
        }
    
    def get_similar_artists_by_genre(self, artist_ids, limit=SIMILAR_ARTISTS_LIMIT):
        """Get similar artists by searching for artists with similar genres"""
        client = self._get_client()
        similar_artists = []
        if client:
            for artist_id in artist_ids[:limit]:
                try:
                    # Get the artist's genres
                    artist = client.artist(artist_id)
                    genres = artist.get('genres', [])
                    
                    if genres:
                        # Search for artists with similar genres
                        genre_query = ' OR '.join(genres[:2])  # Use top 2 genres
                        search_results = client.search(q=f'genre:{genre_query}', type='artist', limit=DISPLAY_LIMITS["SEARCH_RESULTS"])
                        similar_artists.extend(search_results.get('artists', {}).get('items', []))
                except Exception:
                    continue
        return similar_artists
    
    def get_artists_top_tracks(self, artist_ids, market=SPOTIFY["DEFAULT_MARKET"], limit=ARTIST_TOP_TRACKS_LIMIT):
        client = self._get_client()
        tracks = []
        if client:
            for artist_id in artist_ids:
                try:
                    top_tracks = client.artist_top_tracks(artist_id, country=market)['tracks'][:limit]
                    tracks += top_tracks
                except Exception:
                    continue
        return tracks
    
    def search_tracks(self, query, limit=DISPLAY_LIMITS["SEARCH_RESULTS"]):
        """Search for tracks"""
        client = self._get_client()
        if client:
            try:
                results = client.search(q=query, type='track', limit=limit)
                return results.get('tracks', {}).get('items', [])
            except Exception as e:
                print(f"Track search error: {e}")
                return []
        return []

    def search_artists(self, query, limit=DISPLAY_LIMITS["SEARCH_RESULTS"]):
        """Search for artists"""
        client = self._get_client()
        if client:
            try:
                results = client.search(q=query, type='artist', limit=limit)
                return results.get('artists', {}).get('items', [])
            except Exception as e:
                print(f"Artist search error: {e}")
                return []
        return []

    def get_artist_top_tracks(self, artist_id, market=SPOTIFY["DEFAULT_MARKET"]):
        """Get top tracks for a specific artist"""
        client = self._get_client()
        if client:
            try:
                return client.artist_top_tracks(artist_id, country=market)['tracks']
            except Exception as e:
                print(f"Artist top tracks error: {e}")
                return []
        return []

    def get_track(self, track_id):
        """Get full track info by Spotify track ID using the authenticated client"""
        client = self._get_client()
        if client:
            try:
                return client.track(track_id)
            except Exception as e:
                print(f"Error fetching track info for {track_id}: {e}")
        return None

def get_spotify_album_image(track_id, access_token):
    url = f'https://api.spotify.com/v1/tracks/{track_id}'
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.get(url, headers=headers, timeout=3)
        if response.status_code == 200:
            data = response.json()
            images = data.get('album', {}).get('images', [])
            if images:
                return images[0]['url']  # Largest image
    except Exception as e:
        print(f"Error fetching album image for {track_id}: {e}")
    return '/static/default-album.png' 