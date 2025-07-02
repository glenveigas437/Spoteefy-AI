"""
API routes for AJAX endpoints
"""

from flask import Blueprint, request, jsonify
from app.services.spotify_service import SpotifyService, get_spotify_album_image
from app.services.ai_client_service import AIClientService
from app.services.auth_service import AuthService
from app.constants import (
    DEFAULT_MOOD, DEFAULT_GENRE, DEFAULT_LANGUAGE, DEFAULT_LIMIT, SEARCH_LIMIT,
    ARTIST_TOP_TRACKS_LIMIT, SIMILAR_ARTISTS_LIMIT, RECOMMENDATIONS_LIMIT,
    MOOD_KEYWORDS, MOOD_GENRE_QUERIES, LANGUAGE_FILTERS, MESSAGES, HTTP_STATUS,
    DISPLAY_LIMITS, SPOTIFY
)
import os
import requests

bp = Blueprint('api', __name__, url_prefix='/api')
spotify_service = SpotifyService()
ai_client = AIClientService()
auth_service = AuthService()

SPOTIFY_ACCESS_TOKEN = os.environ.get('SPOTIFY_ACCESS_TOKEN')

@bp.route('/recommendations')
def recommendations():
    """Get track recommendations"""
    if not auth_service.is_authenticated():
        return jsonify({'error': MESSAGES["NOT_AUTHENTICATED"]}), HTTP_STATUS["UNAUTHORIZED"]
    
    seed_tracks = request.args.get('seed_tracks', '').split(',')
    limit = int(request.args.get('limit', DEFAULT_LIMIT))
    
    recommendations = spotify_service.get_recommendations(seed_tracks, limit)
    
    return jsonify(recommendations)

@bp.route('/create-playlist', methods=['POST'])
def create_playlist():
    """Create AI-generated playlist using treble-clef microservice"""
    if not auth_service.is_authenticated():
        return jsonify({'error': MESSAGES["NOT_AUTHENTICATED"]}), HTTP_STATUS["UNAUTHORIZED"]
    
    data = request.get_json()
    theme = data.get('theme', 'Chill Vibes')
    tracks_count = data.get('tracks_count', DEFAULT_LIMIT)
    
    # Call treble-clef microservice for playlist concept
    playlist_concept = ai_client.generate_playlist_concept(
        theme=theme,
        mood='chill',  # Default mood
        genre='pop',   # Default genre
        duration=tracks_count * 3  # Rough estimate: 3 minutes per track
    )
    
    return jsonify(playlist_concept)

@bp.route('/user-stats')
def user_stats():
    """Get user listening statistics"""
    if not auth_service.is_authenticated():
        return jsonify({'error': MESSAGES["NOT_AUTHENTICATED"]}), HTTP_STATUS["UNAUTHORIZED"]
    
    stats = spotify_service.get_user_stats()
    
    return jsonify(stats)

@bp.route('/search-tracks')
def search_tracks():
    """Search for tracks"""
    if not auth_service.is_authenticated():
        return jsonify({'error': MESSAGES["NOT_AUTHENTICATED"]}), HTTP_STATUS["UNAUTHORIZED"]
    
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', SEARCH_LIMIT))
    language = request.args.get('language', DEFAULT_LANGUAGE)
    
    if not query:
        return jsonify({'error': 'Query parameter required'}), HTTP_STATUS["BAD_REQUEST"]
    
    # Add language filter to search query
    language_filter = get_language_filter(language)
    if language_filter:
        query = f"{query} {language_filter}"
    
    tracks = spotify_service.search_tracks(query, limit)
    return jsonify({'success': True, 'tracks': tracks})

@bp.route('/search-artists')
def search_artists():
    """Search for artists"""
    if not auth_service.is_authenticated():
        return jsonify({'error': MESSAGES["NOT_AUTHENTICATED"]}), HTTP_STATUS["UNAUTHORIZED"]
    
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', SEARCH_LIMIT))
    language = request.args.get('language', DEFAULT_LANGUAGE)
    
    if not query:
        return jsonify({'error': 'Query parameter required'}), HTTP_STATUS["BAD_REQUEST"]
    
    # Add language filter to search query
    language_filter = get_language_filter(language)
    if language_filter:
        query = f"{query} {language_filter}"
    
    artists = spotify_service.search_artists(query, limit)
    return jsonify({'success': True, 'artists': artists})

@bp.route('/discover')
def discover():
    """AI-powered music discovery using treble-clef microservice"""
    if not auth_service.is_authenticated():
        return jsonify({'error': MESSAGES["NOT_AUTHENTICATED"]}), HTTP_STATUS["UNAUTHORIZED"]

    mood = request.args.get('mood', DEFAULT_MOOD)
    genre = request.args.get('genre', DEFAULT_GENRE)
    language = request.args.get('language', DEFAULT_LANGUAGE)
    search_seeds = request.args.get('seeds', '').split(',')
    seed_artists = []
    seed_tracks = []
    
    for seed in search_seeds:
        if seed.startswith('track:'):
            track_id = seed.split(':', 1)[1]
            track_info = spotify_service.get_track(track_id)
            if track_info:
                for artist in track_info.get('artists', []):
                    seed_artists.append(artist['name'])
                seed_tracks.append(track_info.get('name', ''))
    # Remove duplicates
    seed_artists = list(set(seed_artists))
    seed_tracks = list(set(seed_tracks))

    # Get user's top artists and tracks for AI discovery (fallback if no seeds)
    if not seed_artists:
        top_artists = spotify_service.get_top_artists(limit=ARTIST_TOP_TRACKS_LIMIT)
        artist_names = [artist['name'] for artist in top_artists.get('items', [])]
        seed_artists = artist_names
    if not seed_tracks:
        top_tracks = spotify_service.get_top_tracks(limit=RECOMMENDATIONS_LIMIT)
        track_names = [track['name'] for track in top_tracks.get('items', [])]
        seed_tracks = track_names

    # Use treble-clef microservice for AI-powered discovery
    ai_discoveries = ai_client.discover_music(
        seed_artists=seed_artists,
        seed_tracks=seed_tracks,
        mood=mood,
        genre=genre,
        language=language,
        limit=DISPLAY_LIMITS['DISCOVER_RECOMMENDATIONS']
    )
    
    # If AI service fails, fallback to Spotify-based discovery
    if not ai_discoveries.get('success', False):
        # Fallback to original Spotify-based logic
        all_tracks = []
        
        if not artist_names and not track_names:
            print("No user data found, using popular tracks fallback")
            popular_tracks = get_popular_tracks_by_mood(mood, genre, language)
            return jsonify({
                'success': True,
                'recommendations': popular_tracks,
                'no_user_data': True,
                'message': MESSAGES["POPULAR_TRACKS_FALLBACK"]
            })
        
        # Get similar artists and their tracks
        artist_ids = [artist['id'] for artist in top_artists.get('items', [])]
        similar_artists = spotify_service.get_similar_artists_by_genre(artist_ids, limit=SIMILAR_ARTISTS_LIMIT)
        similar_artist_ids = [artist['id'] for artist in similar_artists]
        candidate_tracks = spotify_service.get_artists_top_tracks(similar_artist_ids, limit=ARTIST_TOP_TRACKS_LIMIT)
        all_tracks = candidate_tracks + top_tracks.get('items', [])
        
        # Mood filtering
        if mood in MOOD_KEYWORDS:
            mood_tracks = []
            for keyword in MOOD_KEYWORDS[mood][:2]:
                language_filter = get_language_filter(language)
                search_query = keyword
                if language_filter:
                    search_query = f"{keyword} {language_filter}"
                search_results = spotify_service.search_tracks(search_query, limit=5)
                mood_tracks.extend(search_results)
            all_tracks = mood_tracks + all_tracks
        
        return jsonify({
            'success': True,
            'recommendations': all_tracks[:DISPLAY_LIMITS['DISCOVER_RECOMMENDATIONS']],
            'fallback': True
        })
    
    
    recommendations = []
    if ai_discoveries and isinstance(ai_discoveries['discoveries'], list):
        for track_id in ai_discoveries['discoveries']:
            track_info = spotify_service.get_track(track_id)
            if track_info:
                recommendations.append(track_info)
    
    return jsonify({
        'success': True,
        'recommendations': recommendations,
        'count': len(recommendations),
        'ai_generated': True
    })

def get_language_filter(language):
    return LANGUAGE_FILTERS.get(language, '')

def get_popular_tracks_by_mood(mood, genre, language=DEFAULT_LANGUAGE):
    """Get popular tracks based on mood, genre, and language as a fallback"""
    # Get queries for the mood and genre
    queries = MOOD_GENRE_QUERIES.get(mood, {}).get(genre, [f'{mood} {genre}'])
    
    # Add language filter
    language_filter = get_language_filter(language)
    
    popular_tracks = []
    for query in queries[:2]:  # Use first 2 queries
        try:
            # Add language filter to query
            if language_filter:
                query = f"{query} {language_filter}"
            tracks = spotify_service.search_tracks(query, limit=SEARCH_LIMIT)
            popular_tracks.extend(tracks)
        except Exception as e:
            print(f"Error searching for '{query}': {e}")
            continue
    
    # If still no tracks, use a generic search with language filter
    if not popular_tracks:
        try:
            generic_query = 'popular music'
            if language_filter:
                generic_query = f"{generic_query} {language_filter}"
            popular_tracks = spotify_service.search_tracks(generic_query, limit=DEFAULT_LIMIT)
        except Exception as e:
            print(f"Error with generic search: {e}")
            return []
    
    return popular_tracks[:DISPLAY_LIMITS['DISCOVER_RECOMMENDATIONS']] 