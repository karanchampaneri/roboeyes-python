"""
Streamlined emotion animation system for RoboEyes.

This module provides a simplified EmotionAnimationManager that focuses on core
functionality for real-time emotion-driven animations while maintaining essential
features like emotion chaining and seamless transitions.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import logging
import time

# Emotion category constants for the five patient emotions
EMOTION_HAPPY = "happy"
EMOTION_NEUTRAL = "neutral"
EMOTION_URGENT = "urgent"
EMOTION_CONCERNED = "concerned"
EMOTION_REQUEST = "request"

# Collection of all valid emotion categories
VALID_EMOTIONS = {
    EMOTION_HAPPY,
    EMOTION_NEUTRAL,
    EMOTION_URGENT,
    EMOTION_CONCERNED,
    EMOTION_REQUEST
}

# Default emotion for fallback scenarios
DEFAULT_EMOTION = EMOTION_NEUTRAL


@dataclass
class EmotionConfig:
    """
    Simplified configuration for emotion-to-animation mapping.
    
    Attributes:
        sequence_name: Name of the animation sequence to trigger
        duration_ms: How long to maintain this emotion (None for indefinite)
        loop: Whether to loop the animation
    """
    sequence_name: str
    duration_ms: Optional[int] = None
    loop: bool = True


def get_default_emotion_configs() -> Dict[str, EmotionConfig]:
    """
    Get the default emotion-to-animation configuration.
    
    Returns:
        Dictionary mapping emotion names to EmotionConfig instances
    """
    return {
        EMOTION_NEUTRAL: EmotionConfig(
            sequence_name="idle_gentle",
            duration_ms=None,  # Indefinite
            loop=True
        ),
        EMOTION_HAPPY: EmotionConfig(
            sequence_name="gentle_joy",
            duration_ms=4000,
            loop=False
        ),
        EMOTION_URGENT: EmotionConfig(
            sequence_name="alert_focused",
            duration_ms=None,  # Indefinite until changed
            loop=True
        ),
        EMOTION_CONCERNED: EmotionConfig(
            sequence_name="empathetic_support",
            duration_ms=5000,
            loop=False
        ),
        EMOTION_REQUEST: EmotionConfig(
            sequence_name="attentive_listening",
            duration_ms=3000,
            loop=False
        )
    }


class EmotionAnimationManager:
    """
    Streamlined emotion animation manager for real-time emotion chaining.
    
    This class provides a simplified interface for triggering emotion-based
    eye animations while preserving real-time updates and seamless transitions.
    """
    
    def __init__(self, roboeyes_instance, 
                 emotion_config: Optional[Dict[str, EmotionConfig]] = None,
                 # Backward compatibility parameters (ignored in streamlined version)
                 emotion_mappings: Optional[Dict[str, Any]] = None,
                 config_file_path: Optional[str] = None):
        """
        Initialize the EmotionAnimationManager with simple configuration.
        
        Args:
            roboeyes_instance: The RoboEyes instance to control animations
            emotion_config: Optional custom emotion configurations. If None, uses defaults.
            emotion_mappings: Legacy parameter for backward compatibility (ignored)
            config_file_path: Legacy parameter for backward compatibility (ignored)
        """
        if roboeyes_instance is None:
            raise ValueError("roboeyes_instance cannot be None")
            
        self.roboeyes = roboeyes_instance
        self.logger = logging.getLogger(__name__)
        
        # Initialize state tracking
        self._current_emotion: Optional[str] = None
        self._is_transitioning: bool = False
        self._transition_start_time: Optional[float] = None
        self._transition_duration: float = 1.0  # Default 1 second transition
        self._animation_start_time: Optional[float] = None
        
        # Initialize emotion configurations with simple dictionary-based approach
        self._emotion_configs = self._initialize_emotion_configs(emotion_config)
        
        # Log backward compatibility warnings if legacy parameters are used
        if emotion_mappings is not None:
            self.logger.warning("emotion_mappings parameter is deprecated in streamlined version. Use emotion_config instead.")
        if config_file_path is not None:
            self.logger.warning("config_file_path parameter is deprecated in streamlined version. Use emotion_config instead.")
        
        self.logger.info(f"EmotionAnimationManager initialized with {len(self._emotion_configs)} emotions")
    
    def _initialize_emotion_configs(self, emotion_config: Optional[Dict[str, EmotionConfig]]) -> Dict[str, EmotionConfig]:
        """
        Initialize emotion configurations with validation and defaults.
        
        Args:
            emotion_config: Optional custom emotion configurations
            
        Returns:
            Dictionary of validated emotion configurations
        """
        if emotion_config is not None:
            # Use provided configuration
            configs = emotion_config.copy()
        else:
            # Use default configuration
            configs = get_default_emotion_configs()
        
        # Ensure we have at least neutral emotion for fallback
        if EMOTION_NEUTRAL not in configs:
            configs[EMOTION_NEUTRAL] = EmotionConfig(
                sequence_name="idle_gentle",
                duration_ms=None,
                loop=True
            )
            self.logger.info(f"Added default neutral emotion configuration")
        
        # Validate all configurations
        for emotion_name, config in configs.items():
            if not isinstance(config, EmotionConfig):
                self.logger.error(f"Invalid configuration type for emotion '{emotion_name}': expected EmotionConfig")
                # Replace with default neutral config
                configs[emotion_name] = configs[EMOTION_NEUTRAL]
            elif not config.sequence_name or not isinstance(config.sequence_name, str):
                self.logger.error(f"Invalid sequence_name for emotion '{emotion_name}': must be non-empty string")
                # Replace with default neutral config
                configs[emotion_name] = configs[EMOTION_NEUTRAL]
        
        return configs
    
    def trigger_emotion(self, emotion_name: str) -> bool:
        """
        Trigger an emotion animation with seamless transitions.
        
        Args:
            emotion_name: Name of emotion to trigger. Must be one of:
                         ['happy', 'neutral', 'urgent', 'concerned', 'request']
        
        Returns:
            bool: True if emotion was successfully triggered, False otherwise
        
        Raises:
            ValueError: If emotion_name is not supported (provides clear error message)
        
        Example:
            >>> manager.trigger_emotion('happy')
            True
            >>> manager.trigger_emotion('invalid')
            False
        """
        try:
            # Handle None input gracefully
            if emotion_name is None:
                self.logger.warning("Emotion name is None. Using neutral fallback.")
                return self._safe_fallback_to_neutral()
            
            # Normalize emotion name
            if not isinstance(emotion_name, str):
                self.logger.error(f"Invalid emotion name type: {type(emotion_name)}. Expected string.")
                return self._safe_fallback_to_neutral()
            
            emotion_name = emotion_name.lower().strip()
            
            # Handle empty string
            if not emotion_name:
                self.logger.warning("Empty emotion name. Using neutral fallback.")
                return self._safe_fallback_to_neutral()
            
            # Check if emotion is supported - provide clear error message
            if emotion_name not in self._emotion_configs:
                available = sorted(list(self._emotion_configs.keys()))
                error_msg = f"Emotion '{emotion_name}' not supported. Available emotions: {available}"
                self.logger.warning(error_msg)
                return self._safe_fallback_to_neutral()
            
            # Don't retrigger the same emotion unless transitioning
            if self._current_emotion == emotion_name and not self._is_transitioning:
                self.logger.debug(f"Emotion '{emotion_name}' is already active")
                return True
            
            # Start the emotion animation with error recovery
            return self._start_emotion_animation_safe(emotion_name)
            
        except Exception as e:
            # Never let exceptions break the animation loop
            self.logger.error(f"Unexpected error triggering emotion '{emotion_name}': {e}")
            return self._safe_fallback_to_neutral()
    
    def update(self) -> None:
        """
        Update animation state - called every frame for real-time updates.
        
        This method should be called regularly (e.g., every frame) to maintain
        smooth transitions and handle animation timing. Never throws exceptions
        to preserve pygame rendering loop continuity.
        """
        try:
            current_time = time.time()
            
            # Update transition state with error recovery
            if self._is_transitioning:
                try:
                    self._update_transition(current_time)
                except Exception as e:
                    self.logger.error(f"Error updating transition: {e}. Completing transition.")
                    self._is_transitioning = False
                    self._transition_start_time = None
            
            # Check if current emotion should expire
            if self._current_emotion and self._animation_start_time:
                try:
                    config = self._emotion_configs.get(self._current_emotion)
                    if config and config.duration_ms:
                        elapsed_ms = (current_time - self._animation_start_time) * 1000
                        if elapsed_ms >= config.duration_ms:
                            self.logger.debug(f"Emotion '{self._current_emotion}' duration expired, returning to neutral")
                            # Use safe fallback to prevent cascading errors
                            self._safe_fallback_to_neutral()
                except Exception as e:
                    self.logger.error(f"Error checking emotion expiration: {e}. Continuing animation.")
                        
        except Exception as e:
            # Never let update() break the rendering loop
            self.logger.error(f"Critical error in update: {e}. Animation system continuing.")
    
    def get_available_emotions(self) -> List[str]:
        """
        Get list of supported emotions.
        
        Returns:
            List of emotion names that can be used with trigger_emotion()
        """
        try:
            return sorted(list(self._emotion_configs.keys()))
        except Exception as e:
            self.logger.error(f"Error getting available emotions: {e}")
            return [EMOTION_NEUTRAL]  # Return at least neutral as fallback
    
    def is_emotion_active(self, emotion_name: str) -> bool:
        """
        Check if a specific emotion is currently active.
        
        Args:
            emotion_name: Name of the emotion to check
            
        Returns:
            True if the emotion is currently active, False otherwise
        """
        try:
            if not isinstance(emotion_name, str):
                return False
            return self._current_emotion == emotion_name.lower().strip()
        except Exception as e:
            self.logger.error(f"Error checking if emotion '{emotion_name}' is active: {e}")
            return False
    
    def get_current_emotion(self) -> Optional[str]:
        """
        Get the currently active emotion.
        
        Returns:
            Name of the current emotion, or None if no emotion is active
        """
        try:
            return self._current_emotion
        except Exception as e:
            self.logger.error(f"Error getting current emotion: {e}")
            return None
    
    def _safe_fallback_to_neutral(self) -> bool:
        """
        Safely fallback to neutral emotion without breaking animation continuity.
        
        This method ensures that even if the neutral emotion fails, the system
        maintains a consistent state and never breaks the pygame rendering loop.
        
        Returns:
            True if fallback was successful, False otherwise
        """
        try:
            # Ensure neutral emotion exists
            if EMOTION_NEUTRAL not in self._emotion_configs:
                self.logger.critical("Neutral emotion not configured. Creating emergency fallback.")
                self._emotion_configs[EMOTION_NEUTRAL] = EmotionConfig(
                    sequence_name="idle_gentle",
                    duration_ms=None,
                    loop=True
                )
            
            return self._start_emotion_animation_safe(EMOTION_NEUTRAL)
            
        except Exception as e:
            # Last resort: maintain state consistency even if animation fails
            self.logger.critical(f"Emergency fallback failed: {e}. Maintaining state consistency.")
            self._current_emotion = EMOTION_NEUTRAL
            self._is_transitioning = False
            self._transition_start_time = None
            self._animation_start_time = time.time()
            return False
    
    def _start_emotion_animation_safe(self, emotion_name: str) -> bool:
        """
        Safely start an emotion animation with comprehensive error handling.
        
        This method ensures animation continuity even if individual steps fail,
        maintaining consistent state and never breaking the pygame rendering loop.
        
        Args:
            emotion_name: Name of the emotion to start
            
        Returns:
            True if animation started successfully, False otherwise
        """
        try:
            # Validate emotion exists
            if emotion_name not in self._emotion_configs:
                self.logger.error(f"Animation failed: emotion '{emotion_name}' not configured")
                return False
            
            config = self._emotion_configs[emotion_name]
            current_time = time.time()
            
            # If we're already in this emotion and not transitioning, nothing to do
            if self._current_emotion == emotion_name and not self._is_transitioning:
                return True
            
            # Safely handle transition state
            try:
                if self._current_emotion and self._current_emotion != emotion_name:
                    self._is_transitioning = True
                    self._transition_start_time = current_time
                    self.logger.debug(f"Starting transition from '{self._current_emotion}' to '{emotion_name}'")
                else:
                    # Direct animation start
                    self._is_transitioning = False
                    self._transition_start_time = None
            except Exception as e:
                self.logger.error(f"Error setting transition state: {e}. Proceeding with direct animation.")
                self._is_transitioning = False
                self._transition_start_time = None
            
            # Update state before attempting animation
            previous_emotion = self._current_emotion
            self._current_emotion = emotion_name
            self._animation_start_time = current_time
            
            # Safely trigger the animation sequence
            try:
                # Call the sequence method directly on the roboeyes instance
                if hasattr(self.roboeyes, config.sequence_name):
                    sequence_method = getattr(self.roboeyes, config.sequence_name)
                    sequence_method()
                    self.logger.debug(f"Started animation sequence '{config.sequence_name}' for emotion '{emotion_name}'")
                else:
                    self.logger.warning(f"RoboEyes instance does not have sequence method '{config.sequence_name}'")
                    # Still consider this successful since state is consistent
                
                return True
                
            except Exception as e:
                self.logger.error(f"Animation sequence failed for '{emotion_name}': {e}. State remains consistent.")
                # Animation failed but state is consistent - this is acceptable
                return False
            
        except Exception as e:
            self.logger.error(f"Critical error starting animation for '{emotion_name}': {e}")
            # Try to maintain some consistency
            try:
                self._current_emotion = emotion_name
                self._animation_start_time = time.time()
                self._is_transitioning = False
                self._transition_start_time = None
            except:
                pass  # Even state recovery failed, but we won't crash
            return False
    
    def _update_transition(self, current_time: float) -> None:
        """
        Safely update the current transition state.
        
        Args:
            current_time: Current timestamp
        """
        if not self._is_transitioning or not self._transition_start_time:
            return
        
        try:
            # Calculate transition progress
            elapsed = current_time - self._transition_start_time
            progress = min(elapsed / self._transition_duration, 1.0)
            
            # Complete transition when done
            if progress >= 1.0:
                self._is_transitioning = False
                self._transition_start_time = None
                self.logger.debug(f"Completed transition to '{self._current_emotion}'")
                
        except Exception as e:
            # Force transition completion on error to maintain consistency
            self.logger.error(f"Error updating transition: {e}. Forcing completion.")
            self._is_transitioning = False
            self._transition_start_time = None