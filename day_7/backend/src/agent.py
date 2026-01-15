import logging
import json
import os
import random
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    RoomInputOptions,
    WorkerOptions,
    cli,
    metrics,
    tokenize,
    function_tool,
    RunContext
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")

load_dotenv(".env.local")

# Data paths
DATA_DIR = Path(__file__).parent / "data"
CATALOG_PATH = DATA_DIR / "catalog.json"
ORDERS_PATH = DATA_DIR / "orders.json"

# Load catalog
with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    CATALOG = json.load(f)

# Session cart and offers (in production, use Redis or database)
cart = {}
applied_coupon = None

# Available offers
OFFERS = {
    "FIRST50": {"type": "percent", "value": 50, "max_discount": 100, "description": "50% off up to ₹100 on first order"},
    "MAGGI20": {"type": "percent", "value": 20, "max_discount": 50, "description": "20% off on Maggi products", "category": "maggi"},
    "SNACK15": {"type": "percent", "value": 15, "max_discount": 30, "description": "15% off on snacks"},
    "FREE99": {"type": "free_delivery", "min_order": 199, "description": "Free delivery on orders above ₹199"}
}

# Delivery partners
DELIVERY_PARTNERS = ["Raju", "Amit", "Priya", "Vikram", "Sneha", "Rohan", "Divya", "Karan"]
DARK_STORES = ["Hitech City", "Banjara Hills", "Madhapur", "Jubilee Hills", "Gachibowli", "Kondapur"]

# Helper function for fuzzy search
def fuzzy_search_items(query: str):
    """Search items with fuzzy matching - exact, contains, tags, aliases"""
    query_lower = query.lower().strip()
    exact_matches = []
    contains_matches = []
    tag_matches = []

    # Check aliases first
    aliases = CATALOG.get("aliases", {})
    if query_lower in aliases:
        # Expand query to include all aliases
        search_terms = [query_lower] + aliases[query_lower]
    else:
        search_terms = [query_lower]

    for category_name, items in CATALOG["categories"].items():
        for item in items:
            item_name_lower = item["name"].lower()
            item_tags = [tag.lower() for tag in item["tags"]]

            # Check each search term
            for term in search_terms:
                # Exact match
                if term == item_name_lower:
                    exact_matches.append(item)
                    break
                # Contains match
                elif term in item_name_lower or item_name_lower in term:
                    contains_matches.append(item)
                    break
                # Tag match
                elif any(term in tag or tag in term for tag in item_tags):
                    tag_matches.append(item)
                    break
                # Category match
                elif term in category_name.lower():
                    tag_matches.append(item)
                    break

    # Remove duplicates while preserving order
    all_results = []
    seen_ids = set()
    for match_list in [exact_matches, contains_matches, tag_matches]:
        for item in match_list:
            if item["id"] not in seen_ids:
                all_results.append(item)
                seen_ids.add(item["id"])

    return all_results


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are Swigepto - a super fun and witty voice assistant for food and grocery ordering in India!
            You're a fusion of Swiggy and Zepto - delivering happiness faster than your ex's reply!

            GREETING: When user first connects, give a funny, energetic greeting like:
            "Areyy! Finally you showed up! I was getting bored waiting here. Welcome to Swigepto - where food arrives faster than your Wi-Fi loads! I can help you browse groceries, snacks, ready-to-eat food, suggest ingredients for recipes, manage your cart, apply killer offers, and get your order delivered in 10-15 mins! So tell me boss, what's your tummy craving today?"

            IMPORTANT: Always respond in ENGLISH ONLY. Never use Hindi or any other language. You are a voice assistant - speak only in English with an Indian accent.

            YOUR PERSONALITY:
            - Funny, witty, energetic like talking to a fun friend
            - Use casual Indian English: "Ekdum fresh!", "Coming right up boss!", "Sorted!", "Perfect yaar!", "No worries!"
            - Keep responses SUPER SHORT for voice - 1-2 sentences max
            - Crack small jokes occasionally
            - Be enthusiastic and helpful
            - Never boring or robotic

            YOUR CAPABILITIES:
            - Browse 40+ items: groceries, snacks, prepared food
            - Smart recipe helper: "I need stuff for pasta" adds all ingredients automatically!
            - Manage cart: add, remove, update quantities
            - Show offers and apply coupons (FIRST50, MAGGI20, etc.)
            - Place orders with delivery info
            - Track orders and view history

            CONVERSATION FLOW:
            1. Start with funny greeting + intro capabilities
            2. Help browse: "Want snacks? Groceries? Or ingredients for a recipe?"
            3. Add items with enthusiasm: "Added 2 Maggi! Your cart is now ₹28. Anything else boss?"
            4. Suggest offers when cart has items: "Psst! Use FIRST50 for 50% off!"
            5. When placing order: show cart, suggest offers, get address, confirm with fun message
            6. Fun goodbye: "Your order is racing to you! Come back soon!"

            Always confirm actions briefly. Prices are in rupees. No emojis or formatting.
            Remember: ENGLISH ONLY, SHORT responses, FUN personality!""",
        )

    @function_tool
    async def search_catalog(self, context: RunContext, query: str):
        """Search for items in the catalog by name, category, or tags.

        Args:
            query: Search term (e.g., "bread", "snacks", "maggi", "pizza", "chips", "biryani")
        """
        logger.info(f"Searching catalog for: {query}")
        results = fuzzy_search_items(query)

        if results:
            # Limit to top 5 results for voice
            top_results = results[:5]
            items_str = ", ".join([f"{r['name']} (₹{r['price']})" for r in top_results])
            more_msg = f" and {len(results) - 5} more" if len(results) > 5 else ""
            return f"Found {len(results)} items: {items_str}{more_msg}. Want to add any?"

        # If no results, suggest similar categories
        suggestions = ["snacks like chips or maggi", "prepared food like biryani or pizza", "groceries like bread or milk"]
        return f"Hmm, couldn't find '{query}' boss. Try {random.choice(suggestions)}?"

    @function_tool
    async def add_to_cart(self, context: RunContext, item_name: str, quantity: int = 1):
        """Add an item to the cart by name or search term.

        Args:
            item_name: Name or search term for the item (e.g., "lays", "chips", "biryani", "maggi")
            quantity: Quantity to add (default 1)
        """
        logger.info(f"Adding to cart: {item_name} x {quantity}")

        # Use fuzzy search to find item
        search_results = fuzzy_search_items(item_name)

        if not search_results:
            return f"Oops! Couldn't find '{item_name}'. Try searching for snacks, groceries, or prepared food first?"

        # Take the first/best match
        found_item = search_results[0]

        # If multiple matches, mention them
        suggestions = ""
        if len(search_results) > 1:
            other_items = [item["name"] for item in search_results[1:3]]
            suggestions = f" We also have {', '.join(other_items)}."

        # Add to cart
        item_id = found_item["id"]
        if item_id in cart:
            cart[item_id]["quantity"] += quantity
        else:
            cart[item_id] = {
                "name": found_item["name"],
                "price": found_item["price"],
                "unit": found_item["unit"],
                "quantity": quantity
            }

        total_qty = cart[item_id]["quantity"]
        cart_total = sum(item["price"] * item["quantity"] for item in cart.values())

        responses = [
            f"Done! Added {quantity} {found_item['name']}. Cart total is now ₹{cart_total}.{suggestions}",
            f"Perfect! {found_item['name']} x{quantity} added. Cart is ₹{cart_total} now.{suggestions}",
            f"Sorted! {found_item['name']} in cart. Total: ₹{cart_total}. Anything else?",
        ]
        return random.choice(responses)

    @function_tool
    async def remove_from_cart(self, context: RunContext, item_name: str):
        """Remove an item completely from the cart.

        Args:
            item_name: Name of the item to remove
        """
        logger.info(f"Removing from cart: {item_name}")

        # Find and remove item
        for item_id, cart_item in list(cart.items()):
            if cart_item["name"].lower() == item_name.lower():
                del cart[item_id]
                return f"Removed {cart_item['name']} from cart."

        return f"'{item_name}' not in cart."

    @function_tool
    async def update_cart_quantity(self, context: RunContext, item_name: str, quantity: int):
        """Update the quantity of an item in the cart.

        Args:
            item_name: Name of the item
            quantity: New quantity (use 0 to remove)
        """
        logger.info(f"Updating cart: {item_name} to quantity {quantity}")

        # Find item in cart
        for item_id, cart_item in cart.items():
            if cart_item["name"].lower() == item_name.lower():
                if quantity == 0:
                    del cart[item_id]
                    return f"Removed {cart_item['name']} from cart."
                else:
                    cart[item_id]["quantity"] = quantity
                    return f"Updated {cart_item['name']} to {quantity} units."

        return f"'{item_name}' not in cart."

    @function_tool
    async def view_cart(self, context: RunContext):
        """View all items in the cart with total price."""
        logger.info("Viewing cart")

        if not cart:
            return "Your cart is empty boss! Let's fill it up with some goodies. What are you craving?"

        total = 0
        items_list = []
        for cart_item in cart.values():
            item_total = cart_item["price"] * cart_item["quantity"]
            total += item_total
            items_list.append(f"{cart_item['name']} x{cart_item['quantity']} = ₹{item_total}")

        cart_summary = ". ".join(items_list)

        # Suggest offers if cart has items
        offer_hint = ""
        if total > 0 and not applied_coupon:
            offer_hint = " Psst! Check offers for discounts!"
        elif applied_coupon:
            offer_hint = f" {applied_coupon} coupon applied!"

        return f"Your cart: {cart_summary}. Total: ₹{total}.{offer_hint}"

    @function_tool
    async def get_ingredients_for(self, context: RunContext, dish_name: str):
        """Get all ingredients needed for a recipe and add them to cart.

        Args:
            dish_name: Name of the dish (e.g., "pasta", "sandwich", "maggi", "omelette")
        """
        logger.info(f"Getting ingredients for: {dish_name}")

        dish_lower = dish_name.lower()
        if dish_lower not in CATALOG["recipes"]:
            available = ", ".join(CATALOG["recipes"].keys())
            return f"Don't have recipe for '{dish_name}'. Try: {available}."

        recipe = CATALOG["recipes"][dish_lower]
        ingredient_ids = recipe["ingredients"]
        added_items = []

        # Find and add each ingredient
        for ingredient_id in ingredient_ids:
            for category_items in CATALOG["categories"].values():
                for item in category_items:
                    if item["id"] == ingredient_id:
                        # Add to cart
                        if ingredient_id in cart:
                            cart[ingredient_id]["quantity"] += 1
                        else:
                            cart[ingredient_id] = {
                                "name": item["name"],
                                "price": item["price"],
                                "unit": item["unit"],
                                "quantity": 1
                            }
                        added_items.append(item["name"])
                        break

        items_str = ", ".join(added_items)
        return f"Added ingredients for {dish_name}: {items_str}. Check your cart!"

    @function_tool
    async def list_category(self, context: RunContext, category: str):
        """List all items in a specific category.

        Args:
            category: Category name (e.g., "snacks", "groceries", "prepared food", "food")
        """
        logger.info(f"Listing category: {category}")

        category_lower = category.lower().strip()

        # Map common queries to category names
        category_map = {
            "snack": "snacks",
            "snacks": "snacks",
            "grocery": "groceries",
            "groceries": "groceries",
            "prepared food": "prepared_food",
            "food": "prepared_food",
            "ready to eat": "prepared_food",
        }

        actual_category = category_map.get(category_lower, category_lower.replace(" ", "_"))

        if actual_category not in CATALOG["categories"]:
            return f"Sorry boss, don't have category '{category}'. Try snacks, groceries, or prepared food?"

        items = CATALOG["categories"][actual_category]

        # Group by type for better voice readability
        item_names = [f"{item['name']} (₹{item['price']})" for item in items[:8]]
        more_msg = f" and {len(items) - 8} more items" if len(items) > 8 else ""

        return f"We have {len(items)} items in {category}: " + ", ".join(item_names) + more_msg + ". Want to add any?"

    @function_tool
    async def check_offers(self, context: RunContext):
        """Show all available offers and discounts."""
        logger.info("Checking offers")

        offers_list = []
        for code, offer in OFFERS.items():
            offers_list.append(f"{code} - {offer['description']}")

        return "Awesome offers for you! " + ". ".join(offers_list) + ". Use apply_coupon to grab these deals!"

    @function_tool
    async def apply_coupon(self, context: RunContext, coupon_code: str):
        """Apply a coupon code to get discount on cart.

        Args:
            coupon_code: Coupon code to apply (e.g., FIRST50, MAGGI20)
        """
        global applied_coupon
        logger.info(f"Applying coupon: {coupon_code}")

        coupon_upper = coupon_code.upper()
        if coupon_upper not in OFFERS:
            available = ", ".join(OFFERS.keys())
            return f"Sorry boss, {coupon_code} is not valid. Try these: {available}"

        applied_coupon = coupon_upper
        offer = OFFERS[coupon_upper]
        return f"Yay! Applied {coupon_upper} - {offer['description']}. You'll save money when you checkout!"

    @function_tool
    async def get_delivery_info(self, context: RunContext):
        """Get delivery information including ETA, delivery partner, and store location."""
        logger.info("Getting delivery info")

        partner = random.choice(DELIVERY_PARTNERS)
        store = random.choice(DARK_STORES)

        return f"Delivery in 10-15 minutes from Swigepto Dark Store, {store}. Your delivery partner will be {partner}. Fast and fresh, guaranteed!"

    @function_tool
    async def place_order(self, context: RunContext, delivery_address: str):
        """Place the order with current cart items.

        Args:
            delivery_address: Delivery address (e.g., "Flat 101, Hitech City")
        """
        global applied_coupon
        logger.info("Placing order")

        if not cart:
            return "Your cart is empty boss! Add some items first."

        # Calculate subtotal
        subtotal = sum(item["price"] * item["quantity"] for item in cart.values())
        discount = 0
        delivery_fee = 0

        # Apply coupon discount if any
        if applied_coupon:
            offer = OFFERS[applied_coupon]
            if offer["type"] == "percent":
                discount = min((subtotal * offer["value"]) // 100, offer["max_discount"])
            elif offer["type"] == "free_delivery":
                if subtotal >= offer["min_order"]:
                    delivery_fee = 0
                else:
                    delivery_fee = 20

        # Check free delivery
        if subtotal >= 199 and delivery_fee == 0:
            delivery_msg = "FREE delivery"
        else:
            delivery_fee = 20 if subtotal < 199 else 0
            delivery_msg = f"₹{delivery_fee} delivery fee" if delivery_fee > 0 else "FREE delivery"

        total = subtotal - discount + delivery_fee

        # Random delivery partner and store
        partner = random.choice(DELIVERY_PARTNERS)
        store = random.choice(DARK_STORES)

        # Create order
        order_id = f"SWP{datetime.now().strftime('%Y%m%d%H%M%S')}"
        order = {
            "order_id": order_id,
            "timestamp": datetime.now().isoformat(),
            "items": list(cart.values()),
            "subtotal": subtotal,
            "discount": discount,
            "delivery_fee": delivery_fee,
            "total": total,
            "coupon": applied_coupon,
            "delivery_address": delivery_address,
            "delivery_partner": partner,
            "store": store,
            "status": "confirmed"
        }

        # Save to orders.json
        with open(ORDERS_PATH, "r+", encoding="utf-8") as f:
            orders_data = json.load(f)
            orders_data["orders"].append(order)
            f.seek(0)
            json.dump(orders_data, f, indent=2)
            f.truncate()

        # Clear cart and coupon
        cart.clear()
        applied_coupon = None

        discount_msg = f" You saved ₹{discount}!" if discount > 0 else ""
        return f"Boom! Order placed! Order ID: {order_id}. Total: ₹{total}.{discount_msg} {partner} is zooming from {store} to {delivery_address}. ETA: 10-15 mins. Your food is racing to you!"

    @function_tool
    async def track_order(self, context: RunContext, order_id: str):
        """Track the status of an order.

        Args:
            order_id: Order ID to track
        """
        logger.info(f"Tracking order: {order_id}")

        with open(ORDERS_PATH, "r", encoding="utf-8") as f:
            orders_data = json.load(f)

        for order in orders_data["orders"]:
            if order["order_id"] == order_id:
                return f"Order {order_id} is {order['status']}. Total: ₹{order['total']}."

        return f"Order {order_id} not found. Check your order ID?"

    @function_tool
    async def view_order_history(self, context: RunContext):
        """View past orders."""
        logger.info("Viewing order history")

        with open(ORDERS_PATH, "r", encoding="utf-8") as f:
            orders_data = json.load(f)

        orders = orders_data["orders"]
        if not orders:
            return "No previous orders. Place your first order today!"

        recent_orders = orders[-3:]  # Last 3 orders
        order_list = []
        for order in recent_orders:
            order_list.append(f"{order['order_id']} - ₹{order['total']} - {order['status']}")

        return f"Your recent orders: " + ", ".join(order_list)


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    # Logging setup
    # Add any other context you want in all log entries here
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Set up a voice AI pipeline using OpenAI, Cartesia, AssemblyAI, and the LiveKit turn detector
    session = AgentSession(
        # Speech-to-text (STT) is your agent's ears, turning the user's speech into text that the LLM can understand
        # See all available models at https://docs.livekit.io/agents/models/stt/
        stt=deepgram.STT(model="nova-3"),
        # A Large Language Model (LLM) is your agent's brain, processing user input and generating a response
        # See all available models at https://docs.livekit.io/agents/models/llm/
        llm=google.LLM(
                model="gemini-2.5-flash",
            ),
        # Text-to-speech (TTS) is your agent's voice, turning the LLM's text into speech that the user can hear
        # See all available models as well as voice selections at https://docs.livekit.io/agents/models/tts/
        tts=murf.TTS(
                voice="en-IN-priya",
                style="Conversational",
                tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
                text_pacing=True
            ),
        # VAD and turn detection are used to determine when the user is speaking and when the agent should respond
        # See more at https://docs.livekit.io/agents/build/turns
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        # allow the LLM to generate a response while waiting for the end of turn
        # See more at https://docs.livekit.io/agents/build/audio/#preemptive-generation
        preemptive_generation=True,
    )

    # To use a realtime model instead of a voice pipeline, use the following session setup instead.
    # (Note: This is for the OpenAI Realtime API. For other providers, see https://docs.livekit.io/agents/models/realtime/))
    # 1. Install livekit-agents[openai]
    # 2. Set OPENAI_API_KEY in .env.local
    # 3. Add `from livekit.plugins import openai` to the top of this file
    # 4. Use the following session setup instead of the version above
    # session = AgentSession(
    #     llm=openai.realtime.RealtimeModel(voice="marin")
    # )

    # Metrics collection, to measure pipeline performance
    # For more information, see https://docs.livekit.io/agents/build/metrics/
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    # # Add a virtual avatar to the session, if desired
    # # For other providers, see https://docs.livekit.io/agents/models/avatar/
    # avatar = hedra.AvatarSession(
    #   avatar_id="...",  # See https://docs.livekit.io/agents/models/avatar/plugins/hedra
    # )
    # # Start the avatar and wait for it to join
    # await avatar.start(session, room=ctx.room)

    # Start the session, which initializes the voice pipeline and warms up the models
    await session.start(
        agent=Assistant(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            # For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
