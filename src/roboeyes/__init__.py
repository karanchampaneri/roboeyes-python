"""
Core RoboEyes functionality.
"""

from .desktop_roboeyes import DesktopRoboEyes
from .emotion_animation import (
    AnimationConfig,
    EMOTION_HAPPY,
    EMOTION_NEUTRAL,
    EMOTION_URGENT,
    EMOTION_CONCERNED,
    EMOTION_REQUEST,
    VALID_EMOTIONS,
    DEFAULT_EMOTION,
    validate_animation_config,
    validate_emotion_name,
    validate_emotion_mapping,
    get_default_emotion_mapping
)

__all__ = [
    'DesktopRoboEyes',
    'AnimationConfig',
    'EMOTION_HAPPY',
    'EMOTION_NEUTRAL',
    'EMOTION_URGENT',
    'EMOTION_CONCERNED',
    'EMOTION_REQUEST',
    'VALID_EMOTIONS',
    'DEFAULT_EMOTION',
    'validate_animation_config',
    'validate_emotion_name',
    'validate_emotion_mapping',
    'get_default_emotion_mapping'
]