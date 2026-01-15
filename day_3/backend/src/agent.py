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


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions='''You are WellBot, an enthusiastic and supportive Health & Wellness Voice Companion. You help users with fitness, nutrition, mental health, and overall wellness.
            
Your personality: Motivating, empathetic, and knowledgeable. You celebrate small wins and encourage healthy habits.

Your capabilities:
- Suggest personalized workouts based on fitness level and goals
- Provide nutrition advice and meal suggestions
- Calculate BMI and daily calorie needs
- Track water intake and remind users to stay hydrated
- Offer mental health support and mindfulness exercises
- Give sleep hygiene tips and track sleep quality
- Create custom fitness plans

Keep responses conversational, encouraging, and actionable. No complex formatting, emojis, or asterisks.
Remember: You're talking via voice, so keep it natural and friendly!''',
        )

    @function_tool
    async def suggest_workout(self, context: RunContext, fitness_level: str, goal: str, duration: str):
        """Suggest a personalized workout routine based on user's fitness level, goal, and available time.
        
        Args:
            fitness_level: User's fitness level (beginner, intermediate, advanced)
            goal: Fitness goal (weight_loss, muscle_gain, endurance, flexibility, general_fitness)
            duration: Available workout time (15min, 30min, 45min, 60min)
        """
        
        logger.info(f"Suggesting workout: level={fitness_level}, goal={goal}, duration={duration}")
        
        workouts = {
            "beginner": {
                "weight_loss": f"{duration} cardio: 10min warm-up walk, 20min light jogging intervals, 10min cool-down stretches",
                "muscle_gain": f"{duration} bodyweight: 3 sets of push-ups, squats, lunges, planks with 60sec rest",
                "flexibility": f"{duration} yoga flow: Sun salutations, warrior poses, gentle stretches",
                "general_fitness": f"{duration} mixed routine: 15min cardio, 15min bodyweight exercises, 10min stretching"
            },
            "intermediate": {
                "weight_loss": f"{duration} HIIT: 5min warm-up, 25min high-intensity intervals, burpees, mountain climbers, jump squats",
                "muscle_gain": f"{duration} strength: Weighted squats, deadlifts, bench press, rows - 4 sets each",
                "endurance": f"{duration} cardio: Steady-state running or cycling with progressive intensity",
                "general_fitness": f"{duration} circuit: Mix of cardio bursts and strength exercises, 3 rounds"
            },
            "advanced": {
                "weight_loss": f"{duration} advanced HIIT: Explosive plyometrics, sprint intervals, complex movements",
                "muscle_gain": f"{duration} hypertrophy: Heavy compound lifts with accessory work, 5 sets progressive overload",
                "endurance": f"{duration} performance: Tempo runs, interval training, endurance building protocols",
                "general_fitness": f"{duration} athlete training: Olympic lifts, plyometrics, core work, mobility"
            }
        }
        
        level = fitness_level.lower()
        goal_key = goal.lower().replace(" ", "_")
        
        if level in workouts and goal_key in workouts[level]:
            return f"Perfect! Here's your {duration} {goal} workout for {fitness_level} level: {workouts[level][goal_key]}"
        else:
            return f"I suggest a balanced {duration} routine mixing cardio and strength training for your {goal} goal!"

    @function_tool
    async def calculate_bmi(self, context: RunContext, weight_kg: float, height_cm: float):
        """Calculate BMI and provide health category.
        
        Args:
            weight_kg: User's weight in kilograms
            height_cm: User's height in centimeters
        """
        
        logger.info(f"Calculating BMI: weight={weight_kg}kg, height={height_cm}cm")
        
        height_m = height_cm / 100
        bmi = weight_kg / (height_m ** 2)
        
        if bmi < 18.5:
            category = "underweight"
            advice = "Focus on nutrient-dense foods and strength training to build healthy mass"
        elif 18.5 <= bmi < 25:
            category = "healthy weight"
            advice = "Great job! Maintain your current lifestyle with balanced nutrition and regular exercise"
        elif 25 <= bmi < 30:
            category = "overweight"
            advice = "Consider increasing physical activity and focusing on portion control"
        else:
            category = "obese"
            advice = "I recommend consulting a healthcare provider for a personalized wellness plan"
        
        return f"Your BMI is {bmi:.1f}, which is in the {category} range. {advice}"

    @function_tool
    async def nutrition_advice(self, context: RunContext, meal_type: str, dietary_preference: str, goal: str):
        """Provide meal suggestions based on meal type, dietary preferences, and health goals.
        
        Args:
            meal_type: Type of meal (breakfast, lunch, dinner, snack)
            dietary_preference: Dietary preference (vegetarian, vegan, non_veg, keto, balanced)
            goal: Health goal (weight_loss, muscle_gain, energy_boost, general_health)
        """
        
        logger.info(f"Nutrition advice: {meal_type}, {dietary_preference}, goal={goal}")
        
        meals = {
            "breakfast": {
                "weight_loss": "Greek yogurt with berries and chia seeds, or scrambled eggs with spinach and tomatoes",
                "muscle_gain": "Protein pancakes with peanut butter and banana, or oatmeal with whey protein and nuts",
                "energy_boost": "Whole grain toast with avocado and eggs, or smoothie bowl with fruits and granola",
                "general_health": "Balanced plate with whole grains, protein, and fresh fruits"
            },
            "lunch": {
                "weight_loss": "Grilled chicken salad with olive oil dressing, or quinoa bowl with roasted vegetables",
                "muscle_gain": "Chicken breast with brown rice and broccoli, or salmon with sweet potato",
                "energy_boost": "Whole wheat wrap with lean protein and veggies, or Mediterranean bowl",
                "general_health": "Balanced meal with lean protein, complex carbs, and colorful vegetables"
            },
            "dinner": {
                "weight_loss": "Grilled fish with steamed vegetables, or vegetable stir-fry with tofu",
                "muscle_gain": "Lean beef with quinoa and green beans, or turkey meatballs with whole wheat pasta",
                "energy_boost": "Salmon with roasted sweet potato and asparagus",
                "general_health": "Well-balanced dinner with protein, healthy fats, and fiber-rich vegetables"
            },
            "snack": {
                "weight_loss": "Apple slices with almond butter, or carrot sticks with hummus",
                "muscle_gain": "Protein shake with banana, or cottage cheese with nuts",
                "energy_boost": "Trail mix with nuts and dried fruits, or energy balls",
                "general_health": "Fresh fruits, nuts, or yogurt"
            }
        }
        
        meal_key = meal_type.lower()
        goal_key = goal.lower().replace(" ", "_")
        
        if meal_key in meals and goal_key in meals[meal_key]:
            suggestion = meals[meal_key][goal_key]
            if dietary_preference.lower() in ["vegetarian", "vegan"]:
                suggestion = suggestion.replace("chicken", "tofu").replace("fish", "chickpeas").replace("beef", "lentils")
            return f"For {meal_type} with your {goal} goal, I suggest: {suggestion}"
        else:
            return f"For a healthy {meal_type}, focus on balanced portions with lean protein, whole grains, and plenty of vegetables!"

    @function_tool
    async def water_reminder(self, context: RunContext, weight_kg: float, activity_level: str):
        """Calculate daily water intake recommendation based on weight and activity level.
        
        Args:
            weight_kg: User's weight in kilograms
            activity_level: Activity level (sedentary, moderate, active, very_active)
        """
        
        logger.info(f"Water reminder: weight={weight_kg}kg, activity={activity_level}")
        
        # Base calculation: 30-35ml per kg of body weight
        base_water = weight_kg * 0.033  # liters
        
        activity_multipliers = {
            "sedentary": 1.0,
            "moderate": 1.2,
            "active": 1.5,
            "very_active": 1.8
        }
        
        multiplier = activity_multipliers.get(activity_level.lower(), 1.0)
        recommended_liters = base_water * multiplier
        glasses = int(recommended_liters * 4)  # 250ml per glass
        
        return f"Based on your weight and {activity_level} activity level, drink about {recommended_liters:.1f} liters or {glasses} glasses of water daily. Set reminders every 2 hours!"

    @function_tool
    async def mindfulness_exercise(self, context: RunContext, stress_level: str, duration: str):
        """Provide a mindfulness or breathing exercise based on stress level and available time.
        
        Args:
            stress_level: Current stress level (low, moderate, high, very_high)
            duration: Available time (5min, 10min, 15min, 20min)
        """
        
        logger.info(f"Mindfulness exercise: stress={stress_level}, duration={duration}")
        
        exercises = {
            "low": "Try a gratitude meditation: Close your eyes, take deep breaths, and think of 3 things you're grateful for today",
            "moderate": "Box breathing: Inhale for 4 counts, hold 4, exhale 4, hold 4. Repeat for the duration",
            "high": "Progressive muscle relaxation: Tense and release each muscle group from toes to head, focusing on the sensation of relaxation",
            "very_high": "Guided body scan: Lie down, close your eyes, and slowly bring awareness to each part of your body from feet to head, releasing tension"
        }
        
        exercise = exercises.get(stress_level.lower(), exercises["moderate"])
        
        return f"Perfect, let's do a {duration} mindfulness exercise. {exercise}. Remember to breathe deeply and be present in the moment."

    @function_tool
    async def sleep_tips(self, context: RunContext, sleep_quality: str, hours_slept: float):
        """Provide personalized sleep hygiene tips based on sleep quality and duration.
        
        Args:
            sleep_quality: Recent sleep quality (poor, fair, good, excellent)
            hours_slept: Average hours of sleep per night
        """
        
        logger.info(f"Sleep tips: quality={sleep_quality}, hours={hours_slept}")
        
        if hours_slept < 6:
            duration_advice = "You're not getting enough sleep. Aim for 7-9 hours. Try going to bed 30 minutes earlier each week."
        elif hours_slept < 7:
            duration_advice = "You're close! Try adding another hour to reach the optimal 7-9 hour range."
        elif hours_slept <= 9:
            duration_advice = "Great job on getting adequate sleep duration!"
        else:
            duration_advice = "You might be oversleeping. Stick to 7-9 hours for optimal health."
        
        quality_tips = {
            "poor": "Create a bedtime routine: No screens 1 hour before bed, keep room cool and dark, try chamomile tea",
            "fair": "Improve consistency: Go to bed and wake up at the same time daily, even on weekends",
            "good": "Fine-tune your environment: Use blackout curtains, white noise, and keep bedroom temperature around 65-68F",
            "excellent": "You're doing great! Maintain your current sleep routine and continue prioritizing rest"
        }
        
        quality_advice = quality_tips.get(sleep_quality.lower(), quality_tips["fair"])
        
        return f"{duration_advice} {quality_advice}"

    # Original weather tool kept as example
    # @function_tool
    # async def lookup_weather(self, context: RunContext, location: str):
    #     logger.info(f"Looking up weather for {location}")
    #     return "sunny with a temperature of 70 degrees."


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(
                model="gemini-2.5-flash",
            ),
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
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm, agent_name="WellBot"))

