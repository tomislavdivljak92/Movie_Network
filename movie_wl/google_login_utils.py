import os
import json
from flask import session, redirect, url_for, request
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from movie_wl import db
from movie_wl.models import User
from google_auth_oauthlib.flow import Flow




# Function to determine the credentials based on the environment
def get_google_oauth_credentials():
    if os.getenv('RENDER'):  # Render.com (Production)
        # Load credentials from the environment variable as a dictionary
        return json.loads(os.environ['GOOGLE_CREDENTIAL_OAUTH_PROD'])
    else:  # Local development
        credentials_path = os.getenv('GOOGLE_CREDENTIAL_OAUTH_LOCAL')
        return credentials_path  # Return path for local

# Setup Google OAuth Flow
def get_google_auth_flow():
    credentials = get_google_oauth_credentials()

    # Check if credentials are a dict (for production) or a file path (for local)
    if isinstance(credentials, dict):
        # Use from_client_config if credentials are passed as a dict
        flow = Flow.from_client_config(
            credentials,
            scopes=['https://www.googleapis.com/auth/userinfo.email',
                    'https://www.googleapis.com/auth/userinfo.profile',
                    'openid'],
            # Force HTTPS for the redirect URI
            redirect_uri=url_for('pages.google_callback', _external=True, _scheme='https')
        )
    else:
        # Use from_client_secrets_file if credentials are loaded from a file
        flow = Flow.from_client_secrets_file(
            credentials,
            scopes=['https://www.googleapis.com/auth/userinfo.email',
                    'https://www.googleapis.com/auth/userinfo.profile',
                    'openid'],
            redirect_uri=url_for('pages.google_callback', _external=True, _scheme='https')
        )

    return flow

# Initiates the Google login process
def initiate_google_login():
    flow = get_google_auth_flow()
    authorization_url, state = flow.authorization_url()
    session['state'] = state
    return redirect(authorization_url)

# Handles the Google callback and processes the user's info
def handle_google_callback():
    flow = get_google_auth_flow()

    # Fetch the token from the Google response
    flow.fetch_token(authorization_response=request.url)

    # CSRF protection: Check if the state matches
    if not session['state'] == request.args['state']:
        return redirect(url_for('pages.login'))  # CSRF protection fail

    credentials = flow.credentials
    request_session = google_requests.Request()

    # Get user info from Google's OAuth 2.0 API
    user_info = id_token.verify_oauth2_token(credentials.id_token, request_session)

    if user_info:
        # Check if the user already exists in the database
        user = User.query.filter_by(email=user_info['email']).first()
        if not user:
            # Create a new user if they don't exist
            user = User(username=user_info['name'], email=user_info['email'])
            db.session.add(user)
            db.session.commit()

        return user_info  # Return user info for login
    return None