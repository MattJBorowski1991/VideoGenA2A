# YouTube Video Upload

This module provides functionality to upload videos to YouTube, either from local files or Google Cloud Storage.

## Setup

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up OAuth 2.0 credentials:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the YouTube Data API v3
   - Create OAuth 2.0 credentials (Desktop application)
   - Download the credentials and save as `credentials.json` in this directory

## Usage

```python
from youtube_video_upload import YouTubeUploader

# Initialize the uploader
uploader = YouTubeUploader()

# Upload a local file
response = uploader.upload_video(
    file_path="path/to/your/video.mp4",
    title="My Video Title",
    description="My video description",
    tags=["tag1", "tag2"],
    privacy_status="private"  # or "public", "unlisted"
)

# Or upload from Google Cloud Storage
response = uploader.upload_from_gcs(
    gcs_uri="gs://your-bucket/path/to/video.mp4",
    title="My Video from GCS",
    description="Uploaded from Google Cloud Storage",
    tags=["gcs", "upload"],
    privacy_status="private"
)

print(f"Uploaded video ID: {response['id']}")
```

## Authentication

The first time you run the uploader, it will open a browser window to authenticate with your Google account. The authentication tokens will be saved to `token.pickle` for future use.

## Privacy Policy

Please review the `PRIVACY_POLICY.md` file for information about data handling and privacy.
