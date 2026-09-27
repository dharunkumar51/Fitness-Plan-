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


GEMINI_MODEL = os.getenv(
    "GEMINI_WORKOUT_MODEL",
    "gemini-2.5-flash",
)


# ---------------------------------------------------------
# Gemini client
# ---------------------------------------------------------

def _get_client():

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
# Update plan
# ---------------------------------------------------------

def update_workout_plan(
    user,
    original_plan: str,
    feedback: str,
) -> str:

    client = _get_client()

    if client is not None:

        prompt = f"""
You are FitBuddy.

Update an existing 7-day fitness plan according to user feedback.

USER

Name: {user.username}
Age: {user.age}
Weight: {user.weight} kg
Goal: {user.goal}
Intensity: {user.intensity}

CURRENT PLAN

{original_plan}

USER FEEDBACK

{feedback}

INSTRUCTIONS

1. Keep exactly 7 days.

2. Preserve useful parts of the current plan.

3. Apply the user's requested changes where reasonable.

4. Keep warm-up guidance.

5. Keep exercises and sets/repetitions or duration.

6. Keep rest and recovery guidance.

7. Respect the user's selected goal and intensity.

8. Do not recommend exercising through pain.

9. Do not diagnose medical conditions.

10. Return only the updated plain-text plan.

Do not use a code block.
"""

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
            pass

    # -----------------------------------------------------
    # Fallback
    # -----------------------------------------------------

    return f"""
{original_plan}

==================================================
UPDATED USING USER FEEDBACK
==================================================

User requested:

{feedback}

==================================================

The AI service was unavailable, so the original
plan has been preserved. Please review the feedback
and adjust the plan manually if necessary.
"""