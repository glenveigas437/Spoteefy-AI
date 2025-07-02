"""
Constants and enums for the Spotify AI application
"""

from enum import Enum

class Mood(Enum):
    """Available moods for music discovery"""
    ENERGETIC = "energetic"
    CHILL = "chill"
    HAPPY = "happy"
    MELANCHOLIC = "melancholic"
    PARTY = "party"
    FOCUSED = "focused"
    ROMANTIC = "romantic"
    WORKOUT = "workout"

class Genre(Enum):
    """Available genres for music discovery"""
    POP = "pop"
    ROCK = "rock"
    HIP_HOP = "hip_hop"
    ELECTRONIC = "electronic"
    JAZZ = "jazz"
    CLASSICAL = "classical"
    COUNTRY = "country"
    RNB = "rnb"
    INDIE = "indie"
    FOLK = "folk"
    METAL = "metal"
    BLUES = "blues"
    REGGAE = "reggae"
    LATIN = "latin"
    KPOP = "kpop"
    BOLLYWOOD = "bollywood"

class Language(Enum):
    """Available languages for music filtering"""
    ENGLISH = "english"
    SPANISH = "spanish"
    FRENCH = "french"
    GERMAN = "german"
    ITALIAN = "italian"
    PORTUGUESE = "portuguese"
    HINDI = "hindi"
    KOREAN = "korean"
    JAPANESE = "japanese"
    CHINESE = "chinese"

class TimeRange(Enum):
    """Spotify API time ranges"""
    SHORT_TERM = "short_term"  # Last 4 weeks
    MEDIUM_TERM = "medium_term"  # Last 6 months
    LONG_TERM = "long_term"  # Several years

# Default values
DEFAULT_MOOD = Mood.ENERGETIC.value
DEFAULT_GENRE = Genre.POP.value
DEFAULT_LANGUAGE = Language.ENGLISH.value
DEFAULT_TIME_RANGE = TimeRange.MEDIUM_TERM.value

# API limits
DEFAULT_LIMIT = 20
MAX_LIMIT = 50
SEARCH_LIMIT = 10
ARTIST_TOP_TRACKS_LIMIT = 5
SIMILAR_ARTISTS_LIMIT = 5
RECOMMENDATIONS_LIMIT = 20

# Mood to keyword mappings
MOOD_KEYWORDS = {
    Mood.ENERGETIC.value: ["energetic", "upbeat", "fast"],
    Mood.CHILL.value: ["chill", "relaxing", "ambient"],
    Mood.HAPPY.value: ["happy", "positive", "uplifting"],
    Mood.MELANCHOLIC.value: ["melancholic", "sad", "emotional"],
    Mood.PARTY.value: ["party", "dance", "club"],
    Mood.FOCUSED.value: ["focus", "study", "instrumental"],
    Mood.ROMANTIC.value: ["romantic", "love", "intimate"],
    Mood.WORKOUT.value: ["workout", "gym", "motivation"]
}

# Mood and genre specific search queries
MOOD_GENRE_QUERIES = {
    Mood.ENERGETIC.value: {
        Genre.POP.value: ["pop hits", "top 40"],
        Genre.ROCK.value: ["rock hits", "classic rock"],
        Genre.HIP_HOP.value: ["hip hop hits", "rap hits"],
        Genre.ELECTRONIC.value: ["electronic dance", "edm hits"]
    },
    Mood.CHILL.value: {
        Genre.POP.value: ["chill pop", "acoustic pop"],
        Genre.ROCK.value: ["soft rock", "indie rock"],
        Genre.HIP_HOP.value: ["chill hip hop", "lo-fi"],
        Genre.ELECTRONIC.value: ["ambient", "chill electronic"]
    },
    Mood.HAPPY.value: {
        Genre.POP.value: ["happy pop", "summer hits"],
        Genre.ROCK.value: ["feel good rock", "positive rock"],
        Genre.HIP_HOP.value: ["uplifting hip hop", "positive rap"],
        Genre.ELECTRONIC.value: ["happy electronic", "uplifting edm"]
    },
    Mood.PARTY.value: {
        Genre.POP.value: ["party pop", "dance pop"],
        Genre.ROCK.value: ["party rock", "dance rock"],
        Genre.HIP_HOP.value: ["party hip hop", "club rap"],
        Genre.ELECTRONIC.value: ["party edm", "club music"]
    }
}

# Language filter mappings
LANGUAGE_FILTERS = {
    Language.ENGLISH.value: "english",
    Language.SPANISH.value: "spanish español",
    Language.FRENCH.value: "french français",
    Language.GERMAN.value: "german deutsch",
    Language.ITALIAN.value: "italian italiano",
    Language.PORTUGUESE.value: "portuguese português",
    Language.HINDI.value: "hindi",
    Language.KOREAN.value: "korean 한국어",
    Language.JAPANESE.value: "japanese 日本語",
    Language.CHINESE.value: "chinese 中文"
}

# Playlist themes for AI generation
PLAYLIST_THEMES = {
    "chill vibes": {
        "genres": ["chill", "ambient", "indie"],
        "search_query": "chill ambient music",
        "features": {
            "max_energy": 0.4,
            "target_valence": 0.3,
            "max_tempo": 120
        }
    },
    "workout": {
        "genres": ["pop", "hip-hop", "electronic"],
        "search_query": "workout motivation music",
        "features": {
            "min_energy": 0.8,
            "min_danceability": 0.7,
            "target_tempo": 130
        }
    },
    "study": {
        "genres": ["classical", "ambient", "instrumental"],
        "search_query": "study focus music",
        "features": {
            "max_energy": 0.3,
            "target_instrumentalness": 0.8,
            "max_valence": 0.4
        }
    },
    "party": {
        "genres": ["pop", "dance", "hip-hop"],
        "search_query": "party dance music",
        "features": {
            "min_energy": 0.8,
            "min_danceability": 0.8,
            "target_valence": 0.8
        }
    }
}

# UI Messages
MESSAGES = {
    "NO_USER_DATA": "No recent listening data found. Please search for artists or tracks to get recommendations.",
    "NO_TRACKS_FOUND": "No tracks found. Please search for artists or tracks to get recommendations.",
    "POPULAR_TRACKS_FALLBACK": "Here are some popular tracks based on your mood, genre, and language preferences.",
    "NO_RECOMMENDATIONS": "No recommendations found. Try different settings.",
    "SEARCH_FAILED": "Search failed. Please try again.",
    "NO_SEARCH_RESULTS": "No results found. Try a different search term.",
    "ADD_SEEDS_FIRST": "Please add some artists or tracks first.",
    "PLAYLIST_CREATED": "Playlist created successfully!",
    "TRACK_ADDED": "Track added to playlist!",
    "FAILED_TO_CREATE_PLAYLIST": "Failed to create playlist: ",
    "FAILED_TO_ADD_TRACK": "Failed to add track: ",
    "NOT_AUTHENTICATED": "Not authenticated"
}

# HTTP Status Codes
HTTP_STATUS = {
    "OK": 200,
    "BAD_REQUEST": 400,
    "UNAUTHORIZED": 401,
    "NOT_FOUND": 404,
    "INTERNAL_SERVER_ERROR": 500
}

# Spotify API related constants
SPOTIFY = {
    "MAX_SEED_ITEMS": 5,
    "DEFAULT_MARKET": "US",
    "TRACK_URI_PREFIX": "spotify:track:",
    "ARTIST_URI_PREFIX": "spotify:artist:",
    "PLAYLIST_URI_PREFIX": "spotify:playlist:"
}

# Template display limits
DISPLAY_LIMITS = {
    "DASHBOARD_RECENT_TRACKS": 5,
    "DASHBOARD_TOP_ARTISTS": 5,
    "ANALYZE_TOP_TRACKS": 10,
    "ANALYZE_TOP_ARTISTS": 10,
    "DISCOVER_RECOMMENDATIONS": 20,
    "SEARCH_RESULTS": 10,
    "GENRE_DISTRIBUTION": 10
} 