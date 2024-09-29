import os
import tempfile
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
from werkzeug.utils import secure_filename

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_drive_service():
    credentials = service_account.Credentials.from_service_account_file(
        os.environ.get("GOOGLE_CREDENTIALS_SA"),
        scopes=SCOPES
    )
    drive_service = build('drive', 'v3', credentials=credentials)
    return drive_service

def upload_to_drive(file):
    drive_service = get_drive_service()

    # Define the file metadata
    file_metadata = {
        'name': secure_filename(file.filename),  # Ensure filename is secure
        'mimeType': file.content_type
    }

    # Create a temporary file for the upload
    temp_file_path = tempfile.mktemp(suffix=os.path.splitext(file.filename)[1])  # Unique temp file name

    try:
        # Save the file to the temporary path
        file.save(temp_file_path)  # Save the uploaded file to the temp file path

        # Create a MediaFileUpload object with the saved file path
        media = MediaFileUpload(temp_file_path, mimetype=file.content_type)

        # Upload the file to Google Drive
        uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        
        # Get the uploaded file ID
        file_id = uploaded_file.get('id')

        # Set permissions to allow anyone with the link to view
        permission = {
            'type': 'anyone',  # Allow anyone to access
            'role': 'reader'   # Set role to reader
        }

        # Apply the permission to the uploaded file
        drive_service.permissions().create(
            fileId=file_id,
            body=permission,
            fields='id'
        ).execute()

        return file_id  # Return the Google Drive file ID

    except Exception as e:
        print(f"An error occurred during file upload: {e}")
        raise

    finally:
        # Clean up and remove the temporary file
        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                print(f"Removed temporary file: {temp_file_path}")
            except Exception as e:
                print(f"Error removing temporary file: {e}")