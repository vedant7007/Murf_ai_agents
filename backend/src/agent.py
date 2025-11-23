import logging

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

# Coffee Shop Menu
MENU = {
    "espresso": 3.00,
    "americano": 3.50,
    "cappuccino": 4.50,
    "latte": 4.50,
    "mocha": 5.00,
    "cold_brew": 4.00,
}

current_order = {}


@function_tool
async def add_to_order(context: RunContext, item: str, size: str = "") -> str:
    """Add a coffee drink to the customer's order. IMPORTANT: Always confirm the size with the customer before calling this function.

    Args:
        item: The coffee drink name (e.g., 'latte', 'cappuccino')
        size: Size of the drink ('small', 'medium', 'large') - REQUIRED, do not use default
    """
    item = item.lower().replace(" ", "_")

    if item not in MENU:
        available_items = [i.replace('_', ' ').title() for i in MENU.keys()]
        return f"Sorry, we don't have {item.replace('_', ' ')}. We have: {', '.join(available_items)}"

    # Validate size is provided
    valid_sizes = ["small", "medium", "large"]
    if not size or size.lower() not in valid_sizes:
        return f"I need to know what size you'd like for your {item.replace('_', ' ')}. Would you like a small, medium, or large?"

    size = size.lower()
    order_id = len(current_order) + 1
    current_order[order_id] = {"item": item, "size": size, "price": MENU[item]}
    return f"Great! I've added a {size} {item.replace('_', ' ')} to your order for ${MENU[item]:.2f}."


@function_tool
async def get_menu(context: RunContext) -> str:
    """Get the coffee shop menu with prices."""
    menu_items = []
    for item, price in MENU.items():
        menu_items.append(f"{item.replace('_', ' ').title()} for ${price:.2f}")

    menu_text = "Here's our menu: " + ", ".join(menu_items[:-1])
    if len(menu_items) > 1:
        menu_text += f", and {menu_items[-1]}."
    else:
        menu_text += f"{menu_items[0]}."
    menu_text += " All drinks are available in small, medium, or large sizes."
    return menu_text


@function_tool
async def get_order(context: RunContext) -> str:
    """Get the current order summary with total price."""
    if not current_order:
        return "Your cart is empty. Would you like to order something?"

    summary = "Your Order:\n"
    total = 0
    for order_id, order in current_order.items():
        summary += f"{order_id}. {order['size']} {order['item']} - ${order['price']:.2f}\n"
        total += order['price']
    summary += f"\nTotal: ${total:.2f}"
    return summary


@function_tool
async def confirm_order(context: RunContext) -> str:
    """Confirm and place the customer's order."""
    if not current_order:
        return "You haven't added anything to your order yet."

    order_count = len(current_order)
    total = sum(item['price'] for item in current_order.values())
    current_order.clear()
    return f"Perfect! Your order of {order_count} item(s) totaling ${total:.2f} has been placed. It will be ready in about 5 minutes. Thank you!"


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a friendly and helpful coffee shop barista named Prashant. Your goal is to provide excellent customer service.

            IMPORTANT RULES:
            1. ALWAYS greet customers warmly when they first connect
            2. Offer to show the menu if they seem unsure what to order
            3. When a customer asks about the menu, use the get_menu tool to show all available drinks
            4. CRITICAL: ALWAYS ask for the drink size (small, medium, or large) if the customer doesn't specify it
            5. Never add items to an order without confirming the size first
            6. After adding items, offer to add more or proceed to checkout
            7. Be conversational and natural - this is a voice interaction

            WORKFLOW:
            - Customer mentions a drink without size → Ask "What size would you like - small, medium, or large?"
            - Customer provides both drink and size → Add to order immediately
            - Customer asks "what do you have" or "menu" → Use get_menu tool
            - Customer says "that's all" or "checkout" → Use get_order to summarize, then confirm_order

            Keep responses brief, friendly, and conversational for natural speech.""",
            tools=[add_to_order, get_menu, get_order, confirm_order]
        )


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    # Logging setup
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="en-US-matthew", 
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )

    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    await session.start(
        agent=Assistant(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(
        entrypoint_fnc=entrypoint,
        prewarm_fnc=prewarm,
        agent_name="Prashant"
    ))