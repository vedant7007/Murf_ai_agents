# Setup Instructions for Your Friend

This guide will help anyone clone and run this voice agent project on their system.

## Prerequisites

Before starting, make sure you have these installed:

1. **Python 3.9+** - [Download here](https://www.python.org/downloads/)
2. **uv** (Python package manager) - Install with:
   ```bash
   pip install uv
   ```
3. **Node.js 18+** - [Download here](https://nodejs.org/)
4. **pnpm** - Install with:
   ```bash
   npm install -g pnpm
   ```
5. **LiveKit Server** - Download for your OS:
   - **Windows**: [Download livekit-server.exe](https://github.com/livekit/livekit/releases)
   - **macOS**: `brew install livekit`
   - **Linux**: Download from [LiveKit releases](https://github.com/livekit/livekit/releases)

## Required API Keys

You'll need to get these API keys (all have free tiers):

1. **Deepgram API Key** - [Sign up at deepgram.com](https://deepgram.com/)
2. **Google API Key** (for Gemini) - [Get from Google AI Studio](https://makersuite.google.com/app/apikey)
3. **Murf API Key** - [Sign up at murf.ai](https://murf.ai/)

## Installation Steps

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd ten-days-of-voice-agents-2025
```

### 2. Backend Setup

```bash
cd backend

# Install dependencies
uv sync

# Create environment file
cp .env.example .env

# Edit .env and add your API keys:
# LIVEKIT_URL=ws://127.0.0.1:7880
# LIVEKIT_API_KEY=devkey
# LIVEKIT_API_SECRET=secret
# GOOGLE_API_KEY=your_google_api_key_here
# MURF_API_KEY=your_murf_api_key_here
# DEEPGRAM_API_KEY=your_deepgram_api_key_here

cd ..
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
pnpm install

# Create environment file
cp .env.example .env.local

# Edit .env.local and add:
# LIVEKIT_URL="ws://127.0.0.1:7880"
# LIVEKIT_API_KEY="devkey"
# LIVEKIT_API_SECRET="secret"

cd ..
```

### 4. Running the Application

You need to run **3 separate terminals**:

#### Terminal 1: LiveKit Server

**Windows:**
```bash
./livekit-server.exe --dev
```

**macOS/Linux:**
```bash
livekit-server --dev
```

#### Terminal 2: Backend Agent

```bash
cd backend
uv run python src/agent.py dev
```

#### Terminal 3: Frontend

```bash
cd frontend
pnpm dev
```

### 5. Open the Application

Open your browser and go to: **http://localhost:3000**

## Troubleshooting

### Agent not responding?

1. Check that all 3 servers are running
2. Verify all API keys are correctly set in the `.env` files
3. Make sure `load_dotenv()` has parentheses in `backend/src/agent.py` (line 23)

### LiveKit connection issues?

1. Ensure LiveKit server is running on port 7880
2. Check that the same credentials are in both backend/.env and frontend/.env.local

### Missing dependencies?

- Backend: Run `uv sync` in the backend folder
- Frontend: Run `pnpm install` in the frontend folder

## Important Notes

- **Never commit your `.env` files** - they contain sensitive API keys
- The `.env.example` files show the format but don't contain real keys
- Each person needs their own API keys

## Support

If you encounter issues:
1. Check that all prerequisites are installed
2. Verify your API keys are valid
3. Make sure all 3 servers are running
4. Check the console logs for error messages

Enjoy building with voice AI! 🎙️
