# EmotionAnimationManager API Documentation

Complete API reference for the streamlined EmotionAnimationManager, designed for team integration with TTS systems and healthcare applications.

## Table of Contents

1. [Overview](#overview)
2. [Core Classes](#core-classes)
3. [Emotion Constants](#emotion-constants)
4. [Primary Methods](#primary-methods)
5. [Configuration](#configuration)
6. [Error Handling](#error-handling)
7. [Integration Examples](#integration-examples)
8. [Type Hints Reference](#type-hints-reference)

## Overview

The EmotionAnimationManager provides a streamlined interface for triggering emotion-driven eye animations that coordinate seamlessly with TTS systems. It focuses on 5 core emotions designed for healthcare and empathetic interactions.

### Key Design Principles

- **Real-time updates** - Smooth transitions during pygame rendering
- **Error-safe operation** - Never breaks animation continuity
- **Simple API** - Easy integration with existing applications
- **TTS coordination** - Perfect timing with speech synthesis
- **Healthcare-focused** - Emotions designed for patient interactions

## Core Classes

### EmotionAnimationManager

The primary interface for emotion-driven animations.

```python
from src.roboeyes.emotion_animation_streamlined import EmotionAnimationManager

class EmotionAnimationManager:
    """
    Streamlined emotion animation manager for real-time emotion chaining.
    
    This class provides a simplified interface for triggering emotion-based
    eye animations while preserving real-time updates and seamless transitions.
    """
```

#### Constructor

```python
def __init__(self, roboeyes_instance, 
             emotion_config: Optional[Dict[str, EmotionConfig]] = None,
             emotion_mappings: Optional[Dict[str, Any]] = None,
             config_file_path: Optional[str] = None) -> None:
    """
    Initialize the EmotionAnimationManager with simple configuration.
    
    Args:
        roboeyes_instance: The RoboEyes instance to control animations.
                          Cannot be None.
        emotion_config: Optional custom emotion configurations. 
                       If None, uses default configurations.
        emotion_mappings: Legacy parameter for backward compatibility (ignored).
        config_file_path: Legacy parameter for backward compatibility (ignored).
    
    Raises:
        ValueError: If roboeyes_instance is None.
    
    Example:
        # Basic initialization with defaults
        emotion_manager = EmotionAnimationManager(roboeyes_instance)
        
        # Custom emotion configuration
        custom_config = {
            'happy': EmotionConfig('gentle_joy', duration_ms=4000),
            'neutral': EmotionConfig('idle_gentle', duration_ms=None)
        }
        emotion_manager = EmotionAnimationManager(roboeyes_instance, custom_config)
    """
```

### EmotionConfig

Configuration class for individual emotions.

```python
from src.roboeyes.emotion_animation_streamlined import EmotionConfig

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
```

#### Example Usage

```python
# Create custom emotion configurations
happy_config = EmotionConfig(
    sequence_name='gentle_joy',
    duration_ms=4000,  # 4 seconds
    loop=False
)

neutral_config = EmotionConfig(
    sequence_name='idle_gentle',
    duration_ms=None,  # Indefinite
    loop=True
)

custom_emotions = {
    'happy': happy_config,
    'neutral': neutral_config
}
```

## Emotion Constants

The system provides 5 core emotions designed for healthcare and TTS integration:

```python
from src.roboeyes.emotion_animation_streamlined import (
    EMOTION_HAPPY,
    EMOTION_NEUTRAL, 
    EMOTION_URGENT,
    EMOTION_CONCERNED,
    EMOTION_REQUEST,
    VALID_EMOTIONS,
    DEFAULT_EMOTION
)
```

### Emotion Descriptions

| Constant | Value | Use Case | Duration | Animation |
|----------|-------|----------|----------|-----------|
| `EMOTION_NEUTRAL` | `"neutral"` | Default/idle state, waiting | Indefinite | `idle_gentle` |
| `EMOTION_HAPPY` | `"happy"` | Greetings, positive news, reassurance | 4 seconds | `gentle_joy` |
| `EMOTION_REQUEST` | `"request"` | Asking questions, active listening | 3 seconds | `attentive_listening` |
| `EMOTION_CONCERNED` | `"concerned"` | Showing empathy, acknowledging problems | 5 seconds | `empathetic_support` |
| `EMOTION_URGENT` | `"urgent"` | Important information, alerts | Indefinite | `alert_focused` |

### Usage Guidelines

```python
# Healthcare interaction patterns
EMOTION_HAPPY     # "Hello! Welcome to our system."
EMOTION_REQUEST   # "How can I help you today?"
EMOTION_CONCERNED # "I understand your concern."
EMOTION_URGENT    # "This is important information."
EMOTION_NEUTRAL   # Return to idle state
```

## Primary Methods

### trigger_emotion()

Primary API for triggering emotion animations.

```python
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
    
    Error Handling:
        - Invalid emotions automatically fallback to neutral
        - None or empty strings fallback to neutral
        - Exceptions are caught and logged, animation continues
        - Never breaks the pygame rendering loop
    
    Example:
        # Basic usage
        success = emotion_manager.trigger_emotion('happy')
        if success:
            print("Emotion triggered successfully")
        else:
            print("Emotion failed, system used neutral fallback")
        
        # Error handling
        try:
            emotion_manager.trigger_emotion('invalid_emotion')
        except ValueError as e:
            print(f"Error: {e}")
            # Prints: "Emotion 'invalid_emotion' not supported. Available emotions: [...]"
    """
```

### update()

Critical method for real-time animation updates.

```python
def update(self) -> None:
    """
    Update animation state - called every frame for real-time updates.
    
    This method should be called regularly (e.g., every frame) to maintain
    smooth transitions and handle animation timing. Never throws exceptions
    to preserve pygame rendering loop continuity.
    
    Functionality:
        - Updates transition states for smooth emotion changes
        - Handles emotion duration expiration
        - Manages animation timing and state consistency
        - Provides error recovery without breaking rendering
    
    Critical Usage:
        MUST be called every frame in your main loop for proper operation.
        
    Example:
        # Essential main loop pattern
        while roboeyes.running:
            # Your application logic here
            
            emotion_manager.update()  # CRITICAL: Call every frame
            roboeyes.update()         # CRITICAL: Call every frame
            clock.tick(30)            # Control frame rate
    """
```

### get_available_emotions()

Get list of supported emotions.

```python
def get_available_emotions(self) -> List[str]:
    """
    Get list of supported emotions.
    
    Returns:
        List[str]: Sorted list of emotion names that can be used with trigger_emotion()
    
    Error Handling:
        - Returns at least ['neutral'] even if other emotions fail to load
        - Never throws exceptions
    
    Example:
        available = emotion_manager.get_available_emotions()
        print(f"Available emotions: {available}")
        # Output: Available emotions: ['concerned', 'happy', 'neutral', 'request', 'urgent']
        
        # Use in validation
        if 'happy' in available:
            emotion_manager.trigger_emotion('happy')
    """
```

### is_emotion_active()

Check if a specific emotion is currently active.

```python
def is_emotion_active(self, emotion_name: str) -> bool:
    """
    Check if a specific emotion is currently active.
    
    Args:
        emotion_name: Name of the emotion to check
        
    Returns:
        bool: True if the emotion is currently active, False otherwise
    
    Error Handling:
        - Returns False for invalid emotion names
        - Returns False for None or non-string inputs
        - Never throws exceptions
    
    Example:
        # Check before triggering
        if not emotion_manager.is_emotion_active('happy'):
            emotion_manager.trigger_emotion('happy')
        
        # State-dependent logic
        if emotion_manager.is_emotion_active('urgent'):
            # Handle urgent state differently
            handle_urgent_interaction()
    """
```

### get_current_emotion()

Get the currently active emotion.

```python
def get_current_emotion(self) -> Optional[str]:
    """
    Get the currently active emotion.
    
    Returns:
        Optional[str]: Name of the current emotion, or None if no emotion is active
    
    Error Handling:
        - Returns None if unable to determine current emotion
        - Never throws exceptions
    
    Example:
        current = emotion_manager.get_current_emotion()
        if current:
            print(f"Currently displaying: {current}")
        else:
            print("No emotion currently active")
        
        # State transitions
        if current == 'urgent':
            # Transition to concerned after urgent message
            emotion_manager.trigger_emotion('concerned')
    """
```

## Configuration

### Default Configuration

The system provides sensible defaults for healthcare applications:

```python
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
            duration_ms=4000,  # 4 seconds
            loop=False
        ),
        EMOTION_URGENT: EmotionConfig(
            sequence_name="alert_focused",
            duration_ms=None,  # Indefinite until changed
            loop=True
        ),
        EMOTION_CONCERNED: EmotionConfig(
            sequence_name="empathetic_support",
            duration_ms=5000,  # 5 seconds
            loop=False
        ),
        EMOTION_REQUEST: EmotionConfig(
            sequence_name="attentive_listening",
            duration_ms=3000,  # 3 seconds
            loop=False
        )
    }
```

### Custom Configuration

```python
# Create custom emotion configurations
custom_emotions = {
    'happy': EmotionConfig(
        sequence_name='custom_joy_sequence',
        duration_ms=3000,  # 3 seconds instead of default 4
        loop=False
    ),
    'neutral': EmotionConfig(
        sequence_name='custom_idle_sequence',
        duration_ms=None,  # Indefinite
        loop=True
    ),
    # Add other emotions as needed
}

# Initialize with custom configuration
emotion_manager = EmotionAnimationManager(roboeyes_instance, custom_emotions)
```

### Configuration Validation

The system automatically validates configurations:

```python
# Invalid configurations are replaced with neutral fallback
invalid_config = {
    'happy': EmotionConfig(
        sequence_name='',  # Invalid: empty sequence name
        duration_ms=4000
    )
}

# System will log error and use neutral configuration for 'happy'
emotion_manager = EmotionAnimationManager(roboeyes_instance, invalid_config)
```

## Error Handling

### Error-Safe Design

The EmotionAnimationManager is designed to never break your application:

```python
# All methods include comprehensive error handling
try:
    # This will never throw an exception
    emotion_manager.trigger_emotion('invalid_emotion')
    emotion_manager.update()
    current = emotion_manager.get_current_emotion()
    available = emotion_manager.get_available_emotions()
    is_active = emotion_manager.is_emotion_active('happy')
except Exception:
    # This block will never execute - methods don't throw exceptions
    pass
```

### Automatic Fallback Behavior

```python
# Invalid emotions automatically fallback to neutral
emotion_manager.trigger_emotion('nonexistent_emotion')  # Returns False, uses neutral
emotion_manager.trigger_emotion(None)                   # Returns False, uses neutral
emotion_manager.trigger_emotion('')                     # Returns False, uses neutral

# Animation continues smoothly in all cases
```

### Error Logging

```python
import logging

# Enable logging to see error details
logging.basicConfig(level=logging.INFO)

# Errors are logged but don't break execution
emotion_manager.trigger_emotion('invalid')
# Logs: "Emotion 'invalid' not supported. Available emotions: [...]"
# Returns False, continues with neutral emotion
```

## Integration Examples

### Basic TTS Integration

```python
def speak_with_emotion(text, emotion):
    """Basic pattern for TTS integration."""
    # Trigger emotion first for immediate visual feedback
    success = emotion_manager.trigger_emotion(emotion)
    
    # Speak regardless of emotion success
    tts_engine.speak(text)
    
    if not success:
        print(f"Emotion {emotion} failed, but TTS continues normally")

# Usage
speak_with_emotion("Hello! How can I help you?", EMOTION_HAPPY)
speak_with_emotion("I understand your concern.", EMOTION_CONCERNED)
```

### Healthcare Interaction Pattern

```python
def healthcare_interaction_example():
    """Complete healthcare interaction with emotion coordination."""
    
    # Greeting
    emotion_manager.trigger_emotion(EMOTION_HAPPY)
    tts_engine.speak("Hello! Welcome to our healthcare system.")
    
    # Information gathering
    emotion_manager.trigger_emotion(EMOTION_REQUEST)
    tts_engine.speak("Could you tell me about your symptoms?")
    
    # Show empathy
    emotion_manager.trigger_emotion(EMOTION_CONCERNED)
    tts_engine.speak("I understand this must be concerning for you.")
    
    # Important information
    emotion_manager.trigger_emotion(EMOTION_URGENT)
    tts_engine.speak("This is important information about your medication.")
    
    # Return to neutral
    emotion_manager.trigger_emotion(EMOTION_NEUTRAL)
```

### Error-Safe Integration Pattern

```python
def robust_emotion_trigger(emotion, fallback=EMOTION_NEUTRAL):
    """Robust emotion triggering with fallback."""
    success = emotion_manager.trigger_emotion(emotion)
    if not success:
        # Try fallback
        fallback_success = emotion_manager.trigger_emotion(fallback)
        if not fallback_success:
            print("Warning: Both primary and fallback emotions failed")
        return False
    return True

def error_safe_tts_coordination(text, emotion):
    """TTS coordination that never fails."""
    try:
        # Try to trigger emotion
        emotion_success = robust_emotion_trigger(emotion)
        
        # Always attempt TTS
        try:
            tts_engine.speak(text)
        except Exception as tts_error:
            print(f"TTS failed: {tts_error}")
            # Animation continues even if TTS fails
        
        return emotion_success
        
    except Exception as e:
        print(f"Coordination error: {e}")
        # Ensure safe state
        emotion_manager.trigger_emotion(EMOTION_NEUTRAL)
        return False
```

## Type Hints Reference

Complete type annotations for all public interfaces:

```python
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

# Core types
@dataclass
class EmotionConfig:
    sequence_name: str
    duration_ms: Optional[int] = None
    loop: bool = True

# Main class
class EmotionAnimationManager:
    def __init__(self, 
                 roboeyes_instance: Any,
                 emotion_config: Optional[Dict[str, EmotionConfig]] = None,
                 emotion_mappings: Optional[Dict[str, Any]] = None,
                 config_file_path: Optional[str] = None) -> None: ...
    
    def trigger_emotion(self, emotion_name: str) -> bool: ...
    def update(self) -> None: ...
    def get_available_emotions(self) -> List[str]: ...
    def is_emotion_active(self, emotion_name: str) -> bool: ...
    def get_current_emotion(self) -> Optional[str]: ...

# Constants
EMOTION_HAPPY: str
EMOTION_NEUTRAL: str
EMOTION_URGENT: str
EMOTION_CONCERNED: str
EMOTION_REQUEST: str
VALID_EMOTIONS: set[str]
DEFAULT_EMOTION: str

# Configuration function
def get_default_emotion_configs() -> Dict[str, EmotionConfig]: ...
```

### Usage with Type Checking

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.roboeyes.emotion_animation_streamlined import EmotionAnimationManager

def setup_emotion_system(roboeyes_instance) -> 'EmotionAnimationManager':
    """Type-safe emotion system setup."""
    emotion_manager = EmotionAnimationManager(roboeyes_instance)
    return emotion_manager

def trigger_with_validation(emotion_manager: 'EmotionAnimationManager', 
                          emotion: str) -> bool:
    """Type-safe emotion triggering."""
    available = emotion_manager.get_available_emotions()
    if emotion in available:
        return emotion_manager.trigger_emotion(emotion)
    else:
        print(f"Invalid emotion: {emotion}. Available: {available}")
        return False
```

## Summary

The EmotionAnimationManager API provides:

- **5 core emotions** designed for healthcare and TTS integration
- **Error-safe methods** that never break your application
- **Real-time updates** for smooth animation transitions
- **Simple configuration** with sensible defaults
- **Comprehensive type hints** for development tools
- **Production-ready patterns** for team integration

### Essential Integration Checklist

1. ✅ Initialize with `EmotionAnimationManager(roboeyes_instance)`
2. ✅ Call `emotion_manager.update()` every frame in main loop
3. ✅ Use `trigger_emotion()` with emotion constants
4. ✅ Handle return values for error detection
5. ✅ Trigger emotions before TTS for immediate visual feedback
6. ✅ Use appropriate emotions for interaction context

Your team now has complete API documentation for production-ready emotion-driven animations!