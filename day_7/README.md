# Day 7: Food & Grocery Ordering Voice Agent

This project develops an advanced voice agent functioning as a **Food & Grocery Ordering Shopping Assistant**. It allows users to verbally build and manage a shopping cart, culminating in a placed order that is saved digitally.

---

## 🚀 Project Goal

The primary objective for Day 7 is to create an intelligent and interactive shopping assistant. The agent should be able to understand complex ordering requests, manage a dynamic shopping cart, and finalize orders for persistence.

### Key Features

*   **Customizable Catalog:** Utilizes a custom JSON catalog of food and grocery items, complete with categories, prices, and optional attributes, allowing for flexible product offerings.
*   **Intuitive Ordering Persona:** The agent adopts a friendly persona, guiding users through the ordering process and seeking clarifications when necessary (e.g., quantity, brand).
*   **Dynamic Cart Management:** Implements robust cart functionality, enabling users to add, remove, update quantities, and view items in their current order.
*   **Intelligent "Ingredients For X" Requests:** Capable of interpreting high-level requests (e.g., "ingredients for a sandwich") and automatically adding multiple relevant items to the cart.
*   **Order Placement & Persistence:** Detects user completion, confirms the final order details verbally, and then saves the complete order (items, quantities, total, timestamp) to a JSON file.
*   **(Optional) Advanced Shopping Features:** Optional challenges include developing a mock order tracking system, maintaining historical order records, supporting multiple concurrent orders, offering smart reorder/recommendation functionalities, and implementing budget or dietary constraint-aware ordering.

---

## 🛠️ Technical Focus

This challenge delves into more sophisticated conversational design and data handling:

*   **Conversational State Management:** Efficiently managing the state of the user's shopping cart throughout a multi-turn conversation.
*   **Data-Driven Agent Logic:** Using a JSON catalog to dynamically populate product information and guide the agent's responses.
*   **Intent Recognition for Bundles:** Implementing logic to map natural language requests for ingredient bundles to specific catalog items.
*   **External Data Persistence:** Writing structured order data to JSON files for record-keeping and potential future retrieval (e.g., order history).

---

## 🏃‍♀️ Setup and Usage

The core setup for this project aligns with the previous days.

1.  **Prerequisites:** Ensure all necessary tools and API keys are configured.
2.  **Catalog Preparation:** Create your custom food/grocery catalog as a JSON file, defining items and their properties.
3.  **Detailed Instructions:** For comprehensive setup steps, please refer to the `SETUP_INSTRUCTIONS.md` file located in the `day_1` directory.
4.  **Running the App:** Start the LiveKit server, the backend agent, and the frontend application in three separate terminals.

Once the agent is running, interact with it to experience a voice-powered food and grocery shopping journey!