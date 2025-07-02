from flask import Flask
from config.settings import config
import os

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG') or 'default'
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    from app.routes import auth, main, api
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(api.bp)
    @app.context_processor
    def inject_constants():
        from app.constants import (
            Mood, Genre, Language, TimeRange, DEFAULT_MOOD, DEFAULT_GENRE, 
            DEFAULT_LANGUAGE, DEFAULT_TIME_RANGE, MESSAGES, DISPLAY_LIMITS
        )
        from app.utils import (
            get_mood_options, get_genre_options, get_language_options,
            get_time_range_options, format_duration, truncate_text,
            get_artist_names, get_album_image_url
        )
        return {
            'Mood': Mood,
            'Genre': Genre,
            'Language': Language,
            'TimeRange': TimeRange,
            'DEFAULT_MOOD': DEFAULT_MOOD,
            'DEFAULT_GENRE': DEFAULT_GENRE,
            'DEFAULT_LANGUAGE': DEFAULT_LANGUAGE,
            'DEFAULT_TIME_RANGE': DEFAULT_TIME_RANGE,
            'MESSAGES': MESSAGES,
            'DISPLAY_LIMITS': DISPLAY_LIMITS,
            'get_mood_options': get_mood_options,
            'get_genre_options': get_genre_options,
            'get_language_options': get_language_options,
            'get_time_range_options': get_time_range_options,
            'format_duration': format_duration,
            'truncate_text': truncate_text,
            'get_artist_names': get_artist_names,
            'get_album_image_url': get_album_image_url
        }
    return app 