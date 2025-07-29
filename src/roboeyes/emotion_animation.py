"""
Core emotion animation data structures for RoboEyes.

This module provides the foundational data structures and constants for the
emotion-driven animation system, including configuration classes, emotion
categories, and validation functions.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import logging
import json
import os
import time
import threading
from pathlib import Path
from typing import Callable

# Emotion category constants for the five patient emotions
# These correspond to the emotions returned by the AI emotion detection service
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
class AnimationConfig:
    """
    Configuration class that defines how an emotion maps to specific animations.
    
    This dataclass encapsulates all the parameters needed to configure how
    a specific emotion should be animated, including the animation sequence,
    timing, and behavior settings.
    
    Attributes:
        sequence_name: Name of the animation sequence to trigger
        mood: RoboEyes mood constant (DEFAULT, HAPPY, etc.)
        duration_ms: How long to maintain this emotion (None for indefinite)
        transition_duration_ms: Time to transition from previous emotion
        loop: Whether to loop the animation
        priority: Priority for handling simultaneous emotions (higher = more important)
    """
    sequence_name: str
    mood: int = 0  # DEFAULT mood constant
    duration_ms: Optional[int] = None
    transition_duration_ms: int = 1000
    loop: bool = True
    priority: int = 1
    
    def __post_init__(self):
        """Validate the configuration after initialization."""
        validation_errors = validate_animation_config(self)
        if validation_errors:
            raise ValueError(f"Invalid AnimationConfig: {', '.join(validation_errors)}")


def validate_animation_config(config: AnimationConfig) -> List[str]:
    """
    Validate an AnimationConfig instance for correctness.
    
    This function performs comprehensive validation of an AnimationConfig
    to ensure all values are within acceptable ranges and types.
    
    Args:
        config: The AnimationConfig instance to validate
        
    Returns:
        List of validation error messages. Empty list if valid.
    """
    errors = []
    
    # Validate sequence_name
    if not isinstance(config.sequence_name, str):
        errors.append("sequence_name must be a string")
    elif not config.sequence_name.strip():
        errors.append("sequence_name cannot be empty")
    
    # Validate mood
    if not isinstance(config.mood, int):
        errors.append("mood must be an integer")
    elif config.mood < 0:
        errors.append("mood must be non-negative")
    
    # Validate duration_ms
    if config.duration_ms is not None:
        if not isinstance(config.duration_ms, int):
            errors.append("duration_ms must be an integer or None")
        elif config.duration_ms <= 0:
            errors.append("duration_ms must be positive when specified")
    
    # Validate transition_duration_ms
    if not isinstance(config.transition_duration_ms, int):
        errors.append("transition_duration_ms must be an integer")
    elif config.transition_duration_ms < 0:
        errors.append("transition_duration_ms must be non-negative")
    elif config.transition_duration_ms > 10000:  # 10 seconds max
        errors.append("transition_duration_ms should not exceed 10000ms")
    
    # Validate loop
    if not isinstance(config.loop, bool):
        errors.append("loop must be a boolean")
    
    # Validate priority
    if not isinstance(config.priority, int):
        errors.append("priority must be an integer")
    elif config.priority < 1 or config.priority > 10:
        errors.append("priority must be between 1 and 10")
    
    return errors


def validate_emotion_name(emotion_name: str, allow_custom: bool = False) -> bool:
    """
    Validate that an emotion name is one of the supported categories.
    
    Args:
        emotion_name: The emotion name to validate
        allow_custom: If True, allows custom emotion names beyond the predefined set
        
    Returns:
        True if the emotion name is valid, False otherwise
    """
    if not isinstance(emotion_name, str):
        return False
    
    if allow_custom:
        # For custom emotions, just check that it's a non-empty string
        return bool(emotion_name.strip())
    
    return emotion_name.lower() in VALID_EMOTIONS


def validate_emotion_mapping(emotion_mapping: Dict[str, Any]) -> List[str]:
    """
    Validate a complete emotion-to-animation mapping configuration.
    
    This function validates that all required emotions are present and
    that each emotion has a valid AnimationConfig.
    
    Args:
        emotion_mapping: Dictionary mapping emotion names to animation configs
        
    Returns:
        List of validation error messages. Empty list if valid.
    """
    errors = []
    
    if not isinstance(emotion_mapping, dict):
        errors.append("emotion_mapping must be a dictionary")
        return errors
    
    # Check that all required emotions are present
    missing_emotions = VALID_EMOTIONS - set(emotion_mapping.keys())
    if missing_emotions:
        errors.append(f"Missing required emotions: {', '.join(sorted(missing_emotions))}")
    
    # Check for invalid emotion names
    invalid_emotions = set(emotion_mapping.keys()) - VALID_EMOTIONS
    if invalid_emotions:
        errors.append(f"Invalid emotion names: {', '.join(sorted(invalid_emotions))}")
    
    # Validate each animation config
    for emotion_name, config_data in emotion_mapping.items():
        if not validate_emotion_name(emotion_name):
            continue  # Already reported as invalid emotion name
        
        try:
            if isinstance(config_data, dict):
                # Convert dict to AnimationConfig for validation
                config = AnimationConfig(**config_data)
            elif isinstance(config_data, AnimationConfig):
                config = config_data
            else:
                errors.append(f"Invalid config type for emotion '{emotion_name}': must be dict or AnimationConfig")
                continue
            
            # Validate the config
            config_errors = validate_animation_config(config)
            for error in config_errors:
                errors.append(f"Error in emotion '{emotion_name}': {error}")
                
        except Exception as e:
            errors.append(f"Failed to validate config for emotion '{emotion_name}': {str(e)}")
    
    return errors


def get_default_emotion_mapping() -> Dict[str, AnimationConfig]:
    """
    Get the default emotion-to-animation mapping configuration.
    
    This provides a baseline configuration that maps each emotion category
    to appropriate animation sequences with healthcare-appropriate settings.
    
    Returns:
        Dictionary mapping emotion names to AnimationConfig instances
    """
    return {
        EMOTION_NEUTRAL: AnimationConfig(
            sequence_name="idle_gentle",
            mood=0,  # DEFAULT mood
            duration_ms=None,  # Indefinite
            transition_duration_ms=1000,
            loop=True,
            priority=1
        ),
        EMOTION_HAPPY: AnimationConfig(
            sequence_name="gentle_joy",
            mood=3,  # HAPPY mood
            duration_ms=4000,
            transition_duration_ms=1500,
            loop=False,
            priority=3
        ),
        EMOTION_URGENT: AnimationConfig(
            sequence_name="alert_focused",
            mood=0,  # DEFAULT mood
            duration_ms=None,  # Indefinite until changed
            transition_duration_ms=500,
            loop=True,
            priority=5
        ),
        EMOTION_CONCERNED: AnimationConfig(
            sequence_name="empathetic_support",
            mood=0,  # DEFAULT mood
            duration_ms=5000,
            transition_duration_ms=1200,
            loop=False,
            priority=4
        ),
        EMOTION_REQUEST: AnimationConfig(
            sequence_name="attentive_listening",
            mood=0,  # DEFAULT mood
            duration_ms=3000,
            transition_duration_ms=800,
            loop=False,
            priority=3
        )
    }


def log_emotion_validation_errors(errors: List[str], logger: Optional[logging.Logger] = None) -> None:
    """
    Log validation errors with appropriate severity levels.
    
    Args:
        errors: List of validation error messages
        logger: Optional logger instance. If None, uses default logging
    """
    if not errors:
        return
    
    if logger is None:
        logger = logging.getLogger(__name__)
    
    for error in errors:
        logger.error(f"Emotion animation validation error: {error}")


def load_emotion_mappings_from_json(config_file_path: str) -> Dict[str, AnimationConfig]:
    """
    Load emotion-to-animation mappings from a JSON configuration file.
    
    This function reads a JSON file containing emotion mappings and converts
    them to AnimationConfig instances. The JSON structure should match the
    schema defined in the design document.
    
    Args:
        config_file_path: Path to the JSON configuration file
        
    Returns:
        Dictionary mapping emotion names to AnimationConfig instances
        
    Raises:
        FileNotFoundError: If the configuration file doesn't exist
        json.JSONDecodeError: If the JSON file is malformed
        ValueError: If the configuration data is invalid
    """
    logger = logging.getLogger(__name__)
    
    # Check if file exists
    if not os.path.exists(config_file_path):
        raise FileNotFoundError(f"Configuration file not found: {config_file_path}")
    
    # Load JSON data
    try:
        with open(config_file_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in configuration file {config_file_path}: {e.msg}", e.doc, e.pos)
    
    # Extract emotion mappings from the configuration
    if not isinstance(config_data, dict):
        raise ValueError("Configuration file must contain a JSON object")
    
    # Support both direct emotion mappings and nested structure
    if "emotion_mappings" in config_data:
        emotion_mappings_data = config_data["emotion_mappings"]
    else:
        # Assume the entire file is emotion mappings
        emotion_mappings_data = config_data
    
    if not isinstance(emotion_mappings_data, dict):
        raise ValueError("Emotion mappings must be a JSON object")
    
    # Convert to AnimationConfig instances
    emotion_mappings = {}
    for emotion_name, config_dict in emotion_mappings_data.items():
        if not isinstance(config_dict, dict):
            raise ValueError(f"Configuration for emotion '{emotion_name}' must be an object")
        
        try:
            # Create AnimationConfig from dictionary
            animation_config = AnimationConfig(**config_dict)
            emotion_mappings[emotion_name] = animation_config
        except TypeError as e:
            raise ValueError(f"Invalid configuration for emotion '{emotion_name}': {e}")
        except ValueError as e:
            raise ValueError(f"Invalid configuration for emotion '{emotion_name}': {e}")
    
    # Validate the complete mapping
    validation_errors = validate_emotion_mapping(emotion_mappings)
    if validation_errors:
        error_msg = f"Configuration validation failed: {'; '.join(validation_errors)}"
        raise ValueError(error_msg)
    
    logger.info(f"Successfully loaded {len(emotion_mappings)} emotion mappings from {config_file_path}")
    return emotion_mappings


def save_emotion_mappings_to_json(emotion_mappings: Dict[str, AnimationConfig], 
                                config_file_path: str,
                                include_metadata: bool = True) -> None:
    """
    Save emotion-to-animation mappings to a JSON configuration file.
    
    This function converts AnimationConfig instances to JSON format and saves
    them to a file. The output format matches the schema expected by
    load_emotion_mappings_from_json().
    
    Args:
        emotion_mappings: Dictionary of emotion name to AnimationConfig mappings
        config_file_path: Path where to save the JSON configuration file
        include_metadata: Whether to include additional metadata in the JSON
        
    Raises:
        ValueError: If the emotion mappings are invalid
        OSError: If the file cannot be written
    """
    logger = logging.getLogger(__name__)
    
    # Validate the mappings before saving
    validation_errors = validate_emotion_mapping(emotion_mappings)
    if validation_errors:
        error_msg = f"Cannot save invalid emotion mappings: {'; '.join(validation_errors)}"
        raise ValueError(error_msg)
    
    # Convert AnimationConfig instances to dictionaries
    emotion_mappings_dict = {}
    for emotion_name, config in emotion_mappings.items():
        emotion_mappings_dict[emotion_name] = {
            "sequence_name": config.sequence_name,
            "mood": config.mood,
            "duration_ms": config.duration_ms,
            "transition_duration_ms": config.transition_duration_ms,
            "loop": config.loop,
            "priority": config.priority
        }
    
    # Create the configuration structure
    if include_metadata:
        config_data = {
            "emotion_mappings": emotion_mappings_dict,
            "default_emotion": DEFAULT_EMOTION,
            "transition_settings": {
                "smooth_transitions": True,
                "max_transition_time_ms": 2000,
                "interrupt_transitions": False
            },
            "metadata": {
                "version": "1.0",
                "description": "Emotion-to-animation mappings for RoboEyes healthcare assistant",
                "supported_emotions": list(VALID_EMOTIONS)
            }
        }
    else:
        config_data = emotion_mappings_dict
    
    # Ensure the directory exists
    config_path = Path(config_file_path)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write to file
    try:
        with open(config_file_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
    except OSError as e:
        raise OSError(f"Failed to write configuration file {config_file_path}: {e}")
    
    logger.info(f"Successfully saved {len(emotion_mappings)} emotion mappings to {config_file_path}")


def create_default_config_file(config_file_path: str) -> None:
    """
    Create a default emotion mappings configuration file.
    
    This function creates a JSON configuration file with the default emotion
    mappings, which can be used as a starting point for customization.
    
    Args:
        config_file_path: Path where to create the default configuration file
        
    Raises:
        OSError: If the file cannot be written
    """
    default_mappings = get_default_emotion_mapping()
    save_emotion_mappings_to_json(default_mappings, config_file_path, include_metadata=True)


def find_config_file(config_filename: str = "emotion_config.json") -> Optional[str]:
    """
    Find an emotion configuration file in common locations.
    
    This function searches for a configuration file in the following order:
    1. Current working directory
    2. User's home directory/.roboeyes/
    3. System config directory (platform-specific)
    
    Args:
        config_filename: Name of the configuration file to search for
        
    Returns:
        Path to the configuration file if found, None otherwise
    """
    search_paths = [
        # Current directory
        Path.cwd() / config_filename,
        # User config directory
        Path.home() / ".roboeyes" / config_filename,
        # Relative to the source directory
        Path(__file__).parent.parent.parent / "config" / config_filename,
    ]
    
    for config_path in search_paths:
        if config_path.exists() and config_path.is_file():
            return str(config_path)
    
    return None


class EmotionAnimationManager:
    """
    Manages emotion-to-animation mappings and provides API for triggering animations.
    
    This class serves as the core component for the emotion-driven animation system,
    providing a clean interface for triggering appropriate eye animation sequences
    based on emotional categories.
    """
    
    def __init__(self, roboeyes_instance, 
                 emotion_mappings: Optional[Dict[str, AnimationConfig]] = None,
                 config_file_path: Optional[str] = None):
        """
        Initialize the EmotionAnimationManager.
        
        Args:
            roboeyes_instance: The RoboEyes instance to control animations
            emotion_mappings: Optional custom emotion-to-animation mappings.
                            If None and config_file_path is None, uses default mappings.
            config_file_path: Optional path to JSON configuration file.
                            If provided, loads mappings from this file.
                            Takes precedence over emotion_mappings parameter.
        """
        self.roboeyes = roboeyes_instance
        self.logger = logging.getLogger(__name__)
        self._config_file_path: Optional[str] = None
        
        # Initialize state tracking first
        self._current_emotion: Optional[str] = None
        self._is_transitioning: bool = False
        self._fallback_emotion: str = DEFAULT_EMOTION
        
        # Animation state
        self._current_animation_start_time: Optional[int] = None
        self._transition_start_time: Optional[int] = None
        
        # Transition state
        self._target_emotion: Optional[str] = None
        self._target_animation_config: Optional[AnimationConfig] = None
        self._previous_emotion: Optional[str] = None
        self._transition_progress: float = 0.0
        
        # Initialize emotion mappings with comprehensive error handling
        self._emotion_mappings = {}
        self._initialization_errors = []
        
        try:
            if config_file_path is not None:
                # Load from configuration file
                try:
                    self._emotion_mappings = self.load_emotion_mappings(config_file_path)
                    self._config_file_path = config_file_path
                    self.logger.info(f"Successfully loaded emotion mappings from config file: {config_file_path}")
                except Exception as e:
                    error_msg = f"Failed to load configuration from {config_file_path}: {e}"
                    self.logger.error(error_msg)
                    self._initialization_errors.append(error_msg)
                    self._emotion_mappings = get_default_emotion_mapping()
                    self.logger.info("Falling back to default emotion mappings")
                    
            elif emotion_mappings is not None:
                # Use provided mappings
                try:
                    validation_errors = validate_emotion_mapping(emotion_mappings)
                    if validation_errors:
                        log_emotion_validation_errors(validation_errors, self.logger)
                        error_msg = f"Provided emotion mappings failed validation: {validation_errors}"
                        self.logger.warning(error_msg)
                        self._initialization_errors.append(error_msg)
                        self._emotion_mappings = get_default_emotion_mapping()
                        self.logger.info("Using default emotion mappings due to validation errors")
                    else:
                        self._emotion_mappings = emotion_mappings.copy()
                        self.logger.info("Successfully initialized with provided emotion mappings")
                except Exception as e:
                    error_msg = f"Error processing provided emotion mappings: {e}"
                    self.logger.error(error_msg)
                    self._initialization_errors.append(error_msg)
                    self._emotion_mappings = get_default_emotion_mapping()
                    self.logger.info("Falling back to default emotion mappings")
                    
            else:
                # Try to find and load a configuration file, otherwise use defaults
                try:
                    found_config = find_config_file()
                    if found_config:
                        try:
                            self._emotion_mappings = self.load_emotion_mappings(found_config)
                            self._config_file_path = found_config
                            self.logger.info(f"Automatically loaded configuration from: {found_config}")
                        except Exception as e:
                            error_msg = f"Failed to load auto-discovered configuration from {found_config}: {e}"
                            self.logger.warning(error_msg)
                            self._initialization_errors.append(error_msg)
                            self._emotion_mappings = get_default_emotion_mapping()
                            self.logger.info("Using default emotion mappings after auto-discovery failure")
                    else:
                        self._emotion_mappings = get_default_emotion_mapping()
                        self.logger.info("No configuration file found, using default emotion mappings")
                except Exception as e:
                    error_msg = f"Error during configuration auto-discovery: {e}"
                    self.logger.error(error_msg)
                    self._initialization_errors.append(error_msg)
                    self._emotion_mappings = get_default_emotion_mapping()
                    self.logger.info("Using default emotion mappings after auto-discovery error")
            
            # Ensure we have at least basic emotion mappings
            if not self._emotion_mappings:
                self.logger.critical("No emotion mappings available, creating minimal fallback")
                self._emotion_mappings = {
                    EMOTION_NEUTRAL: AnimationConfig(
                        sequence_name="idle_gentle",
                        mood=0,
                        duration_ms=None,
                        transition_duration_ms=1000,
                        loop=True,
                        priority=1
                    )
                }
                self._initialization_errors.append("Created minimal fallback emotion mapping")
            
            # Validate that fallback emotion exists
            if self._fallback_emotion not in self._emotion_mappings:
                if EMOTION_NEUTRAL in self._emotion_mappings:
                    self._fallback_emotion = EMOTION_NEUTRAL
                    self.logger.info(f"Set fallback emotion to '{EMOTION_NEUTRAL}'")
                else:
                    # Use first available emotion as fallback
                    self._fallback_emotion = next(iter(self._emotion_mappings.keys()))
                    self.logger.warning(f"Set fallback emotion to '{self._fallback_emotion}' (first available)")
                    
        except Exception as e:
            error_msg = f"Critical error during emotion mapping initialization: {e}"
            self.logger.critical(error_msg)
            self._initialization_errors.append(error_msg)
            
            # Create absolute minimal configuration
            self._emotion_mappings = {
                EMOTION_NEUTRAL: AnimationConfig(
                    sequence_name="idle_gentle",
                    mood=0,
                    duration_ms=None,
                    transition_duration_ms=1000,
                    loop=True,
                    priority=1
                )
            }
            self._fallback_emotion = EMOTION_NEUTRAL
        

        
        # Initialize configuration file watcher attributes
        self._config_watcher_running = False
        self._config_watcher_thread = None
        self._config_watcher_callback = None
        self._last_config_mtime = None
        
        # Log initialization summary
        if self._initialization_errors:
            self.logger.warning(f"EmotionAnimationManager initialized with {len(self._emotion_mappings)} emotion mappings, but encountered {len(self._initialization_errors)} errors during initialization")
            for error in self._initialization_errors:
                self.logger.debug(f"Initialization error: {error}")
        else:
            self.logger.info(f"EmotionAnimationManager initialized successfully with {len(self._emotion_mappings)} emotion mappings")
    
    def __del__(self):
        """Cleanup method to ensure config watcher is stopped."""
        try:
            self.stop_config_file_watcher()
        except:
            pass  # Ignore errors during cleanup
    
    @property
    def current_emotion(self) -> Optional[str]:
        """Get the currently active emotion."""
        return self._current_emotion
    
    @property
    def is_transitioning(self) -> bool:
        """Check if an animation transition is in progress."""
        return self._is_transitioning
    
    @property
    def fallback_emotion(self) -> str:
        """Get the fallback emotion used for invalid emotion names."""
        return self._fallback_emotion
    
    @property
    def transition_progress(self) -> float:
        """
        Get the current transition progress.
        
        Returns:
            Float between 0.0 and 1.0 indicating transition progress,
            or 0.0 if not transitioning
        """
        return self._transition_progress if self._is_transitioning else 0.0
    
    @fallback_emotion.setter
    def fallback_emotion(self, emotion_name: str) -> None:
        """
        Set the fallback emotion.
        
        Args:
            emotion_name: The emotion name to use as fallback
            
        Raises:
            ValueError: If the emotion name is not valid
        """
        if not validate_emotion_name(emotion_name):
            raise ValueError(f"Invalid fallback emotion name: {emotion_name}")
        
        if emotion_name not in self._emotion_mappings:
            raise ValueError(f"Fallback emotion '{emotion_name}' not found in emotion mappings")
        
        self._fallback_emotion = emotion_name
        self.logger.debug(f"Fallback emotion set to: {emotion_name}")
    
    def trigger_emotion(self, emotion_name: str, confidence: float = 1.0) -> bool:
        """
        Trigger an animation based on the specified emotion category with comprehensive error handling.
        
        This method serves as the main API for triggering emotion-based animations.
        It validates the emotion name, handles fallback scenarios, and initiates
        the appropriate animation sequence with robust error recovery.
        
        Args:
            emotion_name: The name of the emotion to trigger
            confidence: Confidence level of the emotion detection (0.0 to 1.0)
                       Currently used for logging, may be used for future features
            
        Returns:
            True if the emotion was successfully triggered, False otherwise
        """
        try:
            # Check system health before proceeding
            if not self.is_animation_system_healthy():
                self.logger.warning("Animation system health check failed, attempting recovery")
                if not self.recover_from_error():
                    self.logger.error("System recovery failed, using emergency fallback")
                    return self._emergency_animation_recovery(emotion_name)
            
            # Validate confidence parameter
            if not isinstance(confidence, (int, float)) or not (0.0 <= confidence <= 1.0):
                self.logger.warning(f"Invalid confidence value: {confidence}. Using 1.0")
                confidence = 1.0
            
            # Handle None or empty emotion name
            if emotion_name is None:
                self.logger.warning("Emotion name is None. Using fallback emotion.")
                return self._trigger_fallback_emotion()
            
            # Normalize emotion name
            if not isinstance(emotion_name, str):
                self.logger.error(f"Invalid emotion name type: {type(emotion_name)}. Expected string.")
                return self._trigger_fallback_emotion()
            
            emotion_name = emotion_name.lower().strip()
            
            # Handle empty string after normalization
            if not emotion_name:
                self.logger.warning("Empty emotion name after normalization. Using fallback emotion.")
                return self._trigger_fallback_emotion()
            
            # Validate emotion name (allow custom emotions if they're registered)
            if not validate_emotion_name(emotion_name, allow_custom=True):
                self.logger.warning(f"Invalid emotion name: '{emotion_name}'. Using fallback emotion: '{self._fallback_emotion}'")
                return self._trigger_fallback_emotion()
            
            # Check if emotion mapping exists
            if emotion_name not in self._emotion_mappings:
                self.logger.warning(f"No animation mapping found for emotion: '{emotion_name}'. Available emotions: {list(self._emotion_mappings.keys())}. Using fallback emotion: '{self._fallback_emotion}'")
                return self._trigger_fallback_emotion()
            
            # Get animation configuration with validation
            try:
                animation_config = self._emotion_mappings[emotion_name]
                if animation_config is None:
                    self.logger.error(f"Animation config for emotion '{emotion_name}' is None")
                    return self._trigger_fallback_emotion()
            except Exception as e:
                self.logger.error(f"Error accessing animation config for emotion '{emotion_name}': {e}")
                return self._trigger_fallback_emotion()
            
            # Log the emotion trigger with additional context
            self.logger.info(f"Triggering emotion: '{emotion_name}' with confidence: {confidence:.2f} "
                           f"(current: '{self._current_emotion}', transitioning: {self._is_transitioning})")
            
            # Update any ongoing transition with error handling
            try:
                if self._is_transitioning:
                    self._update_transition()
            except Exception as e:
                self.logger.warning(f"Error updating transition state: {e}. Forcing transition completion.")
                self.force_complete_transition()
            
            # Handle transition logic with error recovery
            try:
                if self._current_emotion != emotion_name:
                    # Check if we need to start a new transition
                    if animation_config.transition_duration_ms > 0:
                        self._start_emotion_transition(emotion_name, animation_config)
                    else:
                        # Immediate transition (no smooth animation)
                        self._current_emotion = emotion_name
            except Exception as e:
                self.logger.warning(f"Error handling transition logic for emotion '{emotion_name}': {e}")
                # Continue with direct animation execution
            
            # Trigger the animation with comprehensive error handling
            try:
                result = self._execute_emotion_animation(emotion_name, animation_config)
                
                if result:
                    self.logger.debug(f"Successfully triggered emotion '{emotion_name}'")
                    return True
                else:
                    self.logger.warning(f"Failed to execute animation for emotion '{emotion_name}', trying fallback")
                    return self._trigger_fallback_emotion()
                    
            except Exception as e:
                self.logger.error(f"Exception during animation execution for emotion '{emotion_name}': {e}")
                return self._trigger_fallback_emotion()
        
        except Exception as e:
            self.logger.error(f"Critical error in trigger_emotion for '{emotion_name}': {e}")
            # Last resort: emergency recovery
            return self._emergency_animation_recovery(emotion_name)
    
    def _trigger_fallback_emotion(self) -> bool:
        """
        Trigger the fallback emotion animation with comprehensive error handling.
        
        Returns:
            True if fallback emotion was successfully triggered, False otherwise
        """
        try:
            # Validate fallback emotion exists
            if self._fallback_emotion not in self._emotion_mappings:
                self.logger.error(f"Fallback emotion '{self._fallback_emotion}' not found in mappings. Available: {list(self._emotion_mappings.keys())}")
                
                # Try to use neutral as ultimate fallback
                if EMOTION_NEUTRAL in self._emotion_mappings and self._fallback_emotion != EMOTION_NEUTRAL:
                    self.logger.warning(f"Using '{EMOTION_NEUTRAL}' as ultimate fallback")
                    self._fallback_emotion = EMOTION_NEUTRAL
                else:
                    # Use any available emotion as last resort
                    if self._emotion_mappings:
                        available_emotion = next(iter(self._emotion_mappings.keys()))
                        self.logger.warning(f"Using '{available_emotion}' as emergency fallback")
                        self._fallback_emotion = available_emotion
                    else:
                        self.logger.critical("No emotion mappings available - system non-functional")
                        return self._emergency_animation_recovery("fallback")
            
            # Get animation configuration with validation
            try:
                animation_config = self._emotion_mappings[self._fallback_emotion]
                if animation_config is None:
                    self.logger.error(f"Fallback emotion '{self._fallback_emotion}' has None configuration")
                    return self._emergency_animation_recovery("fallback")
            except Exception as e:
                self.logger.error(f"Error accessing fallback emotion config: {e}")
                return self._emergency_animation_recovery("fallback")
            
            self.logger.info(f"Triggering fallback emotion: '{self._fallback_emotion}'")
            
            # Handle transition to fallback with error recovery
            try:
                if self._current_emotion != self._fallback_emotion:
                    self._start_emotion_transition(self._fallback_emotion, animation_config)
            except Exception as e:
                self.logger.warning(f"Error starting transition to fallback emotion: {e}")
                # Continue with direct execution
            
            # Execute fallback animation
            try:
                result = self._execute_emotion_animation(self._fallback_emotion, animation_config)
                
                if result:
                    self.logger.debug(f"Successfully triggered fallback emotion '{self._fallback_emotion}'")
                    return True
                else:
                    self.logger.error(f"Failed to execute fallback emotion '{self._fallback_emotion}'")
                    return self._emergency_animation_recovery("fallback")
                    
            except Exception as e:
                self.logger.error(f"Exception executing fallback emotion '{self._fallback_emotion}': {e}")
                return self._emergency_animation_recovery("fallback")
        
        except Exception as e:
            self.logger.critical(f"Critical error in fallback emotion trigger: {e}")
            return self._emergency_animation_recovery("fallback")
    
    def _start_emotion_transition(self, new_emotion: str, animation_config: AnimationConfig) -> None:
        """
        Start a transition to a new emotion.
        
        Args:
            new_emotion: The emotion to transition to
            animation_config: Animation configuration for the new emotion
        """
        try:
            from desktop.timing import ticks_ms
        except ImportError:
            # Fallback for testing or when desktop timing is not available
            import time
            ticks_ms = lambda: int(time.time() * 1000)
        
        self._is_transitioning = True
        self._transition_start_time = ticks_ms()
        self._target_emotion = new_emotion
        self._target_animation_config = animation_config
        
        # Store previous emotion for smooth blending
        self._previous_emotion = self._current_emotion
        
        self.logger.debug(f"Starting transition from '{self._current_emotion}' to '{new_emotion}' "
                         f"(duration: {animation_config.transition_duration_ms}ms)")
    
    def _update_transition(self) -> bool:
        """
        Update the current transition state and check if it's complete.
        
        Returns:
            True if transition is complete, False if still in progress
        """
        if not self._is_transitioning or self._transition_start_time is None:
            return True
        
        try:
            from desktop.timing import ticks_ms, ticks_diff
        except ImportError:
            # Fallback for testing or when desktop timing is not available
            import time
            ticks_ms = lambda: int(time.time() * 1000)
            ticks_diff = lambda t1, t2: t1 - t2
        
        current_time = ticks_ms()
        elapsed_time = ticks_diff(current_time, self._transition_start_time)
        
        if self._target_animation_config is None:
            # No target config, complete transition immediately
            self._complete_transition()
            return True
        
        transition_duration = self._target_animation_config.transition_duration_ms
        
        if elapsed_time >= transition_duration:
            # Transition is complete
            self._complete_transition()
            return True
        
        # Calculate transition progress (0.0 to 1.0)
        self._transition_progress = min(elapsed_time / transition_duration, 1.0)
        
        self.logger.debug(f"Transition progress: {self._transition_progress:.2f} "
                         f"({elapsed_time}ms / {transition_duration}ms)")
        
        return False
    
    def _complete_transition(self) -> None:
        """Complete the current transition and update state."""
        if self._target_emotion is not None:
            self._current_emotion = self._target_emotion
        
        self._is_transitioning = False
        self._transition_start_time = None
        self._target_emotion = None
        self._target_animation_config = None
        self._previous_emotion = None
        self._transition_progress = 0.0
        
        self.logger.debug(f"Completed transition to emotion: '{self._current_emotion}'")
    
    def _should_interrupt_current_animation(self, new_animation_config: AnimationConfig) -> bool:
        """
        Determine if the current animation should be interrupted for a new one.
        
        Args:
            new_animation_config: Configuration of the new animation to potentially start
            
        Returns:
            True if current animation should be interrupted, False otherwise
        """
        # Always allow interruption if no current emotion
        if self._current_emotion is None:
            return True
        
        # Get current emotion's config
        current_config = self._emotion_mappings.get(self._current_emotion)
        if current_config is None:
            return True
        
        # Check priority - higher priority can interrupt lower priority
        if new_animation_config.priority > current_config.priority:
            return True
        
        # If same priority, check if current animation has a duration limit
        if (new_animation_config.priority == current_config.priority and 
            current_config.duration_ms is not None):
            # Check if current animation should have expired
            if self._current_animation_start_time is not None:
                try:
                    from desktop.timing import ticks_ms, ticks_diff
                except ImportError:
                    import time
                    ticks_ms = lambda: int(time.time() * 1000)
                    ticks_diff = lambda t1, t2: t1 - t2
                
                current_time = ticks_ms()
                elapsed = ticks_diff(current_time, self._current_animation_start_time)
                
                if elapsed >= current_config.duration_ms:
                    return True
        
        # Don't interrupt critical animations abruptly
        # Critical animations are those with high priority (4 or higher)
        if current_config.priority >= 4:
            # Only allow interruption by higher priority or if transition is smooth
            return (new_animation_config.priority > current_config.priority or
                    new_animation_config.transition_duration_ms > 0)
        
        return False

    def _execute_emotion_animation(self, emotion_name: str, animation_config: AnimationConfig) -> bool:
        """
        Execute the animation for the specified emotion with comprehensive error handling.
        
        Args:
            emotion_name: The emotion name
            animation_config: Animation configuration
            
        Returns:
            True if animation was successfully started, False otherwise
        """
        try:
            try:
                from desktop.timing import ticks_ms
            except ImportError:
                # Fallback for testing or when desktop timing is not available
                import time
                ticks_ms = lambda: int(time.time() * 1000)
            
            # Check if we should interrupt the current animation
            if (self._current_emotion is not None and 
                not self._should_interrupt_current_animation(animation_config)):
                self.logger.debug(f"Not interrupting current animation '{self._current_emotion}' "
                                f"for '{emotion_name}' (priority: {animation_config.priority})")
                return False
            
            # If we're transitioning, check if we should wait for completion
            if self._is_transitioning and animation_config.transition_duration_ms > 0:
                # Update transition state
                transition_complete = self._update_transition()
                
                if not transition_complete:
                    # Still transitioning, apply blended animation if possible
                    self._apply_blended_animation(emotion_name, animation_config)
                    return True
            
            # Set the mood with error recovery
            try:
                if hasattr(self.roboeyes, 'mood') and self.roboeyes.mood != animation_config.mood:
                    # Apply mood gradually during transition if transitioning
                    if self._is_transitioning and self._transition_progress < 1.0:
                        # Blend mood change during transition
                        self._apply_gradual_mood_change(animation_config.mood)
                    else:
                        self.roboeyes.mood = animation_config.mood
                        self.logger.debug(f"Set mood to: {animation_config.mood}")
            except Exception as e:
                self.logger.warning(f"Failed to set mood for emotion '{emotion_name}': {e}. Continuing with animation.")
            
            # Try to trigger the animation sequence with multiple fallback strategies
            sequence_name = animation_config.sequence_name
            animation_triggered = False
            
            try:
                # Strategy 1: Check if the sequence method exists on the roboeyes instance
                if hasattr(self.roboeyes, sequence_name):
                    sequence_method = getattr(self.roboeyes, sequence_name)
                    if callable(sequence_method):
                        sequence_method()
                        self.logger.debug(f"Triggered animation sequence: {sequence_name}")
                        animation_triggered = True
                    else:
                        self.logger.warning(f"Sequence '{sequence_name}' is not callable")
                
                # Strategy 2: Fallback to checking sequences collection (for backward compatibility)
                elif hasattr(self.roboeyes, 'sequences') and hasattr(self.roboeyes.sequences, sequence_name):
                    sequence_method = getattr(self.roboeyes.sequences, sequence_name)
                    if callable(sequence_method):
                        sequence_method()
                        self.logger.debug(f"Triggered animation sequence: {sequence_name}")
                        animation_triggered = True
                    else:
                        self.logger.warning(f"Sequence '{sequence_name}' is not callable")
                
                # Strategy 3: Try common animation fallbacks
                elif not animation_triggered:
                    fallback_triggered = self._try_animation_fallbacks(emotion_name, animation_config)
                    if fallback_triggered:
                        animation_triggered = True
                        self.logger.info(f"Used fallback animation for emotion '{emotion_name}'")
                    else:
                        self.logger.warning(f"Animation sequence '{sequence_name}' not found. Using basic mood change.")
                
            except Exception as e:
                self.logger.error(f"Error executing animation sequence '{sequence_name}': {e}")
                # Try fallback animations
                try:
                    fallback_triggered = self._try_animation_fallbacks(emotion_name, animation_config)
                    if fallback_triggered:
                        animation_triggered = True
                        self.logger.info(f"Used fallback animation after sequence error for emotion '{emotion_name}'")
                except Exception as fallback_error:
                    self.logger.error(f"Fallback animation also failed for emotion '{emotion_name}': {fallback_error}")
            
            # Update state only if not transitioning or transition is complete
            if not self._is_transitioning:
                self._current_emotion = emotion_name
                self._current_animation_start_time = ticks_ms()
            
            # Return True if any animation was triggered, even if it was a fallback
            return animation_triggered or self._ensure_basic_animation_state()
            
        except Exception as e:
            self.logger.error(f"Critical error executing animation for emotion '{emotion_name}': {e}")
            # Last resort: try to maintain basic functionality
            return self._emergency_animation_recovery(emotion_name)
    
    def _apply_blended_animation(self, target_emotion: str, target_config: AnimationConfig) -> None:
        """
        Apply a blended animation during transition.
        
        Args:
            target_emotion: The emotion being transitioned to
            target_config: Animation configuration for the target emotion
        """
        # For now, this is a placeholder for future enhancement
        # In a full implementation, this would blend between the current and target animations
        # based on the transition progress
        
        self.logger.debug(f"Applying blended animation: {self._transition_progress:.2f} "
                         f"blend from '{self._previous_emotion}' to '{target_emotion}'")
        
        # Simple implementation: just log the blend state
        # Future enhancement could implement actual visual blending
    
    def _apply_gradual_mood_change(self, target_mood: int) -> None:
        """
        Apply a gradual mood change during transition.
        
        Args:
            target_mood: The target mood to transition to
        """
        if not hasattr(self.roboeyes, 'mood'):
            return
        
        current_mood = getattr(self.roboeyes, 'mood', 0)
        
        # Simple linear interpolation between moods
        # In practice, moods are discrete values, so this is more conceptual
        if current_mood != target_mood:
            # For discrete mood values, we can only switch at certain progress thresholds
            if self._transition_progress >= 0.5:  # Switch halfway through transition
                self.roboeyes.mood = target_mood
                self.logger.debug(f"Gradually changed mood to: {target_mood} "
                                f"(progress: {self._transition_progress:.2f})")
    
    def get_available_emotions(self) -> List[str]:
        """
        Get a list of all available emotion categories.
        
        Returns:
            List of emotion names that can be triggered
        """
        return list(self._emotion_mappings.keys())
    
    def register_emotion_mapping(self, emotion_name: str, animation_config: AnimationConfig) -> bool:
        """
        Register or update an emotion-to-animation mapping.
        
        Args:
            emotion_name: The emotion name to register
            animation_config: Animation configuration for this emotion
            
        Returns:
            True if registration was successful, False otherwise
        """
        # Validate emotion name (allow custom emotions for extensibility)
        if not validate_emotion_name(emotion_name, allow_custom=True):
            self.logger.error(f"Cannot register invalid emotion name: '{emotion_name}'")
            return False
        
        # Validate animation config
        validation_errors = validate_animation_config(animation_config)
        if validation_errors:
            log_emotion_validation_errors(validation_errors, self.logger)
            self.logger.error(f"Cannot register emotion '{emotion_name}' due to invalid configuration")
            return False
        
        # Register the mapping
        self._emotion_mappings[emotion_name] = animation_config
        self.logger.info(f"Registered emotion mapping: '{emotion_name}' -> '{animation_config.sequence_name}'")
        return True
    
    def remove_emotion_mapping(self, emotion_name: str) -> bool:
        """
        Remove an emotion-to-animation mapping.
        
        Args:
            emotion_name: The emotion name to remove
            
        Returns:
            True if removal was successful, False otherwise
        """
        if emotion_name not in self._emotion_mappings:
            self.logger.warning(f"Cannot remove non-existent emotion mapping: '{emotion_name}'")
            return False
        
        # Prevent removal of fallback emotion
        if emotion_name == self._fallback_emotion:
            self.logger.error(f"Cannot remove fallback emotion: '{emotion_name}'")
            return False
        
        del self._emotion_mappings[emotion_name]
        self.logger.info(f"Removed emotion mapping: '{emotion_name}'")
        
        # Reset current emotion if it was the removed one
        if self._current_emotion == emotion_name:
            self._current_emotion = None
            self.logger.debug("Reset current emotion due to mapping removal")
        
        return True
    
    def get_emotion_config(self, emotion_name: str) -> Optional[AnimationConfig]:
        """
        Get the animation configuration for a specific emotion.
        
        Args:
            emotion_name: The emotion name to look up
            
        Returns:
            AnimationConfig if found, None otherwise
        """
        return self._emotion_mappings.get(emotion_name)
    
    def update_emotion_config(self, emotion_name: str, animation_config: AnimationConfig) -> bool:
        """
        Update the animation configuration for an existing emotion.
        
        Args:
            emotion_name: The emotion name to update
            animation_config: New animation configuration
            
        Returns:
            True if update was successful, False otherwise
        """
        if emotion_name not in self._emotion_mappings:
            self.logger.error(f"Cannot update non-existent emotion: '{emotion_name}'")
            return False
        
        # Validate the new configuration
        validation_errors = validate_animation_config(animation_config)
        if validation_errors:
            log_emotion_validation_errors(validation_errors, self.logger)
            self.logger.error(f"Cannot update emotion '{emotion_name}' due to invalid configuration")
            return False
        
        self._emotion_mappings[emotion_name] = animation_config
        self.logger.info(f"Updated emotion mapping: '{emotion_name}' -> '{animation_config.sequence_name}'")
        return True
    
    def update(self) -> None:
        """
        Update the emotion animation system.
        
        This method should be called regularly (e.g., in the main animation loop)
        to update transition states and handle animation timing.
        """
        if self._is_transitioning:
            transition_complete = self._update_transition()
            
            if transition_complete and self._target_emotion is not None:
                # Execute the target animation now that transition is complete
                target_config = self._emotion_mappings.get(self._target_emotion)
                if target_config is not None:
                    self._execute_emotion_animation(self._target_emotion, target_config)
    
    def force_complete_transition(self) -> bool:
        """
        Force completion of any ongoing transition.
        
        Returns:
            True if a transition was completed, False if no transition was active
        """
        if not self._is_transitioning:
            return False
        
        self.logger.debug("Forcing completion of ongoing transition")
        self._complete_transition()
        
        # Execute the target animation if we had one
        if self._target_emotion is not None:
            target_config = self._emotion_mappings.get(self._target_emotion)
            if target_config is not None:
                self._execute_emotion_animation(self._target_emotion, target_config)
        
        return True
    
    def reset_to_neutral(self) -> bool:
        """
        Reset the animation system to neutral emotion.
        
        Returns:
            True if reset was successful, False otherwise
        """
        return self.trigger_emotion(EMOTION_NEUTRAL)
    
    def get_emotion_mappings(self) -> Dict[str, AnimationConfig]:
        """
        Get a copy of all current emotion mappings.
        
        Returns:
            Dictionary of emotion name to AnimationConfig mappings
        """
        return self._emotion_mappings.copy()
    
    def load_emotion_mappings(self, config_file_path: str) -> Dict[str, AnimationConfig]:
        """
        Load emotion mappings from a JSON configuration file.
        
        This method loads emotion-to-animation mappings from a JSON file and
        validates them before returning. If loading fails, it logs the error
        and raises an exception.
        
        Args:
            config_file_path: Path to the JSON configuration file
            
        Returns:
            Dictionary mapping emotion names to AnimationConfig instances
            
        Raises:
            FileNotFoundError: If the configuration file doesn't exist
            json.JSONDecodeError: If the JSON file is malformed
            ValueError: If the configuration data is invalid
        """
        try:
            emotion_mappings = load_emotion_mappings_from_json(config_file_path)
            self.logger.info(f"Successfully loaded emotion mappings from: {config_file_path}")
            return emotion_mappings
        except Exception as e:
            self.logger.error(f"Failed to load emotion mappings from {config_file_path}: {e}")
            raise
    
    def reload_emotion_mappings(self, config_file_path: Optional[str] = None) -> bool:
        """
        Reload emotion mappings from the configuration file.
        
        This method reloads the emotion mappings from the specified configuration
        file or the previously loaded file. This enables hot-reloading of
        configuration changes without restarting the system.
        
        Args:
            config_file_path: Optional path to configuration file.
                            If None, uses the previously loaded file path.
            
        Returns:
            True if reload was successful, False otherwise
        """
        # Determine which config file to use
        file_path = config_file_path or self._config_file_path
        
        if file_path is None:
            self.logger.error("No configuration file path available for reload")
            return False
        
        try:
            # Load new mappings
            new_mappings = self.load_emotion_mappings(file_path)
            
            # Update current mappings
            old_count = len(self._emotion_mappings)
            self._emotion_mappings = new_mappings
            self._config_file_path = file_path
            
            self.logger.info(f"Successfully reloaded emotion mappings from {file_path} "
                           f"({old_count} -> {len(new_mappings)} mappings)")
            
            # Reset current emotion if it's no longer available
            if (self._current_emotion is not None and 
                self._current_emotion not in self._emotion_mappings):
                self.logger.warning(f"Current emotion '{self._current_emotion}' no longer available after reload")
                self._current_emotion = None
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to reload emotion mappings: {e}")
            return False
    
    def save_emotion_mappings(self, config_file_path: Optional[str] = None, 
                            include_metadata: bool = True) -> bool:
        """
        Save current emotion mappings to a JSON configuration file.
        
        Args:
            config_file_path: Optional path to save the configuration file.
                            If None, uses the previously loaded file path.
            include_metadata: Whether to include additional metadata in the JSON
            
        Returns:
            True if save was successful, False otherwise
        """
        # Determine which config file to use
        file_path = config_file_path or self._config_file_path
        
        if file_path is None:
            self.logger.error("No configuration file path available for save")
            return False
        
        try:
            save_emotion_mappings_to_json(self._emotion_mappings, file_path, include_metadata)
            self._config_file_path = file_path
            self.logger.info(f"Successfully saved emotion mappings to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save emotion mappings: {e}")
            return False
    
    def create_default_config(self, config_file_path: str) -> bool:
        """
        Create a default emotion mappings configuration file.
        
        This method creates a JSON configuration file with the default emotion
        mappings, which can be used as a starting point for customization.
        
        Args:
            config_file_path: Path where to create the default configuration file
            
        Returns:
            True if creation was successful, False otherwise
        """
        try:
            create_default_config_file(config_file_path)
            self.logger.info(f"Successfully created default configuration at {config_file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create default configuration: {e}")
            return False
    
    def _try_animation_fallbacks(self, emotion_name: str, animation_config: AnimationConfig) -> bool:
        """
        Try various fallback animation strategies when the primary sequence fails.
        
        Args:
            emotion_name: The emotion name
            animation_config: Animation configuration
            
        Returns:
            True if a fallback animation was successfully triggered, False otherwise
        """
        try:
            # Fallback 1: Try basic eye movements based on emotion type
            if emotion_name == EMOTION_HAPPY:
                if hasattr(self.roboeyes, 'happy_eyes') and callable(self.roboeyes.happy_eyes):
                    self.roboeyes.happy_eyes()
                    return True
                elif hasattr(self.roboeyes, 'mood'):
                    self.roboeyes.mood = HAPPY if hasattr(self.roboeyes, 'HAPPY') else 3
                    return True
            
            elif emotion_name == EMOTION_URGENT:
                if hasattr(self.roboeyes, 'alert') and callable(self.roboeyes.alert):
                    self.roboeyes.alert()
                    return True
                elif hasattr(self.roboeyes, 'wide_open') and callable(self.roboeyes.wide_open):
                    self.roboeyes.wide_open()
                    return True
            
            elif emotion_name == EMOTION_CONCERNED:
                if hasattr(self.roboeyes, 'concerned') and callable(self.roboeyes.concerned):
                    self.roboeyes.concerned()
                    return True
                elif hasattr(self.roboeyes, 'tired_eyes') and callable(self.roboeyes.tired_eyes):
                    self.roboeyes.tired_eyes()
                    return True
            
            elif emotion_name == EMOTION_REQUEST:
                if hasattr(self.roboeyes, 'attentive') and callable(self.roboeyes.attentive):
                    self.roboeyes.attentive()
                    return True
                elif hasattr(self.roboeyes, 'look_up') and callable(self.roboeyes.look_up):
                    self.roboeyes.look_up()
                    return True
            
            # Fallback 2: Try generic animation methods
            if hasattr(self.roboeyes, 'blink') and callable(self.roboeyes.blink):
                self.roboeyes.blink()
                return True
            
            # Fallback 3: Try to open eyes if they exist
            if hasattr(self.roboeyes, 'open_eyes') and callable(self.roboeyes.open_eyes):
                self.roboeyes.open_eyes()
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error in animation fallbacks for emotion '{emotion_name}': {e}")
            return False
    
    def _ensure_basic_animation_state(self) -> bool:
        """
        Ensure the animation system is in a basic working state.
        
        Returns:
            True if basic state was ensured, False if system is non-functional
        """
        try:
            # Try to ensure eyes are visible and responsive
            if hasattr(self.roboeyes, 'eyeLheightCurrent'):
                # Make sure eyes aren't completely closed
                if self.roboeyes.eyeLheightCurrent <= 1:
                    self.roboeyes.eyeLheightCurrent = max(10, self.roboeyes.eyeLheightDefault // 2)
                    self.logger.debug("Ensured left eye is visible")
            
            if hasattr(self.roboeyes, 'eyeRheightCurrent'):
                # Make sure eyes aren't completely closed
                if self.roboeyes.eyeRheightCurrent <= 1:
                    self.roboeyes.eyeRheightCurrent = max(10, self.roboeyes.eyeRheightDefault // 2)
                    self.logger.debug("Ensured right eye is visible")
            
            # Ensure mood is in a valid state
            if hasattr(self.roboeyes, 'mood'):
                if not isinstance(self.roboeyes.mood, int) or self.roboeyes.mood < 0:
                    self.roboeyes.mood = 0  # DEFAULT mood
                    self.logger.debug("Reset mood to default")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to ensure basic animation state: {e}")
            return False
    
    def _emergency_animation_recovery(self, emotion_name: str) -> bool:
        """
        Emergency recovery when all other animation methods fail.
        
        Args:
            emotion_name: The emotion name that failed
            
        Returns:
            True if emergency recovery succeeded, False if system is non-functional
        """
        try:
            self.logger.warning(f"Attempting emergency recovery for emotion '{emotion_name}'")
            
            # Reset to most basic state
            if hasattr(self.roboeyes, 'mood'):
                self.roboeyes.mood = 0  # DEFAULT mood
            
            # Try to trigger neutral emotion as last resort
            if emotion_name != self._fallback_emotion:
                self.logger.info(f"Emergency fallback to '{self._fallback_emotion}' emotion")
                return self._trigger_fallback_emotion()
            
            # If even fallback emotion failed, try basic eye state
            basic_state = self._ensure_basic_animation_state()
            if basic_state:
                self.logger.info("Emergency recovery: maintained basic eye visibility")
                return True
            
            # System is non-functional
            self.logger.error("Emergency recovery failed - animation system may be non-functional")
            return False
            
        except Exception as e:
            self.logger.critical(f"Emergency recovery failed with exception: {e}")
            return False
    
    def is_animation_system_healthy(self) -> bool:
        """
        Check if the animation system is in a healthy state.
        
        Returns:
            True if the system appears to be functioning normally, False otherwise
        """
        try:
            # Check if roboeyes instance is available
            if self.roboeyes is None:
                self.logger.error("Health check failed: roboeyes instance is None")
                return False
            
            # Check if basic attributes exist
            required_attrs = ['eyeLheightCurrent', 'eyeRheightCurrent', 'mood']
            for attr in required_attrs:
                if not hasattr(self.roboeyes, attr):
                    self.logger.warning(f"Health check: missing attribute '{attr}'")
            
            # Check if emotion mappings are available
            if not self._emotion_mappings:
                self.logger.error("Health check failed: no emotion mappings available")
                return False
            
            # Check if fallback emotion is available
            if self._fallback_emotion not in self._emotion_mappings:
                self.logger.error(f"Health check failed: fallback emotion '{self._fallback_emotion}' not available")
                return False
            
            # Check if we can access timing functions
            try:
                from desktop.timing import ticks_ms
                ticks_ms()
            except ImportError:
                # Fallback timing should work
                import time
                time.time()
            except Exception as e:
                self.logger.warning(f"Health check: timing functions may be unreliable: {e}")
            
            self.logger.debug("Animation system health check passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Health check failed with exception: {e}")
            return False
    
    def recover_from_error(self) -> bool:
        """
        Attempt to recover the animation system from an error state.
        
        Returns:
            True if recovery was successful, False otherwise
        """
        try:
            self.logger.info("Attempting animation system recovery")
            
            # Reset transition state
            self._is_transitioning = False
            self._transition_start_time = None
            self._target_emotion = None
            self._target_animation_config = None
            self._previous_emotion = None
            self._transition_progress = 0.0
            
            # Reset to fallback emotion
            self._current_emotion = None
            
            # Ensure basic animation state
            if not self._ensure_basic_animation_state():
                self.logger.error("Recovery failed: could not ensure basic animation state")
                return False
            
            # Try to trigger fallback emotion
            if not self._trigger_fallback_emotion():
                self.logger.error("Recovery failed: could not trigger fallback emotion")
                return False
            
            # Verify system health
            if not self.is_animation_system_healthy():
                self.logger.error("Recovery failed: system health check failed")
                return False
            
            self.logger.info("Animation system recovery successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Recovery attempt failed: {e}")
            return False
    
    def get_initialization_errors(self) -> List[str]:
        """
        Get any errors that occurred during initialization.
        
        Returns:
            List of error messages from initialization, empty if no errors
        """
        return self._initialization_errors.copy() if hasattr(self, '_initialization_errors') else []
    
    def has_initialization_errors(self) -> bool:
        """
        Check if there were any errors during initialization.
        
        Returns:
            True if there were initialization errors, False otherwise
        """
        return bool(getattr(self, '_initialization_errors', []))
    
    def reload_configuration(self, config_file_path: Optional[str] = None) -> bool:
        """
        Reload emotion mappings from configuration file without system restart.
        
        This method provides dynamic configuration updates by reloading the
        emotion mappings from a configuration file. It validates the new
        configuration before applying it to ensure system stability.
        
        Args:
            config_file_path: Optional path to configuration file. If None,
                            uses the current config file path if available.
        
        Returns:
            True if configuration was successfully reloaded, False otherwise
        """
        try:
            # Determine which config file to use
            target_config_path = config_file_path or self._config_file_path
            
            if not target_config_path:
                self.logger.error("No configuration file path available for reload")
                return False
            
            # Check if file exists
            if not os.path.exists(target_config_path):
                self.logger.error(f"Configuration file not found for reload: {target_config_path}")
                return False
            
            self.logger.info(f"Attempting to reload configuration from: {target_config_path}")
            
            # Load new configuration
            try:
                new_emotion_mappings = load_emotion_mappings_from_json(target_config_path)
            except Exception as e:
                self.logger.error(f"Failed to load new configuration: {e}")
                return False
            
            # Validate new configuration
            validation_errors = validate_emotion_mapping(new_emotion_mappings)
            if validation_errors:
                self.logger.error(f"New configuration failed validation: {'; '.join(validation_errors)}")
                log_emotion_validation_errors(validation_errors, self.logger)
                return False
            
            # Store current configuration for rollback
            old_emotion_mappings = self._emotion_mappings.copy()
            old_fallback_emotion = self._fallback_emotion
            
            try:
                # Apply new configuration
                self._emotion_mappings = new_emotion_mappings
                
                # Update fallback emotion if it's no longer available
                if self._fallback_emotion not in self._emotion_mappings:
                    if EMOTION_NEUTRAL in self._emotion_mappings:
                        self._fallback_emotion = EMOTION_NEUTRAL
                    else:
                        self._fallback_emotion = next(iter(self._emotion_mappings.keys()))
                    self.logger.info(f"Updated fallback emotion to: {self._fallback_emotion}")
                
                # Update config file path if provided
                if config_file_path:
                    self._config_file_path = config_file_path
                
                self.logger.info(f"Successfully reloaded configuration with {len(self._emotion_mappings)} emotion mappings")
                
                # Log configuration reload event
                self._log_configuration_reload_event(target_config_path, len(new_emotion_mappings))
                
                return True
                
            except Exception as e:
                # Rollback on error
                self.logger.error(f"Error applying new configuration, rolling back: {e}")
                self._emotion_mappings = old_emotion_mappings
                self._fallback_emotion = old_fallback_emotion
                return False
                
        except Exception as e:
            self.logger.error(f"Unexpected error during configuration reload: {e}")
            return False
    
    def update_emotion_mapping(self, emotion_name: str, animation_config: AnimationConfig) -> bool:
        """
        Update a single emotion mapping without full configuration reload.
        
        This method allows for dynamic updates of individual emotion mappings
        while the system is running. It validates the new configuration before
        applying it.
        
        Args:
            emotion_name: The emotion name to update
            animation_config: The new animation configuration
        
        Returns:
            True if the mapping was successfully updated, False otherwise
        """
        try:
            # Validate emotion name
            if not validate_emotion_name(emotion_name, allow_custom=True):
                self.logger.error(f"Invalid emotion name for mapping update: {emotion_name}")
                return False
            
            # Validate animation config
            config_errors = validate_animation_config(animation_config)
            if config_errors:
                self.logger.error(f"Invalid animation config for emotion '{emotion_name}': {'; '.join(config_errors)}")
                return False
            
            # Store old mapping for rollback
            old_mapping = self._emotion_mappings.get(emotion_name)
            
            try:
                # Apply new mapping
                self._emotion_mappings[emotion_name] = animation_config
                
                self.logger.info(f"Successfully updated emotion mapping for '{emotion_name}'")
                
                # Log the update event
                self._log_emotion_mapping_update_event(emotion_name, animation_config)
                
                return True
                
            except Exception as e:
                # Rollback on error
                self.logger.error(f"Error updating emotion mapping for '{emotion_name}', rolling back: {e}")
                if old_mapping is not None:
                    self._emotion_mappings[emotion_name] = old_mapping
                elif emotion_name in self._emotion_mappings:
                    del self._emotion_mappings[emotion_name]
                return False
                
        except Exception as e:
            self.logger.error(f"Unexpected error during emotion mapping update: {e}")
            return False
    
    def remove_emotion_mapping(self, emotion_name: str) -> bool:
        """
        Remove an emotion mapping from the configuration.
        
        This method allows for dynamic removal of emotion mappings. It prevents
        removal of required emotions and the current fallback emotion.
        
        Args:
            emotion_name: The emotion name to remove
        
        Returns:
            True if the mapping was successfully removed, False otherwise
        """
        try:
            # Check if emotion exists
            if emotion_name not in self._emotion_mappings:
                self.logger.warning(f"Cannot remove emotion mapping '{emotion_name}': not found")
                return False
            
            # Prevent removal of required emotions
            if emotion_name in VALID_EMOTIONS:
                self.logger.error(f"Cannot remove required emotion mapping: {emotion_name}")
                return False
            
            # Prevent removal of current fallback emotion
            if emotion_name == self._fallback_emotion:
                self.logger.error(f"Cannot remove fallback emotion mapping: {emotion_name}")
                return False
            
            # Store old mapping for rollback
            old_mapping = self._emotion_mappings[emotion_name]
            
            try:
                # Remove mapping
                del self._emotion_mappings[emotion_name]
                
                self.logger.info(f"Successfully removed emotion mapping for '{emotion_name}'")
                
                # Log the removal event
                self._log_emotion_mapping_removal_event(emotion_name)
                
                return True
                
            except Exception as e:
                # Rollback on error
                self.logger.error(f"Error removing emotion mapping for '{emotion_name}', rolling back: {e}")
                self._emotion_mappings[emotion_name] = old_mapping
                return False
                
        except Exception as e:
            self.logger.error(f"Unexpected error during emotion mapping removal: {e}")
            return False
    
    def start_config_file_watcher(self, callback: Optional[Callable[[str], None]] = None) -> bool:
        """
        Start watching the configuration file for changes and automatically reload.
        
        This method starts a background thread that monitors the configuration file
        for changes and automatically reloads the configuration when changes are detected.
        
        Args:
            callback: Optional callback function to call after successful reload.
                     Receives the config file path as argument.
        
        Returns:
            True if file watcher was started successfully, False otherwise
        """
        try:
            if not self._config_file_path:
                self.logger.error("Cannot start config file watcher: no config file path available")
                return False
            
            if not os.path.exists(self._config_file_path):
                self.logger.error(f"Cannot start config file watcher: config file not found: {self._config_file_path}")
                return False
            
            # Stop existing watcher if running
            self.stop_config_file_watcher()
            
            # Initialize watcher state
            self._config_watcher_running = True
            self._config_watcher_callback = callback
            self._last_config_mtime = os.path.getmtime(self._config_file_path)
            
            # Start watcher thread
            self._config_watcher_thread = threading.Thread(
                target=self._config_file_watcher_loop,
                daemon=True,
                name="EmotionConfigWatcher"
            )
            self._config_watcher_thread.start()
            
            self.logger.info(f"Started configuration file watcher for: {self._config_file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start config file watcher: {e}")
            return False
    
    def stop_config_file_watcher(self) -> None:
        """
        Stop the configuration file watcher.
        
        This method stops the background thread that monitors the configuration
        file for changes.
        """
        try:
            if hasattr(self, '_config_watcher_running'):
                self._config_watcher_running = False
            
            if hasattr(self, '_config_watcher_thread') and self._config_watcher_thread:
                if self._config_watcher_thread.is_alive():
                    # Give the thread a moment to stop gracefully
                    self._config_watcher_thread.join(timeout=1.0)
                self._config_watcher_thread = None
            
            self.logger.info("Stopped configuration file watcher")
            
        except Exception as e:
            self.logger.error(f"Error stopping config file watcher: {e}")
    
    def is_config_watcher_running(self) -> bool:
        """
        Check if the configuration file watcher is currently running.
        
        Returns:
            True if the watcher is running, False otherwise
        """
        return (hasattr(self, '_config_watcher_running') and 
                self._config_watcher_running and
                hasattr(self, '_config_watcher_thread') and
                self._config_watcher_thread and
                self._config_watcher_thread.is_alive())
    
    def _config_file_watcher_loop(self) -> None:
        """
        Main loop for the configuration file watcher thread.
        
        This method runs in a background thread and periodically checks
        the configuration file for modifications.
        """
        try:
            self.logger.debug("Configuration file watcher loop started")
            
            while getattr(self, '_config_watcher_running', False):
                try:
                    # Check if config file still exists
                    if not os.path.exists(self._config_file_path):
                        self.logger.warning(f"Configuration file no longer exists: {self._config_file_path}")
                        time.sleep(1.0)
                        continue
                    
                    # Check modification time
                    current_mtime = os.path.getmtime(self._config_file_path)
                    
                    if current_mtime > self._last_config_mtime:
                        self.logger.info(f"Configuration file change detected: {self._config_file_path}")
                        
                        # Small delay to ensure file write is complete
                        time.sleep(0.1)
                        
                        # Attempt to reload configuration
                        if self.reload_configuration():
                            self._last_config_mtime = current_mtime
                            
                            # Call callback if provided
                            if hasattr(self, '_config_watcher_callback') and self._config_watcher_callback:
                                try:
                                    self._config_watcher_callback(self._config_file_path)
                                except Exception as e:
                                    self.logger.error(f"Error in config watcher callback: {e}")
                        else:
                            self.logger.error("Failed to reload configuration after file change")
                    
                    # Sleep before next check
                    time.sleep(0.5)  # Check every 500ms
                    
                except Exception as e:
                    self.logger.error(f"Error in config file watcher loop: {e}")
                    time.sleep(1.0)  # Longer sleep on error
            
            self.logger.debug("Configuration file watcher loop stopped")
            
        except Exception as e:
            self.logger.error(f"Fatal error in config file watcher loop: {e}")
    
    def _log_configuration_reload_event(self, config_file_path: str, mapping_count: int) -> None:
        """
        Log a configuration reload event with relevant details.
        
        Args:
            config_file_path: Path to the configuration file that was reloaded
            mapping_count: Number of emotion mappings in the new configuration
        """
        try:
            event_details = {
                "event": "configuration_reload",
                "config_file": config_file_path,
                "mapping_count": mapping_count,
                "timestamp": time.time(),
                "current_emotion": self._current_emotion,
                "fallback_emotion": self._fallback_emotion
            }
            
            self.logger.info(f"Configuration reload event: {json.dumps(event_details)}")
            
        except Exception as e:
            self.logger.error(f"Error logging configuration reload event: {e}")
    
    def _log_emotion_mapping_update_event(self, emotion_name: str, animation_config: AnimationConfig) -> None:
        """
        Log an emotion mapping update event.
        
        Args:
            emotion_name: The emotion name that was updated
            animation_config: The new animation configuration
        """
        try:
            event_details = {
                "event": "emotion_mapping_update",
                "emotion_name": emotion_name,
                "sequence_name": animation_config.sequence_name,
                "mood": animation_config.mood,
                "duration_ms": animation_config.duration_ms,
                "transition_duration_ms": animation_config.transition_duration_ms,
                "loop": animation_config.loop,
                "priority": animation_config.priority,
                "timestamp": time.time()
            }
            
            self.logger.info(f"Emotion mapping update event: {json.dumps(event_details)}")
            
        except Exception as e:
            self.logger.error(f"Error logging emotion mapping update event: {e}")
    
    def _log_emotion_mapping_removal_event(self, emotion_name: str) -> None:
        """
        Log an emotion mapping removal event.
        
        Args:
            emotion_name: The emotion name that was removed
        """
        try:
            event_details = {
                "event": "emotion_mapping_removal",
                "emotion_name": emotion_name,
                "timestamp": time.time()
            }
            
            self.logger.info(f"Emotion mapping removal event: {json.dumps(event_details)}")
            
        except Exception as e:
            self.logger.error(f"Error logging emotion mapping removal event: {e}")
    
    def get_configuration_info(self) -> Dict[str, Any]:
        """
        Get information about the current configuration.
        
        Returns:
            Dictionary containing configuration information
        """
        try:
            return {
                "config_file_path": self._config_file_path,
                "emotion_mappings_count": len(self._emotion_mappings),
                "available_emotions": list(self._emotion_mappings.keys()),
                "fallback_emotion": self._fallback_emotion,
                "current_emotion": self._current_emotion,
                "config_watcher_running": self.is_config_watcher_running(),
                "has_initialization_errors": self.has_initialization_errors(),
                "initialization_errors_count": len(getattr(self, '_initialization_errors', []))
            }
        except Exception as e:
            self.logger.error(f"Error getting configuration info: {e}")
            return {"error": str(e)}