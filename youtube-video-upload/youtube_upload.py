"""YouTube Video Uploader for VideoGenA2A."""

import os
import pickle
from typing import Optional
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']


class YouTubeUploader:
    """Handles authentication and uploading videos to YouTube."""

    def __init__(self, credentials_path: str = 'credentials.json', token_path: str = 'token.pickle'):
        """Initialize with paths to credentials and token files.
        
        Args:
            credentials_path: Path to the OAuth 2.0 credentials JSON file.
            token_path: Path to store the user's access and refresh tokens.
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.youtube = self._get_authenticated_service()

    def _get_authenticated_service(self):
        """Get authenticated YouTube API service."""
        creds = None
        
        # The file token.pickle stores the user's access and refresh tokens
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        return build('youtube', 'v3', credentials=creds)

    def upload_video(
        self,
        file_path: str,
        title: str,
        description: str = "",
        category_id: str = "22",  # Category 22 is "People & Blogs"
        tags: Optional[list] = None,
        privacy_status: str = "private"  # or "public", "unlisted"
    ) -> dict:
        """Upload a video to YouTube.
        
        Args:
            file_path: Path to the video file to upload.
            title: Title of the video.
            description: Description of the video.
            category_id: YouTube video category ID.
            tags: List of video tags.
            privacy_status: Privacy status of the video.
            
        Returns:
            dict: The response from the YouTube API.
        """
        if tags is None:
            tags = []
            
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': privacy_status
            }
        }
        
        media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
        
        request = self.youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=media
        )
        
        return request.execute()

    def upload_from_gcs(
        self,
        gcs_uri: str,
        title: str,
        description: str = "",
        category_id: str = "22",
        tags: Optional[list] = None,
        privacy_status: str = "private"
    ) -> dict:
        """Upload a video to YouTube from Google Cloud Storage.
        
        Args:
            gcs_uri: Google Cloud Storage URI (e.g., 'gs://bucket/path/to/video.mp4').
            title: Title of the video.
            description: Description of the video.
            category_id: YouTube video category ID.
            tags: List of video tags.
            privacy_status: Privacy status of the video.
            
        Returns:
            dict: The response from the YouTube API.
        """
        # Download the file from GCS first
        from google.cloud import storage
        import tempfile
        import os
        
        # Parse GCS URI
        if not gcs_uri.startswith('gs://'):
            raise ValueError("Invalid GCS URI. Must start with 'gs://'")
            
        path_parts = gcs_uri[5:].split('/')
        bucket_name = path_parts[0]
        blob_name = '/'.join(path_parts[1:])
        
        # Download file to a temporary location
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(blob_name)[1]) as temp_file:
            blob.download_to_file(temp_file)
            temp_file_path = temp_file.name
        
        try:
            # Upload the downloaded file to YouTube
            response = self.upload_video(
                file_path=temp_file_path,
                title=title,
                description=description,
                category_id=category_id,
                tags=tags,
                privacy_status=privacy_status
            )
            return response
        finally:
            # Clean up the temporary file
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                print(f"Warning: Could not delete temporary file {temp_file_path}: {e}")


if __name__ == "__main__":
    # Example usage
    uploader = YouTubeUploader()
    
    # For local file
    # response = uploader.upload_video(
    #     file_path="path/to/your/video.mp4",
    #     title="My Awesome Video",
    #     description="This is a test video",
    #     tags=["test", "video"],
    #     privacy_status="private"
    # )
    
    # For GCS file
    # response = uploader.upload_from_gcs(
    #     gcs_uri="gs://your-bucket/path/to/video.mp4",
    #     title="My Awesome Video from GCS",
    #     description="This is a test video from GCS",
    #     tags=["test", "gcs", "video"],
    #     privacy_status="private"
    # )
    
    # print(f"Upload successful! Video ID: {response['id']}")
