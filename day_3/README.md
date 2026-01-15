# Day 3: Health & Wellness Voice Companion

This project evolves the voice agent into a **Health & Wellness Companion**. The agent acts as a supportive, non-clinical companion that performs daily check-ins on the user's mood and goals, persisting the conversation history to inform future interactions.

---

## 🚀 Project Goal

The objective for Day 3 is to create a voice agent that can build context over time. It conducts short, daily check-ins, saves the key takeaways to a JSON file, and uses that data to provide a more personalized experience in the next session.

### Key Features

*   **Supportive Companion Persona:** The agent is designed to be a grounded, supportive listener, avoiding clinical or medical advice.
*   **Daily Check-ins:** It asks about the user's mood, energy levels, and daily intentions in a conversational manner.
*   **JSON-based Persistence:** The agent saves a summary of each check-in (mood, goals, date) to a `wellness_log.json` file.
*   **Contextual Conversations:** It reads the `wellness_log.json` at the start of a new session to recall past conversations (e.g., "Last time we spoke, you wanted to focus on [goal]. How is that going?").
*   **(Optional) Advanced Integrations:** Optional goals include connecting the agent to external services like Notion or Todoist via MCP (Model Context Protocol) to create tasks from goals, or performing weekly mood analysis from the log file.

---

## 🛠️ Technical Focus

This challenge introduces a key concept in agent development: **persistence**. The technical focus is on:

*   Using Python's file I/O to read from and write to a JSON file.
*   Maintaining long-term memory for the agent across different sessions.
*   Structuring the agent's logic to retrieve historical context at the beginning of a conversation.

---

## 🏃‍♀️ Setup and Usage

The setup process for this project is identical to the previous days.

1.  **Prerequisites:** Ensure you have all necessary tools and API keys.
2.  **Detailed Instructions:** For a complete step-by-step guide, please refer to the `SETUP_INSTRUCTIONS.md` file located in the `day_1` directory.
3.  **Running the App:** Start the LiveKit server, the backend agent, and the frontend application in three separate terminals.

Once running, you can start your daily check-in with your new wellness companion!