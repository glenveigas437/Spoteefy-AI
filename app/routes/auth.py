"""
Authentication routes
"""

from flask import Blueprint, redirect, request, url_for, session
from app.services.auth_service import AuthService
from app.constants import MESSAGES, HTTP_STATUS

bp = Blueprint('auth', __name__, url_prefix='/auth')
auth_service = AuthService()

@bp.route('/login')
def login():
    """Initiate Spotify OAuth login"""
    auth_url = auth_service.get_auth_url()
    return redirect(auth_url)

@bp.route('/callback')
def callback():
    """Handle OAuth callback"""
    try:
        code = request.args.get('code')
        if code:
            # Exchange code for access token
            success = auth_service.handle_callback(code)
            if success:
                return redirect(url_for('main.dashboard'))
            else:
                return MESSAGES["NOT_AUTHENTICATED"], HTTP_STATUS["UNAUTHORIZED"]
        else:
            return 'Authorization failed', HTTP_STATUS["BAD_REQUEST"]
    except Exception as e:
        print(f"Auth callback error: {e}")
        return 'Authentication error', HTTP_STATUS["INTERNAL_SERVER_ERROR"]

@bp.route('/logout')
def logout():
    """Logout user"""
    auth_service.logout()
    return redirect(url_for('main.index')) 