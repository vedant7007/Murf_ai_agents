import logging
import sqlite3

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
    llm,
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("fraud-agent")

load_dotenv(".env.local")

# Global state for fraud case tracking
current_case_data = {}
verified_users = {}


# Database helper functions
def get_fraud_case_by_name(user_name: str):
    """Fetch fraud case from database by user name"""
    try:
        conn = sqlite3.connect('fraud_cases.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM fraud_cases
            WHERE LOWER(user_name) = LOWER(?)
            AND status = 'pending_review'
            LIMIT 1
        ''', (user_name,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None
    except Exception as e:
        logger.error(f"Database error: {e}")
        return None


def update_fraud_case_status(case_id: int, status: str, outcome_note: str = ""):
    """Update fraud case status in database"""
    try:
        conn = sqlite3.connect('fraud_cases.db')
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE fraud_cases
            SET status = ?, outcome_note = ?
            WHERE id = ?
        ''', (status, outcome_note, case_id))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Database update error: {e}")
        return False


class FraudAlertAssistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a professional fraud alert agent for SecureBank Fraud Department. You are calling customers about suspicious transactions on their accounts.

CONVERSATION FLOW:
1. Greet the customer professionally and introduce yourself as calling from SecureBank Fraud Department
2. Ask for the customer's full name to look up their case
3. Use the lookup_fraud_case tool to fetch their fraud case details
4. Ask them the security question from the database to verify their identity
5. Use the verify_security_answer tool to check their answer
6. If verified, read out the suspicious transaction details: amount, merchant name, location, transaction time, and last 4 digits of card
7. Ask clearly: "Did you authorize this transaction?" - wait for yes or no answer
8. Use the update_case_status tool to record their response
9. Thank them and end the call professionally

IMPORTANT RULES:
- Keep responses concise and professional
- Speak naturally like a bank fraud department agent
- Do not use emojis, asterisks, or special formatting
- Always verify identity before sharing transaction details
- Be reassuring and professional throughout
- If user cannot be verified, politely end the call without sharing details
- Use the tools provided to fetch and update case information""",
        )
        self.session_id = None

    def _get_session_id(self):
        """Generate a unique session ID for this conversation"""
        if not self.session_id:
            import time
            self.session_id = str(int(time.time() * 1000))
        return self.session_id

    @llm.function_tool()
    async def lookup_fraud_case(self, user_name: str) -> str:
        """Look up a fraud case in the database by customer name. Use this after getting the customer's name.

        Args:
            user_name: The full name of the customer to look up

        Returns:
            A message indicating whether the case was found and next steps
        """
        logger.info(f"Looking up fraud case for: {user_name}")

        case = get_fraud_case_by_name(user_name)
        session_id = self._get_session_id()

        if case:
            current_case_data[session_id] = case
            verified_users[session_id] = False
            return f"Case found for {case['user_name']}. Security identifier: {case['security_identifier']}. Ask them the security question: {case['security_question']}"
        else:
            return f"No pending fraud case found for {user_name}. Please verify the name and try again, or inform the customer there may be an error."

    @llm.function_tool()
    async def verify_security_answer(self, customer_answer: str) -> str:
        """Verify the customer's security answer. Use this after they answer the security question.

        Args:
            customer_answer: The answer provided by the customer to the security question

        Returns:
            Transaction details if verified, or failure message
        """
        session_id = self._get_session_id()

        if session_id not in current_case_data:
            return "No case is currently loaded. Please look up the customer first."

        case = current_case_data[session_id]
        logger.info(f"Verifying security answer for case ID: {case['id']}")

        correct_answer = case['security_answer'].lower().strip()
        provided_answer = customer_answer.lower().strip()

        if correct_answer == provided_answer:
            verified_users[session_id] = True
            return f"Verification successful. Provide the transaction details: A transaction of {case['transaction_amount']} rupees at {case['transaction_name']} in {case['transaction_location']} on {case['transaction_time']} using card ending in {case['card_ending']}. Source: {case['transaction_source']}. Ask if they authorized this transaction."
        else:
            verified_users[session_id] = False
            update_fraud_case_status(
                case['id'],
                'verification_failed',
                'Customer failed security verification'
            )
            return "Verification failed. For security reasons, end the call politely and ask them to contact the bank directly."

    @llm.function_tool()
    async def update_case_status(self, customer_authorized: bool) -> str:
        """Update the fraud case status after getting customer's response about the transaction.

        Args:
            customer_authorized: True if customer says they made the transaction, False if they did not

        Returns:
            Confirmation message with next steps to tell the customer
        """
        session_id = self._get_session_id()

        if session_id not in current_case_data:
            return "No case is currently loaded."

        if not verified_users.get(session_id, False):
            return "Customer has not been verified yet. Cannot update case status."

        case = current_case_data[session_id]
        logger.info(f"Updating case ID {case['id']} - Customer authorized: {customer_authorized}")

        if customer_authorized:
            status = 'confirmed_safe'
            note = 'Customer confirmed they authorized the transaction'
            message = "Case updated as safe transaction. Thank the customer and let them know no further action is needed."
        else:
            status = 'confirmed_fraud'
            note = 'Customer confirmed they did NOT authorize the transaction - card blocked'
            message = "Case updated as fraud. Inform customer their card will be blocked immediately and a new card will be issued within 5-7 business days. Thank them for their time."

        success = update_fraud_case_status(case['id'], status, note)

        if success:
            return message
        else:
            return "There was an error updating the case. Apologize to the customer and ask them to contact the bank directly."


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    # Logging setup
    # Add any other context you want in all log entries here
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Set up a voice AI pipeline using Murf, Deepgram, Google Gemini, and the LiveKit turn detector
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

    # Start the session, which initializes the voice pipeline and warms up the models
    await session.start(
        agent=FraudAlertAssistant(),
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
