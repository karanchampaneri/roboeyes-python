# Emotion Integration Quick Reference

## Essential Code Pattern

```python
from roboeyes.desktop_roboeyes import DesktopRoboEyes
from roboeyes.emotion_animation import *
from desktop.config import RoboEyesConfig

# 1. Initialize
config = RoboEyesConfig(display_width=128, display_height=64, window_width=800, window_height=600, frame_rate=30)
roboeyes = DesktopRoboEyes(config)

# 2. Main loop - KEEP RUNNING CONTINUOUSLY
while roboeyes.running:
    roboeyes.handle_events()           # Prevent window freezing
    
    # YOUR EMOTION DETECTION HERE
    detected_emotion = detect_emotion()
    if detected_emotion:
        roboeyes.trigger_emotion(detected_emotion)
    
    roboeyes.update()                  # CRITICAL: Renders the face
    roboeyes.clock.tick(30)           # Maintain frame rate
```

## Available Emotions

| Emotion | Constant | Use Case |
|---------|----------|----------|
| Neutral | `EMOTION_NEUTRAL` | Default, calm state |
| Happy | `EMOTION_HAPPY` | Joy, satisfaction, positive |
| Urgent | `EMOTION_URGENT` | Needs attention, alert |
| Concerned | `EMOTION_CONCERNED` | Worry, empathy, understanding |
| Request | `EMOTION_REQUEST` | Listening, waiting for input |

## Key Methods

```python
# Trigger emotion
roboeyes.trigger_emotion(EMOTION_HAPPY)
roboeyes.trigger_emotion(EMOTION_CONCERNED, confidence=0.85)

# Check state
current = roboeyes.get_current_emotion()
available = roboeyes.get_available_emotions()
transitioning = roboeyes.emotion_manager.is_transitioning
```

## Critical Rules

1. **Always call `roboeyes.update()`** - This renders the face
2. **Always call `roboeyes.handle_events()`** - Prevents freezing
3. **Don't block the main loop** - Keep emotion detection fast
4. **Use threading for slow detection** - See full guide for examples
5. **Control detection frequency** - Don't trigger emotions every frame

## Common Mistakes

❌ **Wrong - Missing update()**
```python
while roboeyes.running:
    roboeyes.handle_events()
    roboeyes.trigger_emotion(emotion)
    # Missing: roboeyes.update()
    roboeyes.clock.tick(30)
```

✅ **Correct - Always update()**
```python
while roboeyes.running:
    roboeyes.handle_events()
    roboeyes.trigger_emotion(emotion)
    roboeyes.update()  # Face renders here
    roboeyes.clock.tick(30)
```

❌ **Wrong - Blocking detection**
```python
while roboeyes.running:
    roboeyes.handle_events()
    slow_detection()  # Takes 2 seconds - blocks rendering
    roboeyes.update()
    roboeyes.clock.tick(30)
```

✅ **Correct - Non-blocking detection**
```python
last_detection = 0
while roboeyes.running:
    roboeyes.handle_events()
    
    # Only detect periodically
    if time.time() - last_detection > 1.0:
        emotion = quick_detection()
        if emotion:
            roboeyes.trigger_emotion(emotion)
        last_detection = time.time()
    
    roboeyes.update()
    roboeyes.clock.tick(30)
```

## Performance Tips

- **Detection frequency**: Check emotions every 0.5-2 seconds, not every frame
- **Frame rate**: 30 FPS is usually sufficient
- **Threading**: Use separate thread for slow AI/ML processing
- **Throttling**: Don't trigger the same emotion repeatedly

## Files to Reference

- **Full Guide**: `docs/emotion_animation_integration_guide.md`
- **Simple Example**: `examples/simple_emotion_integration.py`
- **Advanced Example**: `examples/emotion_system_usage_demo.py`