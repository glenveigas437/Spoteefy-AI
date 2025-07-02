"""
Utility functions for templates and general use
"""

from app.constants import Mood, Genre, Language, TimeRange

def get_mood_options():
    """Get mood options for templates"""
    return [(mood.value, mood.value.title()) for mood in Mood]

def get_genre_options():
    """Get genre options for templates"""
    return [(genre.value, genre.value.title()) for genre in Genre]

def get_language_options():
    """Get language options for templates"""
    return [(lang.value, lang.value.title()) for lang in Language]

def get_time_range_options():
    """Get time range options for templates"""
    return [(tr.value, tr.value.replace('_', ' ').title()) for tr in TimeRange]

def format_duration(ms):
    """Format duration from milliseconds to MM:SS"""
    if not ms:
        return "0:00"
    
    seconds = int(ms / 1000)
    minutes = int(seconds / 60)
    seconds = seconds % 60
    return f"{minutes}:{seconds:02d}"

def truncate_text(text, max_length=50):
    """Truncate text to specified length"""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def get_artist_names(artists):
    """Get formatted artist names from artist list"""
    if not artists:
        return "Unknown Artist"
    return ", ".join([artist.get('name', 'Unknown') for artist in artists])

def get_album_image_url(album, size='medium'):
    """Get album image URL with specified size"""
    if not album or not album.get('images'):
        return None
    
    images = album['images']
    if size == 'small' and len(images) >= 2:
        return images[-1]['url']
    elif size == 'large' and len(images) >= 1:
        return images[0]['url']
    else:
        # Return medium size (middle image)
        return images[len(images)//2]['url'] if images else None 