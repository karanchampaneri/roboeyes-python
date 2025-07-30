# RoboEyes Examples - Team Integration Focus

This directory contains focused examples for team integration with the EmotionAnimationManager system. These examples demonstrate essential patterns for integrating emotion-driven eye animations with TTS systems and AI applications.

## Core Team Examples

### `simple_emotion_integration.py`
**Essential starting point for new team members**
- Minimal code needed for emotion animation integration
- Shows basic EmotionAnimationManager usage patterns
- Includes placeholder for your AI/ML emotion detection
- Manual testing controls for development
- Clear error handling that maintains animation continuity

**Perfect for:**
- Team members new to the emotion animation system
- Basic emotion-driven eye animations
- Integration with AI/ML emotion detection models
- Development and testing workflows

**Usage:**
```bash
python examples/simple_emotion_integration.py
```

### `team_integration_guide.py`
**Complete TTS integration template**
- Shows how to coordinate EmotionAnimationManager with TTS systems
- Thread-safe TTS and emotion coordination
- Healthcare application examples
- Proper error handling patterns
- Best practices for emotion timing with speech

**Perfect for:**
- TTS system integration projects
- Healthcare applications requiring empathetic interactions
- Production-ready emotion coordination
- Team development templates

**Usage:**
```bash
python examples/team_integration_guide.py
```

### `realtime_emotion_chaining_demo.py`
**Real-time emotion chaining demonstration**
- Shows seamless emotion transitions during pygame rendering
- Demonstrates emotion chaining for TTS integration scenarios
- Interactive demo with multiple emotion chain examples
- Clear team integration patterns with detailed comments

**Perfect for:**
- Understanding real-time emotion transitions
- Learning emotion chaining patterns
- TTS coordination timing examples
- Interactive demonstrations for team training

**Usage:**
```bash
python examples/realtime_emotion_chaining_demo.py
```

## Quick Start Guide

### For New Team Members
1. **Start with `simple_emotion_integration.py`** to understand basic usage
2. **Explore `realtime_emotion_chaining_demo.py`** to see emotion transitions
3. **Use `team_integration_guide.py`** as a template for TTS projects

### For TTS Integration Projects
1. **Copy `team_integration_guide.py`** as your starting template
2. **Replace the placeholder TTS function** with your actual TTS implementation
3. **Customize the healthcare examples** for your specific use case
4. **Test with `realtime_emotion_chaining_demo.py`** to understand timing

### For AI/ML Integration
1. **Start with `simple_emotion_integration.py`**
2. **Replace `your_emotion_detection_function()`** with your AI/ML model
3. **Adjust detection timing** based on your model's performance
4. **Use error handling patterns** to maintain animation continuity

## Available Emotions

All examples use these five core emotions optimized for healthcare applications:

- **`EMOTION_NEUTRAL`** - Calm, idle state (default)
- **`EMOTION_HAPPY`** - Joy, satisfaction, positive responses
- **`EMOTION_CONCERNED`** - Empathy, worry, supportive responses
- **`EMOTION_URGENT`** - Alert, important information, attention needed
- **`EMOTION_REQUEST`** - Listening, questions, information gathering

## Integration Patterns

### Basic Emotion Triggering
```python
# Initialize emotion manager
emotion_manager = EmotionAnimationManager(roboeyes)

# Trigger emotions based on context
emotion_manager.trigger_emotion(EMOTION_HAPPY)  # For positive interactions
emotion_manager.trigger_emotion(EMOTION_CONCERNED)  # For empathetic responses
```

### Real-time Updates (Critical)
```python
# In your main loop - call every frame for smooth transitions
while running:
    emotion_manager.update()  # Essential for real-time emotion chaining
    roboeyes.update()         # Essential for animation rendering
```

### TTS Coordination
```python
# Coordinate emotions with speech timing
coordinator.speak_with_emotion("Hello! How can I help?", EMOTION_HAPPY)
coordinator.speak_with_emotion("I understand your concern", EMOTION_CONCERNED)
```

## Error Handling Best Practices

All examples demonstrate error handling that:
- **Never breaks the animation loop** - pygame rendering continues
- **Provides clear error messages** - helps with debugging
- **Falls back to neutral emotion** - maintains consistent state
- **Logs errors appropriately** - for monitoring and debugging

## Requirements

All examples require:
- Python 3.7+
- Pygame
- The streamlined EmotionAnimationManager (in `src/roboeyes/`)

Install requirements:
```bash
pip install pygame
```

## Development Workflow

1. **Use manual testing controls** during development (number keys 1-5)
2. **Monitor console output** for emotion triggers and errors
3. **Test error scenarios** to ensure animation continuity
4. **Remove manual controls** for production deployment

## Getting Started

1. **For new team members**, start with `simple_emotion_integration.py` to understand the basics
2. **For real-time emotion understanding**, explore `realtime_emotion_chaining_demo.py`
3. **For TTS integration projects**, use `team_integration_guide.py` as your template

## Common Controls

All examples support these common controls:
- **Number keys 1-5**: Trigger different emotions manually
- **ESC**: Exit the application
- **H** or **F1**: Show/hide help (where available)

See individual example documentation for specific controls and usage patterns.