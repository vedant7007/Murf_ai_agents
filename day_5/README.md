# Day 5: AI Sales Development Representative (SDR)

This project develops the voice agent into an **AI Sales Development Representative (SDR)**. The agent is designed to engage with potential customers, answer common questions about a chosen company/product, and efficiently capture crucial lead information.

---

## 🚀 Project Goal

The primary objective for Day 5 is to build a functional SDR agent that can autonomously handle initial customer inquiries and qualify leads. This involves adopting a professional persona, accessing a knowledge base, and intelligently extracting user data.

### Key Features

*   **Custom SDR Persona:** The agent is configured to act as a friendly and focused SDR for a specified company (e.g., an Indian startup), aiming to understand the user's needs.
*   **FAQ Answering:** It can answer basic product, company, and pricing questions by querying a loaded knowledge base (e.g., a text or JSON file of FAQs).
*   **Intelligent Lead Capture:** The agent naturally asks for and collects key lead details such as name, company, email, role, use case, team size, and timeline, storing this information incrementally in a JSON file.
*   **End-of-Call Summary:** Upon detecting the end of a conversation, the agent provides a brief verbal summary of the captured lead and saves the complete lead profile to a JSON file.
*   **(Optional) Advanced SDR Capabilities:** Optional challenges include implementing a mock meeting scheduler, generating CRM-style call notes, persona-aware pitching, drafting follow-up emails, and recognizing returning visitors.

---

## 🛠️ Technical Focus

This challenge emphasizes agent design for real-world business applications:

*   **Prompt Engineering:** Crafting effective prompts to define the SDR persona and guide conversational flow.
*   **Knowledge Retrieval:** Implementing a basic system to retrieve answers from a FAQ knowledge base.
*   **Structured Data Collection:** Designing the agent to extract and store specific pieces of information in a structured JSON format.
*   **Conditional Logic:** Managing conversation turns to ensure all necessary lead fields are collected before summarizing.

---

## 🏃‍♀️ Setup and Usage

The core setup for this project remains consistent with previous days.

1.  **Prerequisites:** Ensure all necessary tools and API keys are configured.
2.  **Company Content:** Prepare your chosen Indian company's FAQ and basic information in a suitable format (text/JSON) for the agent to use.
3.  **Detailed Instructions:** For a complete step-by-step guide on setting up the base project, please refer to the `SETUP_INSTRUCTIONS.md` file located in the `day_1` directory.
4.  **Running the App:** Start the LiveKit server, the backend agent, and the frontend application in three separate terminals.

Once running, engage with the SDR agent by asking company-related questions and providing lead information.