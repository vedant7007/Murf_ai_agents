# 🐉 Realm of Vroskit - AI Voice RPG

**A Next-Gen Voice-Powered RPG Experience powered by LiveKit, Murf AI, and Google Gemini.**

![Realm of Vroskit Banner](https://via.placeholder.com/1200x600/0a0a0f/d4af37?text=REALM+OF+VROSKIT)

## 🌟 Overview

**Realm of Vroskit** is an immersive, voice-controlled RPG where you play as a hero in a dark fantasy world. Instead of clicking buttons, you **speak** to the Game Master (an AI agent) to explore, fight, and roleplay.

This project demonstrates the power of modern AI voice agents in creating interactive entertainment experiences. It features a stunning, game-like frontend and a sophisticated backend agent that manages game state, inventory, and narrative.

## ✨ Features

*   **🗣️ Voice-First Gameplay:** Interact naturally with the Game Master using your voice. No typing required!
*   **🎭 Dynamic AI Game Master:** Powered by **Google Gemini 1.5 Flash**, the GM narrates the story, reacts to your choices, and manages the world.
*   **🔊 Epic Voice Acting:** The GM speaks with a deep, dramatic voice powered by **Murf AI**.
*   **🎲 Real-Time Game Mechanics:**
    *   **3D Dice Rolling:** Watch dramatic 3D dice rolls for combat and skill checks.
    *   **Live Character Sheet:** Stats (HP, Gold, Inventory) update in real-time as you play.
    *   **Visual Effects:** Screen shakes, damage vignettes, and magical particle effects.
*   **⚔️ RPG Systems:**
    *   **Classes:** Choose from Warrior, Mage, or Rogue.
    *   **Inventory:** Collect items, weapons, and quest artifacts.
    *   **Quests:** Track your progress in the "Sacred Quests" log.
    *   **Combat:** Engage in turn-based battles with enemies.

## 🛠️ Tech Stack

### Frontend
*   **Framework:** Next.js 15 (React 19)
*   **Styling:** Tailwind CSS + Custom CSS Animations
*   **Motion:** Framer Motion (for UI animations)
*   **Particles:** tsparticles (for magical effects)
*   **Real-time:** LiveKit Components (for voice & data streaming)

### Backend (AI Agent)
*   **Runtime:** Python 3.12
*   **Framework:** LiveKit Agents
*   **LLM:** Google Gemini 1.5 Flash
*   **TTS:** Murf AI (Simulated/Integrated via LiveKit plugin)
*   **STT:** Deepgram Nova-2
*   **State Management:** Custom JSON-based game state engine

## 🚀 Getting Started

### Prerequisites
*   Node.js 18+
*   Python 3.10+
*   LiveKit Cloud Account
*   Google AI Studio Key (Gemini)
*   Deepgram API Key
*   Murf AI API Key

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/vedant7007/Murf_ai_day8.git
    cd Murf_ai_day8
    ```

2.  **Setup Backend:**
    ```bash
    cd ten-days-of-voice-agents-2025/backend
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # Mac/Linux
    source .venv/bin/activate
    
    pip install -r requirements.txt
    ```

3.  **Configure Backend Environment:**
    Create `.env.local` in `backend/` with your keys:
    ```env
    LIVEKIT_URL=wss://your-project.livekit.cloud
    LIVEKIT_API_KEY=your_key
    LIVEKIT_API_SECRET=your_secret
    GOOGLE_API_KEY=your_gemini_key
    MURF_API_KEY=your_murf_key
    DEEPGRAM_API_KEY=your_deepgram_key
    ```

4.  **Setup Frontend:**
    ```bash
    cd ../frontend
    npm install
    ```

5.  **Configure Frontend Environment:**
    Create `.env.local` in `frontend/` with your LiveKit keys (for client-side connection):
    ```env
    LIVEKIT_URL=wss://your-project.livekit.cloud
    LIVEKIT_API_KEY=your_key
    LIVEKIT_API_SECRET=your_secret
    ```

### Running the Game

1.  **Start the Backend Agent:**
    ```bash
    # In backend terminal
    python src/agent.py dev
    ```

2.  **Start the Frontend:**
    ```bash
    # In frontend terminal
    npm run dev
    ```

3.  Open `http://localhost:3000` in your browser and click **"Begin Your Quest"**!

## 📸 Screenshots

*(Add screenshots of the Landing Page, Character Sheet, and Dice Roll here)*

## 🤝 Contributing

Contributions are welcome! Feel free to submit a Pull Request.

## 📜 License

This project is licensed under the MIT License.

---
*Built for the 10 Days of Voice Agents Challenge 2025* 🚀