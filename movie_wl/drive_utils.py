from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_drive_service():
    credentials = service_account.Credentials.from_service_account_file(
        os.environ.get("GOOGLE_CREDENTIALS_PATH"),
        scopes=SCOPES
    )
    drive_service = build('drive', 'v3', credentials=credentials)
    return drive_service

def upload_to_drive(file):
    drive_service = get_drive_service()

    # Define the file metadata
    file_metadata = {
        'name': file.filename,  # Use the uploaded file's name
        'mimeType': file.content_type  # Use the uploaded file's MIME type
    }

    # Create a MediaFileUpload object
    media = MediaFileUpload(file, mimetype=file.content_type)

    # Upload the file to Google Drive
    uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    
    return uploaded_file.get('id')  # Return the Google Drive file ID