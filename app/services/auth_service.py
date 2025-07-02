"""
Authentication service for Spotify OAuth
"""

import time
from flask import session, url_for
from spotipy.oauth2 import SpotifyOAuth
from config.settings import Config

class AuthService:
    """Handles Spotify OAuth authentication"""
    
    def __init__(self):
        self.oauth = None
    
    def _get_oauth(self):
        """Get or create SpotifyOAuth instance"""
        if not self.oauth:
            self.oauth = SpotifyOAuth(
                client_id=Config.SPOTIFY_CLIENT_ID,
                client_secret=Config.SPOTIFY_CLIENT_SECRET,
                redirect_uri=Config.SPOTIFY_REDIRECT_URI,
                scope=Config.get_spotify_scopes(),
                cache_handler=None  # We'll handle caching manually
            )
        return self.oauth
    
    def get_auth_url(self):
        """Get Spotify OAuth URL"""
        oauth = self._get_oauth()
        return oauth.get_authorize_url()
    
    def handle_callback(self, code):
        """Handle OAuth callback"""
        try:
            oauth = self._get_oauth()
            token_info = oauth.get_access_token(code)
            
            if token_info:
                session['token_info'] = token_info
                session['expires_at'] = int(time.time()) + token_info['expires_in']
                return True
        except Exception as e:
            print(f"OAuth callback error: {e}")
        
        return False
    
    def is_authenticated(self):
        """Check if user is authenticated"""
        if 'token_info' not in session:
            return False
        
        # Check if token is expired
        if 'expires_at' in session:
            if int(time.time()) > session['expires_at']:
                # Token expired, try to refresh
                return self._refresh_token()
        
        return True
    
    def _refresh_token(self):
        """Refresh access token"""
        try:
            oauth = self._get_oauth()
            token_info = oauth.refresh_access_token(
                session['token_info']['refresh_token']
            )
            
            if token_info:
                session['token_info'] = token_info
                session['expires_at'] = int(time.time()) + token_info['expires_in']
                return True
        except Exception as e:
            print(f"Token refresh error: {e}")
        
        return False
    
    def get_access_token(self):
        """Get current access token"""
        if self.is_authenticated():
            return session['token_info']['access_token']
        return None
    
    def logout(self):
        """Clear session data"""
        session.clear() 