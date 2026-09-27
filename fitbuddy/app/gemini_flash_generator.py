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
    "GEMINI_TIP_MODEL",
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
# AI nutrition tip
# ---------------------------------------------------------

def _generate_tip(
    goal: str,
) -> str | None:

    client = _get_client()

    if client is None:
        return None

    prompt = f"""
You are FitBuddy's nutrition and recovery assistant.

Fitness goal:
{goal}

Generate one practical nutrition or recovery tip.

Requirements:

- Maximum 80 words.
- Easy to understand.
- General wellness information.
- Do not diagnose diseases.
- Do not prescribe medication.
- Avoid extreme dieting.
- Return plain text only.
"""

    try:

        from google.genai import types

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.5,
                max_output_tokens=250,
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
# Fallback nutrition tips
# ---------------------------------------------------------

def _fallback_tip(
    goal: str,
) -> str:

    tips = {

        "weight loss":
            "Build meals around vegetables, fruit, adequate protein, whole-food carbohydrates, healthy fats, and water. Focus on sustainable habits rather than extreme restriction.",

        "muscle gain":
            "Include a protein-rich food in each main meal and combine it with adequate calories, resistance training, hydration, and consistent sleep.",

        "general wellness":
            "Aim for balanced meals containing vegetables or fruit, protein, whole-food carbohydrates, healthy fats, and regular hydration.",

        "flexibility":
            "Stay hydrated and eat a balanced diet with sufficient protein and nutrient-rich foods to support regular movement and recovery.",

        "fitness":
            "Maintain consistent hydration and include protein and minimally processed whole foods as part of your regular training routine.",
    }

    return tips.get(
        goal,
        tips["fitness"],
    )


# ---------------------------------------------------------
# Public function
# ---------------------------------------------------------

def generate_nutrition_tip_with_flash(
    goal: str,
) -> str:

    result = _generate_tip(
        goal
    )

    if result:
        return result

    return _fallback_tip(
        goal
    )