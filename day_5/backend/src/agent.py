import logging
import json
import os
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

from rag_handler import FAQRetriever

logger = logging.getLogger("agent")

load_dotenv(".env.local")

# Initialize FAQ retriever
FAQ_FILE = Path(__file__).parent.parent / "data" / "company_faq.json"
faq_retriever = FAQRetriever(str(FAQ_FILE))


class SwiggySDRAssistant(Agent):
    def __init__(self) -> None:
        # Initialize lead data storage
        self.lead_data = {
            "name": None,
            "company": None,
            "email": None,
            "role": None,
            "use_case": None,
            "team_size": None,
            "timeline": None,
            "questions_asked": [],
            "conversation_started": datetime.now().isoformat(),
        }

        super().__init__(
            instructions=f"""You are Alex, a friendly and professional Sales Development Representative for Swiggy, India's leading food delivery and quick commerce platform.

## Your Personality
- Warm, enthusiastic, and genuinely helpful
- Professional but conversational
- Excited about helping businesses grow with Swiggy
- You speak naturally like a real person, not a robot

## Your Primary Goals
1. Greet visitors warmly and ask what brought them here
2. Understand their business and what they're working on
3. Answer questions about Swiggy's products, pricing, and services using the FAQ knowledge base
4. Qualify and capture lead information naturally during the conversation
5. Never fabricate information - only use the provided FAQ content

## Company Information
{faq_retriever.get_company_info()}

## Conversation Flow
1. Start with a warm greeting: "Hi! I'm Alex from Swiggy. Thanks for your interest! What brought you here today?"
2. Listen to their needs and ask: "Tell me a bit about your business - what are you currently working on?"
3. Answer their questions using the search_faq tool
4. Naturally collect their information using the capture_lead_info tool as the conversation progresses
5. When they mention readiness to proceed or say they're done, use the complete_conversation tool

## Important Guidelines
- Keep responses to 1-3 sentences maximum
- Ask ONE question at a time
- Never use markdown, lists, code blocks, or special formatting
- Spell out numbers and currency in words
- Never mention that you're using tools or searching for information
- Make the lead capture feel natural, not like a form
- If you don't know something from the FAQ, be honest and offer to connect them with the right team
- Focus on understanding their business needs before pitching

## Lead Qualification
Try to naturally gather:
- Name and company name
- Email address
- Their role
- Their business type and use case
- Team size
- Timeline for getting started (immediate, soon, or later)

Remember: You're having a natural conversation, not conducting an interrogation. Weave these questions naturally into the discussion.""",
        )

    @function_tool
    async def search_faq(self, context: RunContext, query: str):
        """Search the Swiggy FAQ knowledge base to answer questions about products, pricing, and services.

        Use this tool whenever the prospect asks about:
        - What Swiggy offers
        - Pricing and commission structure
        - How to get started or onboarding process
        - Technical details about partnership
        - Any other questions about Swiggy's services

        Args:
            query: The question or topic to search for in the FAQ
        """
        logger.info(f"Searching FAQ for: {query}")

        # Search for relevant FAQ entries
        results = faq_retriever.search(query, top_k=2)

        if not results:
            return "I don't have specific information about that in my knowledge base. Let me connect you with our partnership team who can provide detailed information."

        # Store question in lead data
        self.lead_data["questions_asked"].append(query)

        # Format the top result as a natural response
        top_result = results[0]
        response = top_result['answer']

        # If there's a second relevant result, add brief additional info
        if len(results) > 1 and results[1]['relevance_score'] > 0.3:
            response += f" {results[1]['answer'][:100]}..."

        return response

    @function_tool
    async def capture_lead_info(
        self,
        context: RunContext,
        name: str = None,
        company: str = None,
        email: str = None,
        role: str = None,
        use_case: str = None,
        team_size: str = None,
        timeline: str = None
    ):
        """Capture prospect information during the conversation.

        Use this tool to store lead information as you learn it naturally during the conversation.
        Call this tool whenever the prospect shares any of these details.

        Args:
            name: Prospect's full name
            company: Company or restaurant name
            email: Email address
            role: Their role (owner, manager, founder, etc.)
            use_case: Type of business or what they do (restaurant, cloud kitchen, cafe, etc.)
            team_size: Size of their team or number of employees
            timeline: When they want to start (immediate, soon, later)
        """
        logger.info(f"Capturing lead info - Name: {name}, Company: {company}, Email: {email}")

        # Update lead data with non-None values
        if name:
            self.lead_data["name"] = name
        if company:
            self.lead_data["company"] = company
        if email:
            self.lead_data["email"] = email
        if role:
            self.lead_data["role"] = role
        if use_case:
            self.lead_data["use_case"] = use_case
        if team_size:
            self.lead_data["team_size"] = team_size
        if timeline:
            self.lead_data["timeline"] = timeline

        return "Information captured successfully."

    @function_tool
    async def complete_conversation(self, context: RunContext):
        """Complete the conversation and generate a summary.

        Use this tool when the prospect indicates they're done, satisfied, ready to proceed, or says goodbye.
        Phrases like "that's all", "I'm done", "thanks", "I'll think about it" are completion signals.

        This will generate a verbal summary of the prospect's profile and save the lead data.
        """
        logger.info("Completing conversation and generating summary")

        # Save lead data to file
        self._save_lead_data()

        # Generate summary
        summary = self._generate_summary()

        return f"Here's a quick summary of our conversation: {summary} I've captured all your information and our partnership team will reach out to you soon. Thanks for your interest in Swiggy!"

    def _save_lead_data(self):
        """Save lead data to JSON file"""
        try:
            # Create leads directory if it doesn't exist
            leads_dir = Path(__file__).parent.parent / "data" / "leads"
            leads_dir.mkdir(parents=True, exist_ok=True)

            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"lead_{timestamp}.json"
            filepath = leads_dir / filename

            # Add metadata
            self.lead_data["conversation_ended"] = datetime.now().isoformat()
            self.lead_data["lead_score"] = self._calculate_lead_score()

            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.lead_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Lead data saved to {filepath}")

        except Exception as e:
            logger.error(f"Error saving lead data: {e}")

    def _calculate_lead_score(self) -> str:
        """Calculate lead qualification score"""
        score = 0

        # Check completeness
        if self.lead_data.get("name"):
            score += 1
        if self.lead_data.get("email"):
            score += 2
        if self.lead_data.get("company"):
            score += 1
        if self.lead_data.get("use_case"):
            score += 1

        # Check timeline
        timeline = self.lead_data.get("timeline", "").lower()
        if "immediate" in timeline:
            score += 2
        elif "soon" in timeline:
            score += 1

        # Check engagement
        if len(self.lead_data.get("questions_asked", [])) >= 3:
            score += 1

        # Classify
        if score >= 6:
            return "hot"
        elif score >= 4:
            return "warm"
        else:
            return "cold"

    def _generate_summary(self) -> str:
        """Generate a natural summary of the lead"""
        parts = []

        name = self.lead_data.get("name", "our prospect")
        company = self.lead_data.get("company")
        use_case = self.lead_data.get("use_case")
        timeline = self.lead_data.get("timeline")
        team_size = self.lead_data.get("team_size")

        if company:
            parts.append(f"You're {name} from {company}")
        else:
            parts.append(f"You're {name}")

        if use_case:
            parts.append(f"running a {use_case}")

        if team_size:
            parts.append(f"with a team of about {team_size}")

        if timeline:
            if "immediate" in timeline.lower():
                parts.append("and you're looking to get started right away")
            elif "soon" in timeline.lower():
                parts.append("and you're planning to start soon")
            else:
                parts.append("and you're exploring options for later")

        # Join parts naturally
        if len(parts) <= 1:
            return parts[0] if parts else "Thanks for chatting with us"

        summary = " ".join(parts)
        return summary


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
                voice="en-US-matthew", 
                style="Conversation",
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
        agent=SwiggySDRAssistant(),
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
