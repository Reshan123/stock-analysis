import base64
import json
import os
import io
import traceback
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

def get_single_drive_file_content(folder_name: str) -> str | None:
    """
    Connects to Google Drive, finds the ONLY file in a specific folder,
    and returns its content as a string.
    """
    try:
        # --- 1. Authentication (Same as before) ---
        encoded_creds = os.getenv("GOOGLE_CREDS_BASE64")
        if not encoded_creds:
            raise RuntimeError("Missing GOOGLE_CREDS_BASE64 env var")

        service_account_info = json.loads(base64.b64decode(encoded_creds))
        scopes = ["https://www.googleapis.com/auth/drive"] # Simplified scopes

        creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)
        drive_service = build('drive', 'v3', credentials=creds)

        # --- 2. Find the Folder ID (Same as before) ---
        folder_query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder'"
        folder_results = drive_service.files().list(q=folder_query, fields="files(id)").execute()
        folders = folder_results.get('files', [])

        if not folders:
            raise FileNotFoundError(f"Folder '{folder_name}' not found.")
        folder_id = folders[0].get('id')

        # --- 3. Find the single file within the folder (MODIFIED LOGIC) ---
        # Search for any file inside the parent folder, excluding sub-folders.
        file_query = f"'{folder_id}' in parents and mimeType != 'application/vnd.google-apps.folder'"
        file_results = drive_service.files().list(q=file_query, fields="files(id, name)").execute()
        files = file_results.get('files', [])

        # Check the number of files found
        if len(files) == 0:
            raise FileNotFoundError(f"No files found in folder '{folder_name}'.")
        if len(files) > 1:
            raise RuntimeError(f"Expected 1 file, but found {len(files)} in folder '{folder_name}'.")
        
        # Get the ID and name of the single file
        the_only_file = files[0]
        file_id = the_only_file.get('id')
        file_name = the_only_file.get('name')
        print(f"Found file: {file_name}")
        
        # --- 4. Download the file content (Same as before) ---
        request = drive_service.files().get_media(fileId=file_id)
        file_handle = io.BytesIO()
        downloader = MediaIoBaseDownload(file_handle, request)
        
        done = False
        while not done:
            status, done = downloader.next_chunk()

        return file_handle.getvalue().decode('utf-8')

    except HttpError as error:
        print(f"An API error occurred: {error}")
        print(traceback.format_exc())
        return None
    except Exception as e:
        print(f"Failed to get file from Google Drive: {e}")
        print(traceback.format_exc())
        return None