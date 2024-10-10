# MovieSphere Network

MovieSphere Network is a Flask-based web application designed for movie enthusiasts. It provides a platform for users to discuss movies, upload and download music, and engage in real-time chat. The application integrates various third-party services, including Google Drive for music file storage and Render.com for deployment.

## Features

- **User Authentication**: Secure user registration and login with Flask-Login and bcrypt for password hashing.
- **User Authentication using Google Sign-In**: Users can sign in using their Google account via OAuth 2.0 integration using Google Cloud Platform (GCP). If a user is not registered, they are automatically added to the database as a new user upon signing in with Google.
- **Real-time Chat**: Implemented using Flask-SocketIO, allowing users to communicate instantly in various chat rooms (NEWS, MOVIES, GAMES, MUSIC).
- **Music Upload & Download**: Users can upload music files, which are securely stored in Google Drive using the Google Drive API (GCP service account). Files are available for download from the music store.
- **Movie Posts**: Users can create, edit, and delete movie posts, like and comment on them.
- **Profile Management**: Users can edit their profiles, change their email addresses, or reset their passwords.
- **Follow System**: Users can follow each other and stay updated on each other's activities.
- **Personal Movie Watchlist**: Users can create their own movie watchlists where they can add details such as a YouTube trailer link, movie description, and other relevant information. Additionally, users can add movies from other users' watchlists to their own.
- **Email Notifications**: Email notifications for password resets and other user-related events using Flask-Mail.
- **Secure File Uploads**: User-uploaded files are stored securely using Google Drive integration with service accounts.

## Tech Stack

- **Flask**: Backend web framework.
- **PostgreSQL**: Database hosted on Render.com.
- **Google Drive API**: Used for music file storage via service accounts (GCP).
- **Socket.IO**: Real-time chat functionality.
- **Flask-Mail**: Email notifications for password resets and account changes.
- **Flask-SQLAlchemy**: ORM for database management.
- **Flask-WTF**: Form handling and CSRF protection.
- **Flask-Bcrypt**: Secure password hashing.
- **Flask-Login**: User session management and authentication.
- **Render.com**: Hosting for the application and PostgreSQL database.
- **Namecheap**: Domain name hosting.

## Application Structure

- **Authentication & User Management**:
  - `flask_login`: Handles user authentication and session management.
  - `bcrypt`: Provides password hashing for secure storage.
  - **Forms**: `RegistrationForm`, `LoginForm`, `EditDetails`, etc., for user actions.

- **Database Models**:
  - `User`, `Post`, `PostMain`, `Messages`, `Like`, `UploadMusic`: ORM models using SQLAlchemy.
  
- **Movie Watchlist**:
  - Users can create personal watchlists, including details such as YouTube trailer links, descriptions, and ratings.
  - Users can also add movies to their watchlists from other users' lists.
  
- **Music Uploads**:
  - Uses Google Drive API for secure file storage with `service_account` from GCP.
  - Music files are stored and managed via the `UploadMusicForm`.

- **Follow System**:
  - Users can follow each other, view posts from the people they follow, and interact with others' watchlists.

- **Chat Rooms**:
  - Real-time chat is powered by Flask-SocketIO with predefined rooms like "NEWS", "MOVIES", "GAMES", and "MUSIC".

- **CSRF Protection**:
  - Flask-WTF ensures that all forms are secured with CSRF tokens.
  
- **Routes**:
  - Handled in `movie_wl.routes.pages` using a blueprint for page rendering and redirects.

## Configuration

The application uses environment variables for sensitive configurations. These include:

- `SECRET_KEY_MW`: Secret key for session management.
- `SQLALCHEMY_DATABASE_URI_MW`: PostgreSQL database URI.
- `EMAIL_USER_MN`: Email username for sending notifications.
- `MAIL_APP_PASSWORD_MN`: App password for sending emails.
- `GOOGLE_CREDENTIALS_PATH`: Path to the Google Drive API service account credentials.
- `GOOGLE_CREDENTIAL_OAUTH_PROD`: Path to the Client ID secrets (json file).

## Deployment

- **Hosting**: The app is deployed on Render.com using their PostgreSQL service for the database.
- **SSL Certificate**: An SSL certificate is configured for HTTPS access.
- **Domain Name**: The domain name was purchased via Namecheap and configured to point to the Render.com deployment.
