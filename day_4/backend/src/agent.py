import logging
import json
from pathlib import Path
from typing import Optional

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

# Load content from JSON file
CONTENT_FILE = Path(__file__).parent.parent.parent / "shared-data" / "day4_tutor_content.json"

def load_tutor_content():
    """Load tutor content from JSON file"""
    try:
        with open(CONTENT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load tutor content: {e}")
        return []

TUTOR_CONTENT = load_tutor_content()

def get_concept_by_id(concept_id: str):
    """Get a specific concept by ID"""
    for concept in TUTOR_CONTENT:
        if concept['id'] == concept_id:
            return concept
    return None

def get_all_concept_titles():
    """Get all concept titles for listing"""
    return [f"{c['id']}: {c['title']}" for c in TUTOR_CONTENT]


class TriageAgent(Agent):
    """Main triage agent that greets users and handles mode selection"""

    def __init__(self, chat_ctx=None) -> None:
        concept_list = "\n".join(get_all_concept_titles())

        super().__init__(
            instructions=f"""You are an Active Recall Coach - a friendly tutor who helps students learn through three different modes.

Your role is to greet the user warmly and help them choose their preferred learning mode.

Available learning modes:
1. LEARN mode - I will explain concepts to you in detail
2. QUIZ mode - I will ask you questions to test your understanding
3. TEACH-BACK mode - You will explain concepts back to me (the best way to learn!)

Available concepts:
{concept_list}

Start by greeting the user enthusiastically and asking which learning mode they'd like to start with.
If they're unsure, briefly explain what each mode does and recommend starting with LEARN mode if they're new to a topic.

Keep your responses conversational and encouraging. You're here to make learning fun and effective!

Once the user chooses a mode, use the appropriate transfer tool to connect them to that mode's specialist.
""",
            chat_ctx=chat_ctx
        )

    @function_tool
    async def transfer_to_learn_mode(self, context: RunContext, concept_id: str):
        """Transfer to Learn Mode where concepts are explained to the student.

        Args:
            concept_id: The ID of the concept to learn (e.g., 'variables', 'loops', 'functions')
        """
        concept = get_concept_by_id(concept_id)
        if not concept:
            return None, f"Sorry, I couldn't find that concept. Available concepts: {', '.join([c['id'] for c in TUTOR_CONTENT])}"

        logger.info(f"Transferring to Learn Mode for concept: {concept_id}")
        return LearnModeAgent(concept_id=concept_id, chat_ctx=self.chat_ctx), f"Transferring to Learn Mode to teach you about {concept['title']}..."

    @function_tool
    async def transfer_to_quiz_mode(self, context: RunContext, concept_id: str):
        """Transfer to Quiz Mode where the student is tested on concepts.

        Args:
            concept_id: The ID of the concept to quiz on (e.g., 'variables', 'loops', 'functions')
        """
        concept = get_concept_by_id(concept_id)
        if not concept:
            return None, f"Sorry, I couldn't find that concept. Available concepts: {', '.join([c['id'] for c in TUTOR_CONTENT])}"

        logger.info(f"Transferring to Quiz Mode for concept: {concept_id}")
        return QuizModeAgent(concept_id=concept_id, chat_ctx=self.chat_ctx), f"Transferring to Quiz Mode to test your knowledge on {concept['title']}..."

    @function_tool
    async def transfer_to_teachback_mode(self, context: RunContext, concept_id: str):
        """Transfer to Teach-Back Mode where the student explains concepts back to me.

        Args:
            concept_id: The ID of the concept for teach-back (e.g., 'variables', 'loops', 'functions')
        """
        concept = get_concept_by_id(concept_id)
        if not concept:
            return None, f"Sorry, I couldn't find that concept. Available concepts: {', '.join([c['id'] for c in TUTOR_CONTENT])}"

        logger.info(f"Transferring to Teach-Back Mode for concept: {concept_id}")
        return TeachBackModeAgent(concept_id=concept_id, chat_ctx=self.chat_ctx), f"Transferring to Teach-Back Mode. Get ready to teach me about {concept['title']}!"


class LearnModeAgent(Agent):
    """Learn Mode - Explains concepts using Matthew voice"""

    def __init__(self, concept_id: str, chat_ctx=None) -> None:
        self.concept_id = concept_id
        concept = get_concept_by_id(concept_id)
        concept_list = "\n".join(get_all_concept_titles())

        if not concept:
            concept_info = "Concept not found."
        else:
            concept_info = f"""
Concept: {concept['title']}
Summary: {concept['summary']}
"""

        super().__init__(
            instructions=f"""You are Matthew, a patient and knowledgeable teacher in LEARN MODE.

{concept_info}

Your role:
1. Explain the current concept ({concept['title'] if concept else 'unknown'}) clearly and thoroughly using the summary provided
2. Use examples and analogies to make concepts easy to understand
3. Break down complex ideas into simple, digestible parts
4. Encourage questions and provide detailed answers
5. Check for understanding by asking if things make sense

Available concepts to teach:
{concept_list}

If the student wants to learn a different concept, use the switch_concept tool.
If they want to switch to Quiz mode, use the transfer_to_quiz_mode tool.
If they want to switch to Teach-Back mode, use the transfer_to_teachback_mode tool.
If they want to return to the main menu, use the return_to_triage tool.

Be warm, encouraging, and make learning enjoyable!
""",
            chat_ctx=chat_ctx
        )

    @function_tool
    async def switch_concept(self, context: RunContext, concept_id: str):
        """Switch to learning a different concept in Learn Mode.

        Args:
            concept_id: The ID of the new concept to learn
        """
        concept = get_concept_by_id(concept_id)
        if not concept:
            return None, f"Sorry, I couldn't find that concept. Available: {', '.join([c['id'] for c in TUTOR_CONTENT])}"

        logger.info(f"Switching to concept: {concept_id} in Learn Mode")
        return LearnModeAgent(concept_id=concept_id, chat_ctx=self.chat_ctx), f"Switching to learn about {concept['title']}..."

    @function_tool
    async def transfer_to_quiz_mode(self, context: RunContext, concept_id: Optional[str] = None):
        """Transfer to Quiz Mode to test knowledge.

        Args:
            concept_id: Optional - the concept to quiz on. If not provided, uses current concept.
        """
        cid = concept_id or self.concept_id
        concept = get_concept_by_id(cid)
        logger.info(f"Transferring from Learn to Quiz Mode for: {cid}")
        return QuizModeAgent(concept_id=cid, chat_ctx=self.chat_ctx), f"Let's test your knowledge on {concept['title']}!"

    @function_tool
    async def transfer_to_teachback_mode(self, context: RunContext, concept_id: Optional[str] = None):
        """Transfer to Teach-Back Mode where student explains the concept.

        Args:
            concept_id: Optional - the concept for teach-back. If not provided, uses current concept.
        """
        cid = concept_id or self.concept_id
        concept = get_concept_by_id(cid)
        logger.info(f"Transferring from Learn to Teach-Back Mode for: {cid}")
        return TeachBackModeAgent(concept_id=cid, chat_ctx=self.chat_ctx), f"Now it's your turn! Teach me about {concept['title']}!"

    @function_tool
    async def return_to_triage(self, context: RunContext):
        """Return to the main menu to choose a different mode or concept."""
        logger.info("Returning to Triage from Learn Mode")
        return TriageAgent(chat_ctx=self.chat_ctx), "Returning to main menu..."


class QuizModeAgent(Agent):
    """Quiz Mode - Asks questions using Alicia voice"""

    def __init__(self, concept_id: str, chat_ctx=None) -> None:
        self.concept_id = concept_id
        concept = get_concept_by_id(concept_id)
        concept_list = "\n".join(get_all_concept_titles())

        if not concept:
            concept_info = "Concept not found."
        else:
            concept_info = f"""
Concept: {concept['title']}
Sample Question: {concept['sample_question']}
Summary (for your reference): {concept['summary']}
"""

        super().__init__(
            instructions=f"""You are Alicia, an enthusiastic quiz master in QUIZ MODE!

{concept_info}

Your role:
1. Ask the student questions about {concept['title'] if concept else 'the concept'}
2. Start with the sample question provided, then ask follow-up questions
3. Provide immediate feedback - praise correct answers enthusiastically!
4. For incorrect answers, gently correct and explain the right answer
5. Ask if they'd like more questions or want to switch modes
6. Keep the quiz engaging and encouraging

Available concepts to quiz on:
{concept_list}

If the student wants to be quizzed on a different concept, use the switch_concept tool.
If they want to switch to Learn mode, use the transfer_to_learn_mode tool.
If they want to switch to Teach-Back mode, use the transfer_to_teachback_mode tool.
If they want to return to the main menu, use the return_to_triage tool.

Be energetic, supportive, and make testing fun!
""",
            chat_ctx=chat_ctx
        )

    @function_tool
    async def switch_concept(self, context: RunContext, concept_id: str):
        """Switch to quizzing on a different concept.

        Args:
            concept_id: The ID of the new concept to quiz
        """
        concept = get_concept_by_id(concept_id)
        if not concept:
            return None, f"Sorry, I couldn't find that concept. Available: {', '.join([c['id'] for c in TUTOR_CONTENT])}"

        logger.info(f"Switching to concept: {concept_id} in Quiz Mode")
        return QuizModeAgent(concept_id=concept_id, chat_ctx=self.chat_ctx), f"Let's quiz you on {concept['title']}!"

    @function_tool
    async def transfer_to_learn_mode(self, context: RunContext, concept_id: Optional[str] = None):
        """Transfer to Learn Mode to review concepts.

        Args:
            concept_id: Optional - the concept to learn. If not provided, uses current concept.
        """
        cid = concept_id or self.concept_id
        concept = get_concept_by_id(cid)
        logger.info(f"Transferring from Quiz to Learn Mode for: {cid}")
        return LearnModeAgent(concept_id=cid, chat_ctx=self.chat_ctx), f"Let's review {concept['title']}!"

    @function_tool
    async def transfer_to_teachback_mode(self, context: RunContext, concept_id: Optional[str] = None):
        """Transfer to Teach-Back Mode where student explains the concept.

        Args:
            concept_id: Optional - the concept for teach-back. If not provided, uses current concept.
        """
        cid = concept_id or self.concept_id
        concept = get_concept_by_id(cid)
        logger.info(f"Transferring from Quiz to Teach-Back Mode for: {cid}")
        return TeachBackModeAgent(concept_id=cid, chat_ctx=self.chat_ctx), f"Now teach me about {concept['title']}!"

    @function_tool
    async def return_to_triage(self, context: RunContext):
        """Return to the main menu to choose a different mode or concept."""
        logger.info("Returning to Triage from Quiz Mode")
        return TriageAgent(chat_ctx=self.chat_ctx), "Returning to main menu..."


class TeachBackModeAgent(Agent):
    """Teach-Back Mode - Student explains concepts using Ken voice"""

    def __init__(self, concept_id: str, chat_ctx=None) -> None:
        self.concept_id = concept_id
        concept = get_concept_by_id(concept_id)
        concept_list = "\n".join(get_all_concept_titles())

        if not concept:
            concept_info = "Concept not found."
        else:
            concept_info = f"""
Concept: {concept['title']}
Expected explanation (for evaluation): {concept['summary']}
"""

        super().__init__(
            instructions=f"""You are Ken, a supportive coach in TEACH-BACK MODE!

{concept_info}

Your role:
1. Ask the student to explain {concept['title'] if concept else 'the concept'} back to you in their own words
2. Listen carefully to their explanation
3. Provide qualitative feedback on their explanation:
   - What they got right (be specific!)
   - What they missed or could improve
   - Overall quality of their understanding (excellent/good/needs work)
4. Encourage them to try again if they struggled, or move on if they did well
5. Ask if they want to teach back another concept or switch modes

Available concepts for teach-back:
{concept_list}

Compare their explanation with the expected summary to evaluate accuracy and completeness.

If the student wants to teach a different concept, use the switch_concept tool.
If they want to switch to Learn mode, use the transfer_to_learn_mode tool.
If they want to switch to Quiz mode, use the transfer_to_quiz_mode tool.
If they want to return to the main menu, use the return_to_triage tool.

Remember: Teaching back is the BEST way to learn! Be encouraging even if they struggle.
""",
            chat_ctx=chat_ctx
        )

    @function_tool
    async def evaluate_explanation(self, context: RunContext, user_explanation: str):
        """Evaluate the student's explanation of the concept and provide detailed feedback.

        Args:
            user_explanation: The student's explanation of the concept
        """
        concept = get_concept_by_id(self.concept_id)

        # This is a simple evaluation - could be enhanced with LLM-based scoring
        feedback = f"""
Let me evaluate your explanation of {concept['title']}:

Your explanation: "{user_explanation}"

Expected key points from the summary:
{concept['summary']}

Based on your explanation, here's my feedback:
"""
        logger.info(f"Evaluating explanation for concept: {self.concept_id}")
        return feedback

    @function_tool
    async def switch_concept(self, context: RunContext, concept_id: str):
        """Switch to teaching back a different concept.

        Args:
            concept_id: The ID of the new concept to teach back
        """
        concept = get_concept_by_id(concept_id)
        if not concept:
            return None, f"Sorry, I couldn't find that concept. Available: {', '.join([c['id'] for c in TUTOR_CONTENT])}"

        logger.info(f"Switching to concept: {concept_id} in Teach-Back Mode")
        return TeachBackModeAgent(concept_id=concept_id, chat_ctx=self.chat_ctx), f"Now teach me about {concept['title']}!"

    @function_tool
    async def transfer_to_learn_mode(self, context: RunContext, concept_id: Optional[str] = None):
        """Transfer to Learn Mode to review concepts.

        Args:
            concept_id: Optional - the concept to learn. If not provided, uses current concept.
        """
        cid = concept_id or self.concept_id
        concept = get_concept_by_id(cid)
        logger.info(f"Transferring from Teach-Back to Learn Mode for: {cid}")
        return LearnModeAgent(concept_id=cid, chat_ctx=self.chat_ctx), f"Let's review {concept['title']}!"

    @function_tool
    async def transfer_to_quiz_mode(self, context: RunContext, concept_id: Optional[str] = None):
        """Transfer to Quiz Mode to test knowledge.

        Args:
            concept_id: Optional - the concept to quiz on. If not provided, uses current concept.
        """
        cid = concept_id or self.concept_id
        concept = get_concept_by_id(cid)
        logger.info(f"Transferring from Teach-Back to Quiz Mode for: {cid}")
        return QuizModeAgent(concept_id=cid, chat_ctx=self.chat_ctx), f"Let's test your knowledge on {concept['title']}!"

    @function_tool
    async def return_to_triage(self, context: RunContext):
        """Return to the main menu to choose a different mode or concept."""
        logger.info("Returning to Triage from Teach-Back Mode")
        return TriageAgent(chat_ctx=self.chat_ctx), "Returning to main menu..."


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    # Logging setup
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Get current agent name from room attributes for voice selection
    async def get_tts_for_agent(agent_name: str):
        """Return appropriate TTS configuration based on agent"""
        voice_map = {
            "TriageAgent": "en-US-matthew",
            "LearnModeAgent": "en-US-matthew",
            "QuizModeAgent": "en-US-alicia",
            "TeachBackModeAgent": "en-US-ken"
        }

        voice = voice_map.get(agent_name, "en-US-matthew")
        logger.info(f"Using voice {voice} for agent {agent_name}")

        return murf.TTS(
            voice=voice,
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True
        )

    # Create initial session with TriageAgent
    initial_tts = await get_tts_for_agent("TriageAgent")

    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=initial_tts,
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )

    # Metrics collection
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    # Agent handoff callback to update TTS voice
    @session.on("agent_handoff")
    def _on_agent_handoff(ev):
        """Update TTS voice when agent changes"""
        import asyncio

        new_agent_name = type(ev.agent).__name__
        logger.info(f"Agent handoff to: {new_agent_name}")

        # Update TTS for the new agent in a sync manner
        async def update_voice():
            # Update room attributes to track current agent
            await ctx.room.local_participant.update_attributes({"current_agent": new_agent_name})

            # Update TTS for the new agent
            new_tts = await get_tts_for_agent(new_agent_name)
            session.tts = new_tts

        asyncio.create_task(update_voice())

    # Start with TriageAgent
    await session.start(
        agent=TriageAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
