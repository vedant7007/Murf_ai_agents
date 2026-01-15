# Day 1: AI Voice Agent Foundation

This project serves as the foundational boilerplate for the **AI Voice Agents Challenge**. It provides a complete, full-stack application structure for building and interacting with a real-time AI voice agent.

The goal for Day 1 is to understand the architecture, set up the development environment, and run the baseline voice agent successfully.

---

## 🚀 Core Technologies

This project is a monorepo integrating several key technologies:

| Area      | Technology                                    | Purpose                                     |
| :-------- | :-------------------------------------------- | :------------------------------------------ |
| **Backend** | [Python](https://www.python.org/) with `uv`         | Agent logic and server-side processing.     |
| **Frontend**  | [Next.js](https://nextjs.org/) (React) with `pnpm`  | User interface and client-side interaction. |
| **Real-time** | [LiveKit Agents](https://docs.livekit.io/agents/) | Manages real-time audio and data streams.    |
| **LLM**       | [Google Gemini](https://ai.google.dev/)       | Core conversational intelligence.           |
| **TTS**       | [Murf Falcon](https://murf.ai/api)            | Ultra-fast Text-to-Speech synthesis.        |
| **STT**       | [Deepgram](https://deepgram.com/)             | Real-time Speech-to-Text transcription.     |

---

## directory Structure

The project is divided into two main parts:

```
.
├── backend/      # Python-based agent logic (LiveKit, Gemini, Murf, Deepgram)
├── frontend/     # Next.js UI for voice interaction
└── README.md     # This file
```

---

## 🛠️ Setup and Usage

To get started, you need to set up the backend, frontend, and a local LiveKit server.

### Prerequisites

Ensure you have **Python 3.9+**, **Node.js 18+**, `uv`, and `pnpm` installed. You will also need API keys for **Google Gemini**, **Murf**, and **Deepgram**.

For highly detailed, step-by-step instructions, please refer to the [SETUP_INSTRUCTIONS.md](./SETUP_INSTRUCTIONS.md) file.

### Quick Start

1.  **Configure Backend:**
    *   Navigate to the `backend/` directory.
    *   Install dependencies with `uv sync`.
    *   Copy `.env.example` to `.env.local` and fill in your API keys.

2.  **Configure Frontend:**
    *   Navigate to the `frontend/` directory.
    *   Install dependencies with `pnpm install`.
    *   Copy `.env.example` to `.env.local` and add your LiveKit credentials.

3.  **Run the Application:**
    You must run three services in separate terminals:
    *   **Terminal 1 (LiveKit):** `livekit-server --dev`
    *   **Terminal 2 (Backend):** `cd backend && uv run python src/agent.py dev`
    *   **Terminal 3 (Frontend):** `cd frontend && pnpm dev`

Once all services are running, you can access the voice agent at `http://localhost:3000`.