# Day 6: AI-Powered Fraud Case Management

This project, distinct in its structure from previous days, shifts focus to a more backend-centric application of AI agents: **Fraud Case Management**. It explores how AI agents can assist in querying, analyzing, and potentially updating fraud-related data, leveraging advanced AI models and the Model Context Protocol (MCP).

---

## 🚀 Project Goal

While a specific `Day 6 Task.md` is not provided, the presence of `fraud_cases.db` and a strong emphasis on "coding agents and MCP" suggests the primary goal is to:

*   Develop an AI agent capable of interacting with a `fraud_cases.db` database.
*   The agent should be able to query, summarize, and potentially assist in the management or analysis of fraud cases.
*   It likely involves integrating advanced LLMs (e.g., Claude, Gemini) and utilizing MCP for tool-assisted interactions, moving towards more complex, domain-specific AI applications.

---

## 🛠️ Technical Focus

This day's challenge highlights:

*   **Backend-Heavy Agent Design:** Unlike previous projects with dedicated frontends, this project is primarily focused on the agent's backend logic and interaction capabilities.
*   **Database Interaction:** Working with SQLite databases (`fraud_cases.db`) from within the Python agent to retrieve and process structured data.
*   **Integration with Advanced LLMs:** The project structure (mentioning `CLAUDE.md`, `GEMINI.md`) implies exploration or integration with different Large Language Models for varied agent behaviors and insights.
*   **Model Context Protocol (MCP):** Emphasizing the use of MCP for agent-IDE collaboration and tool integration, potentially for tasks like code generation or automated analysis based on database queries.

---

## 🏃‍♀️ Setup and Usage

The setup follows the standard LiveKit Agents Python project structure.

1.  **Prerequisites:** Ensure you have all necessary tools and API keys. The `uv` package manager is used for dependency management.
2.  **Database Setup:** The `fraud_cases.db` is central to this project. Refer to `setup_database.py` to understand its structure and how data is populated.
3.  **Detailed Instructions:** Refer to `AGENTS.md` and the general `SETUP_INSTRUCTIONS.md` (if available in `day_1`) for setup specifics.
4.  **Running the Agent:** The agent can likely be run in console mode or dev mode using `uv run python src/agent.py console` or `uv run python src/agent.py dev`.

Once the agent is running, interact with it to explore and manage the fraud cases within the database.