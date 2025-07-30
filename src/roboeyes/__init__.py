"""
Core RoboEyes functionality.
"""

from .desktop_roboeyes import DesktopRoboEyes
from .emotion_animation_streamlined import (
    EmotionAnimationManager,
    EmotionConfig,
    EMOTION_HAPPY,
    EMOTION_NEUTRAL,
    EMOTION_URGENT,
    EMOTION_CONCERNED,
    EMOTION_REQUEST,
    VALID_EMOTIONS,
    DEFAULT_EMOTION,
    get_default_emotion_configs
)

__all__ = [
    'DesktopRoboEyes',
    'EmotionAnimationManager',
    'EmotionConfig',
    'EMOTION_HAPPY',
    'EMOTION_NEUTRAL',
    'EMOTION_URGENT',
    'EMOTION_CONCERNED',
    'EMOTION_REQUEST',
    'VALID_EMOTIONS',
    'DEFAULT_EMOTION',
    'get_default_emotion_configs'
]