"""
Nutrition helper module for FitBuddy.

The actual AI nutrition generation is handled by
gemini_flash_generator.py.
"""

from .gemini_flash_generator import (
    generate_nutrition_tip_with_flash,
)


__all__ = [
    "generate_nutrition_tip_with_flash",
]