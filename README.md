# VideoGenA2A 🎥

VideoGenA2A is an agentic system for generating custom videos from text prompts and seamlessly uploading them to YouTube. Built on Google's VEO (Video Generation) technology, it leverages the `google-generativeai` library to transform text descriptions into high-quality, engaging video content. 🚀

## Table of Contents
- [System Components](#system-components-🛠️)
- [Features](#features-✨)
- [Prerequisites](#prerequisites-📋)
- [Installation](#installation-⚙️)
- [Configuration](#configuration-🔧)
- [Usage](#usage-🎬)
- [Architecture](#architecture-🏗️)
- [Contributing](#contributing-🤝)
- [License](#license-📜)

## System Components 🛠️

### Video Generation Agent
- 🎨 Powers core video generation using Google's VEO model.
- 💾 Manages video processing and storage in Google Cloud Storage.
- 📊 Provides real-time progress updates during video generation.

### CLI Client
- 🖥️ Simple command-line interface for interacting with the Video Generation Agent.
- 📡 Supports streaming responses from the A2A server.
- 🖨️ Displays all server responses directly in the console.
- 🔄 Automatically uses streaming when supported by the server.

## Features ✨
- **AI-Powered Video Generation**: Converts text prompts into high-quality videos using Google's VEO model. 🎞️
- **YouTube Integration**: Automatically uploads generated videos to YouTube. 📤
- **Agent-Based Architecture**: Built on an extensible and maintainable agent framework. 🧩
- **Real-Time Progress**: Provides streaming updates during video generation. ⏳
- **Cloud Storage**: Stores generated videos securely in Google Cloud Storage with signed URL access. ☁️
- **User-Friendly CLI**: Simplifies interaction through a command-line interface. ⌨️

## Prerequisites 📋

### System Requirements
- **Python**: Version 3.12 or higher. 🐍
- **UV Package Manager**: Refer to the [Installation Guide](https://docs.astral.sh/uv/getting-started/installation/) for setup instructions. 📦

### Google Cloud Setup
- ☁️ A Google Cloud Project with the following APIs enabled:
  - Vertex AI API
  - Cloud Storage API
  - YouTube Data API v3 (for YouTube uploads)
- 🔑 A Service Account with the following IAM permissions:
  - Vertex AI access
  - Cloud Storage bucket operations
  - Service Account Token Creator role (for signed URLs)

### CLI - A2AClient
- 🖧 A running A2A server (Video Generation Agent) to connect to.

## Installation ⚙️

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/MattBorowski1991/VideoGenA2A.git
   cd VideoGenA2A
   ```

2. **Create and Activate a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. **Install Required Packages**:
   ```bash
   uv sync
   ```

## Configuration 🔧

### 1. Agent Configuration
Create a `.env` file in the `agents/videogena2a` directory with the following variables:

```bash
# Google Cloud Configuration ☁️
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=your-project-location  # e.g., us-central1
VIDEO_GEN_GCS_BUCKET=your-gcs-bucket-name
SIGNER_SERVICE_ACCOUNT_EMAIL=your-service-account-email@project.iam.gserviceaccount.com

# VEO Model Configuration 🎥
VEO_MODEL_NAME=veo-2.0-generate-001  # Default model
VEO_POLLING_INTERVAL_SECONDS=5  # Interval for progress updates
```

### 2. YouTube Configuration
Place the following files in the `hosts/cli` directory:
- `credentials.json`: Generated after the first YouTube authorization. 🔐
- `client_secrets.json`: Obtained from your Google Cloud Console. 🔑

### Environment Variables Explained
- **GOOGLE_GENAI_USE_VERTEXAI**: Enables Vertex AI integration. ✅
- **GOOGLE_CLOUD_PROJECT**: Your Google Cloud project ID. 🆔
- **GOOGLE_CLOUD_LOCATION**: The region for your GCP services (e.g., `us-central1`). 🌍
- **VIDEO_GEN_GCS_BUCKET**: Name of the Google Cloud Storage bucket for storing videos. 📦
- **SIGNER_SERVICE_ACCOUNT_EMAIL**: Service account email for generating signed URLs. ✉️
- **VEO_MODEL_NAME**: Specifies the VEO model (default: `veo-2.0-generate-001`). 🎬
- **VEO_POLLING_INTERVAL_SECONDS**: Interval for progress updates during video generation. ⏱️

## Usage 🎬

### 1. Running the Agent Server
Start the Video Generation A2A Agent server from the `agents/videogena2a` directory:

```bash
cd agents/videogena2a
uv run .
```

This starts the agent server on `http://localhost:10003` by default. 🌐

### 2. Running the A2A CLI Client
In a separate terminal, navigate to the CLI client directory and run:

```bash
cd hosts/cli
uv run . --agent http://localhost:10003
```

### Generating Videos
The CLI client generates videos of a baby foxes playing with chicken, with random variations in the number of animals, background color, and ground type. Each video is automatically uploaded to the YouTube channel of the author ([@mattjborowski](https://www.youtube.com/@mattjborowski)) after generation. 

## Architecture 🏗️

The project is organized as follows:

```
VideoGenA2A/
├── agents/                  # Agent implementations 🧠
│   └── videogena2a/         # Video generation agent
│       ├── agent.py         # Main agent class
│       └── agent_executor.py# Agent execution logic
├── common/                  # Shared utilities 🛠️
├── hosts/                   # Host applications 🖥️
│   └── cli/                 # Command-line interface
└── youtube-video-upload/    # YouTube upload functionality 📤
```

## Contributing 🤝

1. Fork the repository. 🍴
2. Create a feature branch:
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. Commit your changes:
   ```bash
   git commit -m 'Add some AmazingFeature'
   ```
4. Push to the branch:
   ```bash
   git push origin feature/AmazingFeature
   ```
5. Open a Pull Request. 📬

## License 📜

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
