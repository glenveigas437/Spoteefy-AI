# 🎵 Spoteefy - Now powered by AI

A modern, AI-powered music discovery platform built with Flask and Spotify Web API.

## ✨ Features

- **AI-Powered Music Discovery**: Get personalized recommendations based on mood and preferences
- **Smart Playlist Generation**: Create AI-generated playlists for any theme or activity
- **Music Analysis**: Deep insights into your listening patterns and music taste
- **Mood-Based Recommendations**: Find the perfect music for your current mood
- **Modern Web Interface**: Beautiful, responsive design with real-time updates

## 🏗️ Architecture

The application follows a modular, scalable architecture:

```
spotify-ai-app/
├── app/
│   ├── __init__.py          # Application factory
│   ├── routes/              # Route blueprints
│   │   ├── auth.py         # Authentication routes
│   │   ├── main.py         # Main application routes
│   │   └── api.py          # API endpoints
│   ├── services/           # Business logic services
│   │   ├── auth_service.py # Spotify OAuth handling
│   │   ├── spotify_service.py # Spotify API interactions
│   │   └── ai_service.py   # AI-powered features
│   ├── templates/          # HTML templates
│   └── static/             # Static assets
├── config/
│   └── settings.py         # Configuration settings
├── requirements.txt        # Python dependencies
└── app.py                 # Application entry point
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Spotify Developer Account
- OpenAI API Key (optional, for enhanced AI features)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd spotify-ai-app
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   SPOTIFY_REDIRECT_URI=http://localhost:5000/auth/callback
   SECRET_KEY=your_secret_key
   OPENAI_API_KEY=your_openai_api_key  # Optional
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open your browser**
   Navigate to `http://localhost:5000`

## 🔧 Configuration

### Spotify API Setup

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new application
3. Add `http://localhost:5000/auth/callback` to Redirect URIs
4. Copy Client ID and Client Secret to your `.env` file

### OpenAI API Setup (Optional)

1. Get an API key from [OpenAI](https://platform.openai.com/)
2. Add it to your `.env` file for enhanced AI features

## 📱 Features Overview

### Dashboard
- View your Spotify profile
- See recently played tracks
- Discover your top artists

### AI Discovery
- Mood-based recommendations
- Genre-specific suggestions
- Personalized music discovery

### Music Analysis
- Listening pattern insights
- Genre distribution analysis
- Audio feature statistics

### Smart Playlists
- AI-generated playlists
- Theme-based creation
- Automatic track selection

## 🛠️ Development

### Project Structure

- **Routes**: Handle HTTP requests and responses
- **Services**: Business logic and external API interactions
- **Templates**: HTML views with Jinja2 templating
- **Config**: Application configuration and settings

### Adding New Features

1. **Create a new route** in `app/routes/`
2. **Add business logic** in `app/services/`
3. **Create templates** in `app/templates/`
4. **Update configuration** if needed

### Testing

```bash
# Run with debug mode
python app.py

# Or use Flask CLI
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

## 🔒 Security

- OAuth 2.0 authentication with Spotify
- Secure session management
- Environment variable configuration
- Input validation and sanitization

## 📊 API Endpoints

### Authentication
- `GET /auth/login` - Spotify OAuth login
- `GET /auth/callback` - OAuth callback handler
- `GET /auth/logout` - User logout

### Main Routes
- `GET /` - Landing page
- `GET /dashboard` - User dashboard
- `GET /discover` - AI-powered discovery
- `GET /analyze` - Music analysis
- `GET /playlists` - Playlist management

### API Endpoints
- `GET /api/recommendations` - Get track recommendations
- `POST /api/create-playlist` - Create AI playlist
- `GET /api/user-stats` - User statistics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Spotify Web API for music data
- OpenAI for AI-powered features
- Flask community for the web framework
- Bootstrap for the UI components

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the code comments

---

**Happy coding! 🎵✨** 
