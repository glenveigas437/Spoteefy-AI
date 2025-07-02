"""
Main routes for the application
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services.spotify_service import SpotifyService
from app.services.ai_client_service import AIClientService
from app.services.auth_service import AuthService
from app.constants import (
    DISPLAY_LIMITS, DEFAULT_TIME_RANGE, MESSAGES, HTTP_STATUS
)

bp = Blueprint('main', __name__)
spotify_service = SpotifyService()
ai_client = AIClientService()
auth_service = AuthService()

@bp.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@bp.route('/dashboard')
def dashboard():
    """User dashboard"""
    if not auth_service.is_authenticated():
        return redirect(url_for('auth.login'))
    
    try:
        # Get user profile
        user = spotify_service.get_user_profile()
        
        # Get recent tracks and top artists
        recent_tracks = spotify_service.get_recent_tracks(limit=DISPLAY_LIMITS["DASHBOARD_RECENT_TRACKS"])
        top_artists = spotify_service.get_top_artists(limit=DISPLAY_LIMITS["DASHBOARD_TOP_ARTISTS"], time_range=DEFAULT_TIME_RANGE)
        
        return render_template('dashboard.html', 
                             user=user, 
                             recent_tracks=recent_tracks,
                             top_artists=top_artists)
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return render_template('dashboard.html', 
                             user=None, 
                             recent_tracks={'items': []},
                             top_artists={'items': []})

@bp.route('/discover')
def discover():
    """Music discovery page"""
    if not auth_service.is_authenticated():
        return redirect(url_for('auth.login'))
    
    return render_template('discover.html')

@bp.route('/analyze')
def analyze():
    """Music analysis page"""
    if not auth_service.is_authenticated():
        return redirect(url_for('auth.login'))
    
    try:
        # Get comprehensive music analysis
        analysis = spotify_service.get_music_analysis()
        
        # Get user's top artists and tracks for AI analysis
        top_artists = spotify_service.get_top_artists(limit=10)
        top_tracks = spotify_service.get_top_tracks(limit=10)
        recent_tracks = spotify_service.get_recent_tracks(limit=10)
        
        # Extract names for AI analysis
        artist_names = [artist['name'] for artist in top_artists.get('items', [])]
        track_names = [track['name'] for track in top_tracks.get('items', [])]
        recent_track_names = [track['track']['name'] for track in recent_tracks.get('items', [])]
        
        # Get AI analysis from treble-clef microservice
        ai_analysis = ai_client.analyze_music_taste(
            top_artists=artist_names,
            top_tracks=track_names,
            recent_tracks=recent_track_names
        )
        
        return render_template('analyze.html', 
                             analysis=analysis,
                             ai_analysis=ai_analysis)
    except Exception as e:
        flash(f'Error loading analysis: {str(e)}', 'error')
        return render_template('analyze.html', 
                             analysis={},
                             ai_analysis={'success': False, 'analysis': MESSAGES["NO_USER_DATA"]})

@bp.route('/playlists')
def playlists():
    """Playlists management page"""
    if not auth_service.is_authenticated():
        return redirect(url_for('auth.login'))
    
    try:
        # Get user's playlists
        playlists = spotify_service.get_user_playlists()
        
        return render_template('playlists.html', playlists=playlists)
    except Exception as e:
        flash(f'Error loading playlists: {str(e)}', 'error')
        return render_template('playlists.html', playlists={'items': []}) 