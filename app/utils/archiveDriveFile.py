def archive_drive_file(drive_service, file_id, source_folder_id, dest_folder_name="Archived"):
    """Moves a file to a specified destination folder in Google Drive."""
    try:
        # --- 1. Find the Destination Folder ID ---
        folder_query = f"name = '{dest_folder_name}' and mimeType = 'application/vnd.google-apps.folder'"
        folder_results = drive_service.files().list(q=folder_query, fields="files(id)").execute()
        folders = folder_results.get('files', [])

        if not folders:
            raise FileNotFoundError(f"Destination folder '{dest_folder_name}' not found.")
        dest_folder_id = folders[0].get('id')

        # --- 2. Move the file by updating its parents ---
        drive_service.files().update(
            fileId=file_id,
            addParents=dest_folder_id,
            removeParents=source_folder_id,
            fields='id, parents'
        ).execute()
        
        print(f"✅ Successfully moved file to '{dest_folder_name}' folder.")
        return True

    except Exception as e:
        print(f"❌ Failed to archive file: {e}")
        raise