import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Set the scopes for the Drive API
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Initialize the Drive API
def get_drive_service():
    credentials = service_account.Credentials.from_service_account_file(
        os.environ.get("GOOGLE_CREDENTIALS_PATH"),
        scopes=SCOPES
    )
    
    drive_service = build('drive', 'v3', credentials=credentials)
    return drive_service

# Upload file to Google Drive
def upload_to_drive(file_path):
    drive_service = get_drive_service()
    
    # Define the file metadata and the media body
    file_metadata = {
        'name': os.path.basename(file_path),  # Use the base filename
        'mimeType': 'audio/mpeg'  # Replace with appropriate MIME type if necessary
    }
    
    media = MediaFileUpload(file_path, mimetype='audio/mpeg')

    # Upload the file
    uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return uploaded_file.get('id')