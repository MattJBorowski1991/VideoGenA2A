# VideoGenA2A

VideoGenA2A is an agentic system for generating custom videos from text prompts and uploading them to YouTube. Built on Google's VEO (Video Generation) technology, it leverages the `google-generativeai` library to transform text descriptions into engaging video content.

## System Components

### Video Generation Agent
- Handles the core video generation using Google's VEO model
- Manages video processing and storage in Google Cloud Storage
- Provides real-time progress updates during generation

### CLI Client
- Simple command-line interface for interacting with the video generation agent
- Supports streaming responses from the A2A server
- Displays all server responses directly in the console
- Automatically uses streaming when supported by the server

## Features

- **AI-Powered Video Generation**: Convert text prompts into high-quality videos using Google's VEO model
- **YouTube Integration**: Directly upload generated videos to YouTube
- **Agent-Based Architecture**: Built on an agent framework for extensible and maintainable code
- **Real-time Progress**: Streaming updates during video generation
- **Cloud Storage**: Secure storage and signed URL access for generated videos in Google Cloud Storage
- **Simple CLI**: User-friendly command-line interface for interaction

## Prerequisites

### System Requirements
- **Python 3.12 or higher**
- **UV** package manager ([Installation Guide](https://docs.astral.sh/uv/))

### Google Cloud Setup
- **Google Cloud Project** with:
  - Vertex AI API enabled
  - Cloud Storage API enabled
  - YouTube Data API v3 enabled (for YouTube uploads)
- **Service Account** with appropriate IAM permissions for:
  - Vertex AI access
  - Cloud Storage bucket operations
  - Service Account Token Creator role (for signed URLs)

### CLI - A2AClient
- A running A2A server (the Video Generation Agent) to connect to

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/MattBorowski1991/VideoGenA2A.git
   cd VideoGenA2A
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   uv sync
   ```

## Configuration

### 1. Agent Configuration
Create a `.env` file in the `agents/videogena2a` directory with the following variables:

```env
# Google Cloud Configuration
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=your-project-location  # e.g., us-central1
VIDEO_GEN_GCS_BUCKET=your-gcs-bucket-name
SIGNER_SERVICE_ACCOUNT_EMAIL=your-service-account-email@project.iam.gserviceaccount.com

# VEO Model Configuration
VEO_MODEL_NAME=veo-2.0-generate-001  # Default model
VEO_POLLING_INTERVAL_SECONDS=5  # Interval for progress updates
```

### 2. YouTube Configuration
Place the following files in the `hosts/cli` directory:
- `credentials.json` - Will be generated after first authorization
- `client_secrets.json` - From your Google Cloud Console

### Environment Variables Explained

- `GOOGLE_GENAI_USE_VERTEXAI`: Enables Vertex AI integration
- `GOOGLE_CLOUD_PROJECT`: Your GCP project ID
- `GOOGLE_CLOUD_LOCATION`: The region for your GCP services
- `VIDEO_GEN_GCS_BUCKET`: Name of your GCS bucket for storing generated videos
- `SIGNER_SERVICE_ACCOUNT_EMAIL`: Service account used for generating signed URLs
- `VEO_MODEL_NAME`: Specifies which VEO model to use (default: veo-2.0-generate-001)

## Usage

### 1. Running the Agent Server

First, start the Video Generation A2A Agent server from the `agents/videogena2a` directory:

```bash
cd agents/videogena2a
uv run .
```

This will start the agent server on `http://localhost:10003` by default.

### 2. Running the A2A CLI Client

In a separate terminal, navigate to the CLI client directory and run:

```bash
cd hosts/cli
uv run . --agent http://localhost:10003
```

### Generating Videos

The CLI client will generate consecutive videos of kitten playing with a puppy with varying number of kitten and surrounding: background color, ground type. Each video will be immediately uploaded to the Youtube channel of the author (https://www.youtube.com/@mattjborowski) after generation.

## Architecture

```
VideoGenA2A/
├── agents/                  # Agent implementations
│   └── videogena2a/         # Video generation agent
│       ├── agent.py         # Main agent class
│       └── agent_executor.py# Agent execution logic
├── common/                  # Shared utilities
├── hosts/                   # Host applications
│   └── cli/                 # Command-line interface
└── youtube-video-upload/    # YouTube upload functionality
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


