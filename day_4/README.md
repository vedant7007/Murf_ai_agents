# Day 4: Active Recall Coach

This project transforms the voice agent into a **"Teach-the-Tutor" Active Recall Coach**. The agent facilitates a dynamic learning experience based on the principle that teaching is the best way to learn. It guides the user through various concepts using distinct modes for learning, quizzing, and teaching back.

---

## 🚀 Project Goal

The objective for Day 4 is to create a multi-persona learning agent that can switch between different teaching styles. The agent uses a predefined set of concepts from a JSON file and interacts with the user to help them achieve mastery.

### Key Features

*   **Three Learning Modes:** The agent operates in one of three modes, each with a unique voice and purpose:
    1.  **Learn Mode:** The agent explains a concept to the user.
    2.  **Quiz Mode:** The agent tests the user's knowledge with questions.
    3.  **Teach-Back Mode:** The agent prompts the user to explain the concept in their own words, providing qualitative feedback.
*   **Content-Driven:** All learning materials (summaries, questions) are loaded from an external `day4_tutor_content.json` file, allowing for easy content updates without changing the agent's code.
*   **Dynamic Mode Switching:** The user can switch between learning modes at any point during the conversation.
*   **(Optional) Concept Mastery:** Advanced, optional features include tracking user scores per concept, evaluating teach-back explanations, and creating personalized learning paths.

---

## 🛠️ Technical Focus

This challenge introduces more advanced agent architecture concepts:

*   **Separation of Content and Logic:** Using a JSON file in the `shared-data` directory to manage the agent's knowledge base.
*   **Agent Handoffs:** Implementing logic that allows the agent to switch between different "personas" or modes (learn, quiz, teach-back) seamlessly within a single session.
*   **Stateful Interactions:** Managing the user's current learning mode and selected concept throughout the conversation.

---

## 🏃‍♀️ Setup and Usage

The setup process for this project is identical to the previous days.

1.  **Prerequisites:** Ensure you have all necessary tools and API keys.
2.  **Detailed Instructions:** For a complete step-by-step guide, please refer to the `SETUP_INSTRUCTIONS.md` file located in the `day_1` directory.
3.  **Running the App:** Start the LiveKit server, the backend agent, and the frontend application in three separate terminals.

Once running, you can start your learning session with the Active Recall Coach!