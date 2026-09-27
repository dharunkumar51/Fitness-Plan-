from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


# ---------------------------------------------------------
# Environment
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(
    BASE_DIR / ".env"
)


# ---------------------------------------------------------
# Gemini configuration
# ---------------------------------------------------------

GEMINI_MODEL = os.getenv(
    "GEMINI_WORKOUT_MODEL",
    "gemini-2.5-flash",
)


# ---------------------------------------------------------
# Gemini client
# ---------------------------------------------------------

def _get_gemini_client():

    api_key = os.getenv(
        "GOOGLE_API_KEY",
        "",
    ).strip()

    if not api_key:
        return None

    try:

        from google import genai

        return genai.Client(
            api_key=api_key
        )

    except Exception:

        return None


# ---------------------------------------------------------
# Gemini generation
# ---------------------------------------------------------

def _generate_with_gemini(
    prompt: str,
) -> str | None:

    client = _get_gemini_client()

    if client is None:
        return None

    try:

        from google.genai import types

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=5000,
            ),
        )

        result = getattr(
            response,
            "text",
            None,
        )

        if result:
            return result.strip()

    except Exception:

        return None

    return None


# ---------------------------------------------------------
# Local fallback
# ---------------------------------------------------------

def _fallback_plan(
    username: str,
    age: int,
    weight: float,
    goal: str,
    intensity: str,
) -> str:

    intensity_guidance = {

        "low":
            "Keep the effort comfortable and focus strongly on technique.",

        "medium":
            "Use moderate effort and maintain controlled movement.",

        "high":
            "Use challenging but controlled effort and stop if form breaks down.",
    }

    return f"""
FITBUDDY 7-DAY PERSONALIZED WORKOUT PLAN

Name: {username}
Age: {age}
Weight: {weight:.1f} kg
Goal: {goal}
Intensity: {intensity}

IMPORTANT:
This is general fitness information and is not medical advice.
Stop exercise if you experience pain, dizziness, chest discomfort,
or unusual symptoms.

--------------------------------------------------
DAY 1 — FULL BODY
--------------------------------------------------

Warm-up:
5–10 minutes of walking and mobility.

Workout:

1. Bodyweight Squats
   3 sets × 10–12 reps

2. Incline Push-ups
   3 sets × 8–12 reps

3. Glute Bridges
   3 sets × 12 reps

4. Resistance Band Rows
   3 sets × 10–12 reps

Rest:
60–90 seconds between sets.

Cooldown:
5 minutes gentle stretching.


--------------------------------------------------
DAY 2 — CARDIO + CORE
--------------------------------------------------

Warm-up:
5 minutes easy movement.

Workout:

1. Brisk walking/cycling
   20–30 minutes

2. Dead Bug
   3 sets × 8–10 per side

3. Bird Dog
   3 sets × 8–10 per side

Cooldown:
5 minutes gentle stretching.


--------------------------------------------------
DAY 3 — LOWER BODY
--------------------------------------------------

Warm-up:
5–10 minutes.

Workout:

1. Squats
   3 sets × 10 reps

2. Reverse Lunges
   3 sets × 8 each side

3. Hip Hinge
   3 sets × 10 reps

4. Calf Raises
   3 sets × 12–15 reps

Cooldown:
Gentle lower-body stretching.


--------------------------------------------------
DAY 4 — ACTIVE RECOVERY
--------------------------------------------------

Easy walking:
20–30 minutes.

Mobility:
10 minutes.

Optional:
Gentle yoga.

Keep the intensity easy.


--------------------------------------------------
DAY 5 — UPPER BODY
--------------------------------------------------

Warm-up:
5–10 minutes.

Workout:

1. Push-ups
   3 sets × 8–12 reps

2. Resistance Band Rows
   3 sets × 10–12 reps

3. Shoulder Press
   3 sets × 10 reps

4. Biceps Curls
   2 sets × 12 reps

Cooldown:
5 minutes.


--------------------------------------------------
DAY 6 — FULL BODY + CARDIO
--------------------------------------------------

Warm-up:
5–10 minutes.

Workout:

1. Squats
   3 sets × 10 reps

2. Push-up variation
   3 sets × 8–12 reps

3. Row variation
   3 sets × 10–12 reps

4. Walking/Cycling
   15–20 minutes

Cooldown:
5 minutes.


--------------------------------------------------
DAY 7 — REST & RECOVERY
--------------------------------------------------

Rest from structured training.

Optional:
Easy walking.

Gentle stretching.

Focus on:

- Hydration
- Sleep
- Recovery
- Balanced nutrition


--------------------------------------------------
INTENSITY GUIDANCE
--------------------------------------------------

{intensity_guidance.get(intensity, "Use controlled effort.")}


--------------------------------------------------
PROGRESSION
--------------------------------------------------

Increase repetitions or resistance gradually when
your current workload feels comfortable and controlled.
"""


# ---------------------------------------------------------
# Main generator
# ---------------------------------------------------------

def generate_workout_gemini(
    user,
) -> str:

    prompt = f"""
You are FitBuddy, an AI fitness planning assistant.

Create a personalized 7-day workout plan.

USER INFORMATION

Name: {user.username}
Age: {user.age}
Weight: {user.weight} kg
Goal: {user.goal}
Intensity: {user.intensity}

REQUIREMENTS

1. Create exactly 7 days.

2. Every training day should include:
   - Warm-up
   - Exercises
   - Sets/repetitions or duration
   - Rest guidance
   - Cooldown/recovery

3. Include appropriate recovery/rest days.

4. Adapt the plan to:
   - Goal
   - Age
   - Weight
   - Intensity

5. Use clear headings.

6. Keep the recommendations practical.

7. Do not diagnose medical conditions.

8. Do not prescribe medical treatment.

9. Tell the user to stop if they experience pain
   or unusual symptoms.

10. Return plain text only.

Do not put the response inside a code block.
"""

    ai_result = _generate_with_gemini(
        prompt
    )

    if ai_result:
        return ai_result

    return _fallback_plan(
        username=user.username,
        age=user.age,
        weight=user.weight,
        goal=user.goal,
        intensity=user.intensity,
    )