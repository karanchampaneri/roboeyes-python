# Team Integration Guide - EmotionAnimationManager

This guide provides comprehensive patterns for integrating the EmotionAnimationManager with TTS systems, healthcare applications, and AI assistants. Follow these patterns for production-ready emotion-driven animations that coordinate seamlessly with your applications.

## Table of Contents

1. [Quick Start for Teams](#quick-start-for-teams)
2. [Core Integration Patterns](#core-integration-patterns)
3. [TTS Coordination](#tts-coordination)
4. [Healthcare Application Examples](#healthcare-application-examples)
5. [Error Handling Best Practices](#error-handling-best-practices)
6. [Advanced Integration Patterns](#advanced-integration-patterns)
7. [Performance Guidelines](#performance-guidelines)
8. [Troubleshooting](#troubleshooting)

## Quick Start for Teams

### 1. Basic Setup

```python
from src.roboeyes.desktop_roboeyes import DesktopRoboEyes
from src.roboeyes.emotion_animation_streamlined import (
    EmotionAnimationManager,
    EMOTION_HAPPY, EMOTION_NEUTRAL, EMOTION_URGENT, 
    EMOTION_CONCERNED, EMOTION_REQUEST
)
from src.desktop.config import RoboEyesConfig

# Initialize RoboEyes with team-recommended settings
config = RoboEyesConfig(
    display_width=128,
    display_height=64,
    window_width=800,
    window_height=600,
    frame_rate=30,        # 30 FPS for smooth emotion transitions
    auto_blinker=True     # Maintain natural blinking
)

roboeyes = DesktopRoboEyes(config)
emotion_manager = EmotionAnimationManager(roboeyes)
```

### 2. Essential Main Loop Pattern

```python
# CRITICAL PATTERN: Every team integration must follow this structure
while roboeyes.running:
    # Handle pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            roboeyes.running = False
    
    # Your application logic here
    # - TTS coordination
    # - User input handling
    # - AI processing
    
    # CRITICAL: Update emotion manager every frame
    emotion_manager.update()  # Enables smooth transitions
    
    # CRITICAL: Update RoboEyes every frame  
    roboeyes.update()         # Maintains animations
    
    # Control frame rate
    roboeyes.clock.tick(30)   # 30 FPS recommended
```

### 3. Basic Emotion Triggering

```python
# Get available emotions
available = emotion_manager.get_available_emotions()
# Returns: ['happy', 'neutral', 'urgent', 'concerned', 'request']

# Trigger emotions safely
success = emotion_manager.trigger_emotion(EMOTION_HAPPY)
if not success:
    # Automatic fallback to neutral - animation continues smoothly
    print("Emotion trigger failed, system continues normally")

# Check current state
current_emotion = emotion_manager.get_current_emotion()
is_happy_active = emotion_manager.is_emotion_active(EMOTION_HAPPY)
```## Core I
ntegration Patterns

### Pattern 1: Replace Direct TTS Calls

**Before (Basic TTS):**
```python
tts_engine.speak("Hello! How can I help you?")
```

**After (Emotion-Coordinated TTS):**
```python
emotion_manager.trigger_emotion(EMOTION_HAPPY)
tts_engine.speak("Hello! How can I help you?")
# Emotion transitions automatically via update() calls
```

### Pattern 2: Emotion Chaining for Complex Interactions

```python
def healthcare_greeting_sequence():
    """Example of chaining emotions for natural interaction."""
    
    # Start with neutral baseline
    emotion_manager.trigger_emotion(EMOTION_NEUTRAL)
    time.sleep(0.5)  # Brief pause
    
    # Happy greeting
    emotion_manager.trigger_emotion(EMOTION_HAPPY)
    tts_engine.speak("Hello! Welcome to our healthcare system.")
    
    # Transition to attentive listening
    emotion_manager.trigger_emotion(EMOTION_REQUEST)
    tts_engine.speak("How can I help you today?")
    
    # Return to neutral for user response
    emotion_manager.trigger_emotion(EMOTION_NEUTRAL)
```

### Pattern 3: Emotion State Management

```python
def smart_emotion_trigger(target_emotion):
    """Only trigger emotion if not already active."""
    current = emotion_manager.get_current_emotion()
    
    if current != target_emotion:
        success = emotion_manager.trigger_emotion(target_emotion)
        if success:
            print(f"Transitioned from {current} to {target_emotion}")
        else:
            print(f"Failed to transition to {target_emotion}")
    else:
        print(f"Already in {target_emotion} emotion")
```

## TTS Coordination

### Simple TTS Integration

```python
class SimpleTTSCoordinator:
    """Basic TTS-emotion coordination for teams."""
    
    def __init__(self, emotion_manager, tts_engine):
        self.emotion_manager = emotion_manager
        self.tts_engine = tts_engine
    
    def speak_with_emotion(self, text, emotion):
        """Coordinate TTS with emotion display."""
        # Trigger emotion first for immediate visual feedback
        success = self.emotion_manager.trigger_emotion(emotion)
        
        # Speak regardless of emotion success
        self.tts_engine.speak(text)
        
        if not success:
            print(f"Emotion {emotion} failed, but TTS continues")
    
    def speak_sequence(self, messages):
        """Speak multiple messages with coordinated emotions."""
        for text, emotion in messages:
            self.speak_with_emotion(text, emotion)
            # Add delay between messages if needed
            time.sleep(0.5)

# Usage example
coordinator = SimpleTTSCoordinator(emotion_manager, your_tts_engine)

# Single message
coordinator.speak_with_emotion("Hello!", EMOTION_HAPPY)

# Message sequence
messages = [
    ("Hello! Welcome to our system.", EMOTION_HAPPY),
    ("How can I help you today?", EMOTION_REQUEST),
    ("I'm here to assist you.", EMOTION_NEUTRAL)
]
coordinator.speak_sequence(messages)
```##
 Healthcare Application Examples

### Patient Interaction Scenarios

```python
class HealthcareInteractionManager:
    """Healthcare-specific emotion patterns."""
    
    def __init__(self, emotion_manager, tts_coordinator):
        self.emotion_manager = emotion_manager
        self.tts = tts_coordinator
    
    def greeting_sequence(self):
        """Standard patient greeting."""
        self.tts.speak_with_emotion(
            "Hello! Welcome to our healthcare system. I'm here to help you today.",
            EMOTION_HAPPY
        )
    
    def symptom_inquiry(self):
        """Gather symptom information."""
        self.tts.speak_with_emotion(
            "Could you please tell me about your symptoms?",
            EMOTION_REQUEST
        )
        
        self.tts.speak_with_emotion(
            "When did these symptoms first start?",
            EMOTION_REQUEST
        )
    
    def show_empathy(self, concern_level="normal"):
        """Show appropriate empathy based on situation."""
        if concern_level == "high":
            self.tts.speak_with_emotion(
                "I understand this must be very concerning for you. Let me help you with that.",
                EMOTION_CONCERNED
            )
        else:
            self.tts.speak_with_emotion(
                "I can see you're worried about this. That's completely understandable.",
                EMOTION_CONCERNED
            )
    
    def deliver_urgent_info(self, message):
        """Deliver important medical information."""
        self.tts.speak_with_emotion(
            "This is important information. Please pay close attention.",
            EMOTION_URGENT
        )
        
        self.tts.speak_with_emotion(message, EMOTION_URGENT)
    
    def provide_reassurance(self):
        """Provide positive reassurance."""
        self.tts.speak_with_emotion(
            "Everything looks good with your results. You're doing great!",
            EMOTION_HAPPY
        )
    
    def closing_sequence(self):
        """Standard interaction closing."""
        self.tts.speak_with_emotion(
            "Thank you for your time today. Take care and feel better soon!",
            EMOTION_HAPPY
        )
        
        # Return to neutral for next patient
        self.emotion_manager.trigger_emotion(EMOTION_NEUTRAL)

# Usage example
healthcare_manager = HealthcareInteractionManager(emotion_manager, tts_coordinator)

# Complete patient interaction
healthcare_manager.greeting_sequence()
healthcare_manager.symptom_inquiry()
healthcare_manager.show_empathy("high")
healthcare_manager.provide_reassurance()
healthcare_manager.closing_sequence()
```

### Medication Management Example

```python
def medication_reminder_system(emotion_manager, tts_coordinator):
    """Example medication reminder with appropriate emotions."""
    
    # Get patient attention
    emotion_manager.trigger_emotion(EMOTION_REQUEST)
    tts_coordinator.speak("It's time for your medication reminder.")
    
    # Deliver important information
    emotion_manager.trigger_emotion(EMOTION_URGENT)
    tts_coordinator.speak("Please take your blood pressure medication now.")
    
    # Provide instructions
    emotion_manager.trigger_emotion(EMOTION_NEUTRAL)
    tts_coordinator.speak("Take one tablet with water, as prescribed by your doctor.")
    
    # Positive reinforcement
    emotion_manager.trigger_emotion(EMOTION_HAPPY)
    tts_coordinator.speak("Thank you for staying on track with your medication!")
    
    # Return to neutral
    emotion_manager.trigger_emotion(EMOTION_NEUTRAL)
```## 
Error Handling Best Practices

### Robust Error Handling Pattern

```python
def safe_emotion_trigger(emotion_manager, emotion, fallback=EMOTION_NEUTRAL):
    """Safely trigger emotion with automatic fallback."""
    try:
        success = emotion_manager.trigger_emotion(emotion)
        if not success:
            # Try fallback emotion
            emotion_manager.trigger_emotion(fallback)
            return False
        return True
    except Exception as e:
        # Log error but don't break application
        print(f"Emotion error: {e}")
        try:
            emotion_manager.trigger_emotion(fallback)
        except:
            pass  # Even fallback failed, but app continues
        return False

def error_safe_tts_integration(emotion_manager, tts_engine, text, emotion):
    """TTS integration that never breaks the animation loop."""
    try:
        # Try to trigger emotion
        emotion_success = safe_emotion_trigger(emotion_manager, emotion)
        
        # Try TTS regardless of emotion success
        try:
            tts_engine.speak(text)
        except Exception as tts_error:
            print(f"TTS error: {tts_error}")
            # Animation continues even if TTS fails
        
        return emotion_success
        
    except Exception as e:
        print(f"Integration error: {e}")
        # Ensure we return to a safe state
        safe_emotion_trigger(emotion_manager, EMOTION_NEUTRAL)
        return False
```

## Performance Guidelines

### Optimal Frame Rate and Timing

```python
# Recommended settings for different use cases
PERFORMANCE_CONFIGS = {
    'high_quality': {
        'frame_rate': 30,
        'emotion_update_interval': 0.033,  # Every frame
        'tts_check_interval': 0.1          # 10 times per second
    },
    'balanced': {
        'frame_rate': 24,
        'emotion_update_interval': 0.042,  # Every frame
        'tts_check_interval': 0.2          # 5 times per second
    },
    'performance': {
        'frame_rate': 20,
        'emotion_update_interval': 0.05,   # Every frame
        'tts_check_interval': 0.25         # 4 times per second
    }
}

def configure_for_performance(config_name='balanced'):
    """Configure system for optimal performance."""
    config = PERFORMANCE_CONFIGS.get(config_name, PERFORMANCE_CONFIGS['balanced'])
    
    roboeyes_config = RoboEyesConfig(
        frame_rate=config['frame_rate'],
        # ... other settings
    )
    
    return roboeyes_config, config
```

## Troubleshooting

### Common Integration Issues

**Issue: Emotions not transitioning smoothly**
```python
# Problem: Not calling update() every frame
while running:
    # Missing: emotion_manager.update()
    roboeyes.update()

# Solution: Always call update() every frame
while running:
    emotion_manager.update()  # CRITICAL
    roboeyes.update()
    clock.tick(30)
```

**Issue: TTS and emotions out of sync**
```python
# Problem: Triggering emotions too late
tts_engine.speak("Hello!")
emotion_manager.trigger_emotion(EMOTION_HAPPY)  # Too late

# Solution: Trigger emotion first
emotion_manager.trigger_emotion(EMOTION_HAPPY)  # Visual feedback first
tts_engine.speak("Hello!")
```

**Issue: Application freezing during TTS**
```python
# Problem: Blocking TTS call
tts_engine.speak_and_wait("Long message...")  # Blocks main loop

# Solution: Use async TTS or non-blocking calls
tts_engine.speak_async("Long message...")
# Main loop continues running
```

## Summary

This guide provides comprehensive patterns for integrating EmotionAnimationManager with your team's applications. Key takeaways:

1. **Always call `emotion_manager.update()` every frame** - This is critical for smooth transitions
2. **Trigger emotions before TTS** - Provides immediate visual feedback
3. **Handle errors gracefully** - Never let emotion errors break your application
4. **Use appropriate emotions for context** - Match emotions to interaction types
5. **Monitor performance** - Ensure smooth operation in production

For additional examples and templates, see the `examples/` directory, particularly:
- `simple_emotion_integration.py` - Basic integration template
- `team_integration_guide.py` - Complete TTS coordination example
- `realtime_emotion_chaining_demo.py` - Advanced chaining patterns

Your team now has production-ready patterns for emotion-driven animations that enhance user experience while maintaining system reliability.