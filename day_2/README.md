# Day 2: Coffee Shop Barista Agent

This project builds upon the foundation from Day 1, transforming the generic voice agent into a specialized **Coffee Shop Barista**. The agent is designed to simulate a real-world coffee ordering experience through a conversational voice interface.

---

## 🚀 Project Goal

The primary objective for Day 2 is to implement an agent with a distinct persona that can guide a user through the process of ordering a coffee, collect the necessary details, and confirm the order by summarizing it.

### Key Features

*   **Friendly Barista Persona:** The agent adopts a friendly and helpful tone appropriate for a coffee shop environment.
*   **Interactive Order-Taking:** The agent asks clarifying questions to gather all required order details, such as drink type, size, milk, and other extras.
*   **State Management:** It maintains a structured state of the user's order throughout the conversation.
*   **Order Summarization:** Once the order is complete, the agent saves the final order details to a local JSON file, creating a record of the transaction.
*   **(Optional) HTML Visualization:** An advanced, optional feature involves dynamically rendering an HTML representation of the drink or an order receipt based on the user's choices.

---

## 🛠️ Technical Focus

This challenge focuses on leveraging the capabilities of **LiveKit Agents** to:

*   Implement and manage conversational state.
*   Define and execute specific tasks (e.g., saving the order).
*   Integrate custom logic to create a goal-oriented dialogue flow.

The core technologies (Python, Next.js, Murf TTS, Google Gemini) remain the same as in Day 1.

---

## 🏃‍♀️ Setup and Usage

The setup process for this project is identical to Day 1.

1.  **Prerequisites:** Ensure you have all necessary tools and API keys as outlined in the main project `README.md`.
2.  **Detailed Instructions:** For a complete step-by-step guide, please refer to the [SETUP_INSTRUCTIONS.md](./SETUP_INSTRUCTIONS.md) file.
3.  **Running the App:** Start the LiveKit server, the backend agent, and the frontend application in three separate terminals.

Once running, connect to the agent and try ordering a coffee!