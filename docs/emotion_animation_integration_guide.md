# RoboEyes Emotion Animation Integration Guide

This guide shows developers how to integrate the emotion animation system into their applications to trigger facial animations based on detected emotions while maintaining continuous face rendering.

## Table of Contents
1. [Quick Start](#quick-start)
2. [Basic Integration](#basic-integration)
3. [Continuous Rendering Setup](#continuous-rendering-setup)
4. [Triggering Emotions](#triggering-emotions)
5. [Advanced Usage](#advanced-usage)
6. [Configuration](#configuration)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## Quick Start

### 1. Import Required Components

```python
from roboeyes.desktop_roboeyes import DesktopRoboEyes
from roboeyes.emotion_animation import (
    EMOTION_HAPPY, EMOTION_NEUTRAL, EMOTION_URGENT, 
    EMOTION_CONCERNED, EMOTION_REQUEST
)
from desktop.config import RoboEyesConfig
```

### 2. Initialize RoboEyes with Emotion System

```python
# Create configuration
config = RoboEyesConfig(
    display_width=128,
    display_height=64,
    window_width=800,
    window_height=600,
    frame_rate=30,
    auto_blinker=True  # Keep natural blinking active
)

# Initialize RoboEyes (emotion system is automatically included)
roboeyes = DesktopRoboEyes(config)
```

### 3. Trigger Emotions Based on Detection

```python
# Your emotion detection logic here
detected_emotion = your_emotion_detection_function()

# Trigger the appropriate animation
if detected_emotion == "happy":
    roboeyes.trigger_emotion(EMOTION_HAPPY)
elif detected_emotion == "concerned":
    roboeyes.trigger_emotion(EMOTION_CONCERNED)
elif detected_emotion == "urgent":
    roboeyes.trigger_emotion(EMOTION_URGENT)
# ... etc
```

## Basic Integration

### Complete Minimal Example

```python
#!/usr/bin/env python3
"""
Minimal example showing continuous face rendering with emotion triggers.
"""

import pygame
import time
from roboeyes.desktop_roboeyes import DesktopRoboEyes
from roboeyes.emotion_animation import *
from desktop.config import RoboEyesConfig

def main():
    # Initialize RoboEyes
    config = RoboEyesConfig(
        display_width=128,
        display_height=64,
        window_width=800,
        window_height=600,
        frame_rate=30
    )
    
    roboeyes = DesktopRoboEyes(config)
    
    # Start with neutral emotion
    roboeyes.trigger_emotion(EMOTION_NEUTRAL)
    
    # Main rendering loop
    while roboeyes.running:
        # Handle window events
        roboeyes.handle_events()
        
        # YOUR EMOTION DETECTION CODE GOES HERE
        # Example: detected_emotion = detect_emotion_from_camera()
        
        # Example emotion triggers (replace with your detection logic)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_1]:
            roboeyes.trigger_emotion(EMOTION_NEUTRAL)
        elif keys[pygame.K_2]:
            roboeyes.trigger_emotion(EMOTION_HAPPY)
        elif keys[pygame.K_3]:
            roboeyes.trigger_emotion(EMOTION_URGENT)
        elif keys[pygame.K_4]:
            roboeyes.trigger_emotion(EMOTION_CONCERNED)
        elif keys[pygame.K_5]:
            roboeyes.trigger_emotion(EMOTION_REQUEST)
        
        # Update and render the face (ALWAYS CALL THIS)
        roboeyes.update()
        
        # Maintain frame rate
        roboeyes.clock.tick(config.frame_rate)

if __name__ == "__main__":
    main()
```

## Continuous Rendering Setup

### The Rendering Loop

The key to continuous face rendering is the main loop that constantly updates the display:

```python
# Main rendering loop - keep this running continuously
while roboeyes.running:
    # 1. Handle window events (required)
    roboeyes.handle_events()
    
    # 2. Your emotion detection logic
    detected_emotion = your_emotion_detection()
    
    # 3. Trigger emotions as needed
    if detected_emotion:
        roboeyes.trigger_emotion(detected_emotion)
    
    # 4. Update animations and render (CRITICAL - always call this)
    roboeyes.update()
    
    # 5. Control frame rate
    roboeyes.clock.tick(30)  # 30 FPS
```

### Important Notes:
- **Always call `roboeyes.update()`** - This renders the face and updates animations
- **Always call `roboeyes.handle_events()`** - This prevents the window from freezing
- **Control frame rate** - Use `roboeyes.clock.tick(fps)` to maintain consistent timing
- **Don't block the loop** - Keep emotion detection fast or run it in a separate thread

## Triggering Emotions

### Available Emotions

```python
from roboeyes.emotion_animation import (
    EMOTION_NEUTRAL,    # Calm, reassuring (default state)
    EMOTION_HAPPY,      # Gentle joy, positive
    EMOTION_URGENT,     # Alert, focused attention
    EMOTION_CONCERNED,  # Empathetic, understanding
    EMOTION_REQUEST     # Attentive listening
)
```

### Basic Emotion Triggering

```python
# Simple trigger
roboeyes.trigger_emotion(EMOTION_HAPPY)

# With confidence level (optional)
roboeyes.trigger_emotion(EMOTION_CONCERNED, confidence=0.85)

# Check current state
current = roboeyes.get_current_emotion()
is_transitioning = roboeyes.emotion_manager.is_transitioning
```

### Integration with AI/ML Emotion Detection

```python
def integrate_with_emotion_detection(roboeyes):
    """Example integration with emotion detection system."""
    
    while roboeyes.running:
        roboeyes.handle_events()
        
        # Your emotion detection (replace with actual implementation)
        emotion_result = your_ai_model.detect_emotion(camera_frame)
        
        # Map your detection results to RoboEyes emotions
        emotion_mapping = {
            'joy': EMOTION_HAPPY,
            'neutral': EMOTION_NEUTRAL,
            'worry': EMOTION_CONCERNED,
            'alert': EMOTION_URGENT,
            'listening': EMOTION_REQUEST
        }
        
        # Trigger emotion if confidence is high enough
        if emotion_result['confidence'] > 0.7:
            detected_emotion = emotion_mapping.get(emotion_result['emotion'])
            if detected_emotion:
                roboeyes.trigger_emotion(detected_emotion, 
                                       confidence=emotion_result['confidence'])
        
        # Continue rendering
        roboeyes.update()
        roboeyes.clock.tick(30)
```

### Handling Multiple Emotion Sources

```python
class EmotionController:
    """Manages emotions from multiple sources."""
    
    def __init__(self, roboeyes):
        self.roboeyes = roboeyes
        self.last_emotion_time = {}
        self.emotion_priorities = {
            EMOTION_URGENT: 5,      # Highest priority
            EMOTION_CONCERNED: 4,
            EMOTION_HAPPY: 3,
            EMOTION_REQUEST: 3,
            EMOTION_NEUTRAL: 1      # Lowest priority
        }
    
    def trigger_emotion_with_priority(self, emotion, source="default", confidence=1.0):
        """Trigger emotion considering priority and timing."""
        current_time = time.time()
        
        # Don't spam the same emotion
        if source in self.last_emotion_time:
            if current_time - self.last_emotion_time[source] < 2.0:  # 2 second cooldown
                return False
        
        # Check if this emotion should override current one
        current_emotion = self.roboeyes.get_current_emotion()
        if current_emotion and current_emotion in self.emotion_priorities:
            current_priority = self.emotion_priorities[current_emotion]
            new_priority = self.emotion_priorities.get(emotion, 1)
            
            if new_priority <= current_priority and not self.roboeyes.emotion_manager.is_transitioning:
                return False  # Don't interrupt higher priority emotion
        
        # Trigger the emotion
        result = self.roboeyes.trigger_emotion(emotion, confidence=confidence)
        if result:
            self.last_emotion_time[source] = current_time
        
        return result

# Usage
emotion_controller = EmotionController(roboeyes)

# From different sources
emotion_controller.trigger_emotion_with_priority(EMOTION_HAPPY, source="face_detection")
emotion_controller.trigger_emotion_with_priority(EMOTION_URGENT, source="voice_analysis")
```

## Advanced Usage

### Custom Emotion Configurations

```python
from roboeyes.emotion_animation import AnimationConfig

# Create custom emotion with specific timing
custom_config = AnimationConfig(
    sequence_name="gentle_joy",
    mood=3,  # HAPPY mood
    duration_ms=3000,  # 3 seconds
    transition_duration_ms=1000,  # 1 second transition
    loop=False,
    priority=4
)

# Register custom emotion
roboeyes.emotion_manager.register_emotion_mapping("excited", custom_config)

# Use custom emotion
roboeyes.trigger_emotion("excited")
```

### Monitoring Emotion State

```python
def monitor_emotion_state(roboeyes):
    """Monitor and log emotion state changes."""
    
    last_emotion = None
    
    while roboeyes.running:
        roboeyes.handle_events()
        
        # Check for emotion changes
        current_emotion = roboeyes.get_current_emotion()
        if current_emotion != last_emotion:
            print(f"Emotion changed: {last_emotion} → {current_emotion}")
            last_emotion = current_emotion
        
        # Log transition state
        if roboeyes.emotion_manager.is_transitioning:
            progress = roboeyes.emotion_manager.transition_progress
            print(f"Transitioning... {progress:.1%} complete")
        
        roboeyes.update()
        roboeyes.clock.tick(30)
```

### Threading for Non-Blocking Emotion Detection

```python
import threading
import queue

class ThreadedEmotionDetector:
    """Run emotion detection in separate thread to avoid blocking rendering."""
    
    def __init__(self, roboeyes):
        self.roboeyes = roboeyes
        self.emotion_queue = queue.Queue()
        self.running = True
        self.detection_thread = threading.Thread(target=self._detection_loop)
        self.detection_thread.daemon = True
    
    def start(self):
        """Start the detection thread."""
        self.detection_thread.start()
    
    def stop(self):
        """Stop the detection thread."""
        self.running = False
        self.detection_thread.join()
    
    def _detection_loop(self):
        """Run emotion detection in background thread."""
        while self.running:
            try:
                # Your emotion detection logic here
                emotion_result = your_slow_emotion_detection()
                
                # Put result in queue for main thread
                self.emotion_queue.put(emotion_result)
                
                time.sleep(0.1)  # Detection rate limit
            except Exception as e:
                print(f"Detection error: {e}")
    
    def process_emotions(self):
        """Process detected emotions (call from main thread)."""
        try:
            while not self.emotion_queue.empty():
                emotion_result = self.emotion_queue.get_nowait()
                
                # Trigger emotion based on result
                if emotion_result['confidence'] > 0.7:
                    emotion = emotion_result['emotion']
                    self.roboeyes.trigger_emotion(emotion)
        except queue.Empty:
            pass

# Usage
detector = ThreadedEmotionDetector(roboeyes)
detector.start()

try:
    while roboeyes.running:
        roboeyes.handle_events()
        
        # Process any detected emotions
        detector.process_emotions()
        
        # Continue rendering
        roboeyes.update()
        roboeyes.clock.tick(30)
finally:
    detector.stop()
```

## Configuration

### Loading Custom Emotion Configurations

```python
# Create custom configuration file
emotion_config = {
    "emotion_mappings": {
        "neutral": {
            "sequence_name": "idle_gentle",
            "mood": 0,
            "duration_ms": None,
            "transition_duration_ms": 1000,
            "loop": True,
            "priority": 1
        },
        "happy": {
            "sequence_name": "gentle_joy",
            "mood": 3,
            "duration_ms": 4000,
            "transition_duration_ms": 1500,
            "loop": False,
            "priority": 3
        }
        # ... more emotions
    }
}

# Save to file
import json
with open('my_emotion_config.json', 'w') as f:
    json.dump(emotion_config, f, indent=2)

# Load configuration
from roboeyes.emotion_animation import EmotionAnimationManager
emotion_manager = EmotionAnimationManager(roboeyes, config_file_path='my_emotion_config.json')
```

### Environment-Specific Configurations

```python
# Healthcare environment
healthcare_config = RoboEyesConfig(
    display_width=128,
    display_height=64,
    window_width=1024,
    window_height=768,
    frame_rate=30,
    auto_blinker=True,
    blink_interval=4,  # Slower, more calming blinks
    blink_variation=1
)

# Interactive kiosk environment
kiosk_config = RoboEyesConfig(
    display_width=128,
    display_height=64,
    window_width=800,
    window_height=600,
    frame_rate=60,  # Higher frame rate for responsiveness
    auto_blinker=True,
    blink_interval=2,  # More frequent, alert blinking
    blink_variation=3
)
```

## Best Practices

### 1. Emotion Detection Frequency
```python
# Don't trigger emotions too frequently
class EmotionThrottler:
    def __init__(self, min_interval=2.0):
        self.min_interval = min_interval
        self.last_trigger = {}
    
    def should_trigger(self, emotion):
        now = time.time()
        if emotion in self.last_trigger:
            if now - self.last_trigger[emotion] < self.min_interval:
                return False
        self.last_trigger[emotion] = now
        return True

throttler = EmotionThrottler(min_interval=2.0)  # 2 second minimum between same emotions

if throttler.should_trigger(detected_emotion):
    roboeyes.trigger_emotion(detected_emotion)
```

### 2. Graceful Degradation
```python
def safe_emotion_trigger(roboeyes, emotion, fallback=EMOTION_NEUTRAL):
    """Safely trigger emotion with fallback."""
    try:
        result = roboeyes.trigger_emotion(emotion)
        if not result:
            # Fallback to neutral if trigger failed
            roboeyes.trigger_emotion(fallback)
        return result
    except Exception as e:
        print(f"Emotion trigger error: {e}")
        roboeyes.trigger_emotion(fallback)
        return False
```

### 3. Performance Monitoring
```python
import time

class PerformanceMonitor:
    def __init__(self):
        self.frame_times = []
        self.last_frame_time = time.time()
    
    def update(self):
        now = time.time()
        frame_time = now - self.last_frame_time
        self.frame_times.append(frame_time)
        
        # Keep only last 60 frames
        if len(self.frame_times) > 60:
            self.frame_times.pop(0)
        
        self.last_frame_time = now
    
    def get_fps(self):
        if not self.frame_times:
            return 0
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        return 1.0 / avg_frame_time if avg_frame_time > 0 else 0

monitor = PerformanceMonitor()

while roboeyes.running:
    roboeyes.handle_events()
    
    # Your emotion detection and triggering
    
    roboeyes.update()
    monitor.update()
    
    # Log performance occasionally
    if int(time.time()) % 5 == 0:  # Every 5 seconds
        fps = monitor.get_fps()
        print(f"Current FPS: {fps:.1f}")
    
    roboeyes.clock.tick(30)
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Face Not Rendering
```python
# WRONG - missing update call
while roboeyes.running:
    roboeyes.handle_events()
    roboeyes.trigger_emotion(some_emotion)
    # Missing: roboeyes.update()
    roboeyes.clock.tick(30)

# CORRECT - always call update
while roboeyes.running:
    roboeyes.handle_events()
    roboeyes.trigger_emotion(some_emotion)
    roboeyes.update()  # This renders the face
    roboeyes.clock.tick(30)
```

#### 2. Window Freezing
```python
# WRONG - blocking operation in main loop
while roboeyes.running:
    roboeyes.handle_events()
    
    # This blocks the rendering loop
    slow_emotion_detection()  # Takes 2 seconds
    
    roboeyes.update()
    roboeyes.clock.tick(30)

# CORRECT - use threading or make detection fast
while roboeyes.running:
    roboeyes.handle_events()
    
    # Quick check for cached results
    if emotion_cache.has_new_result():
        emotion = emotion_cache.get_result()
        roboeyes.trigger_emotion(emotion)
    
    roboeyes.update()
    roboeyes.clock.tick(30)
```

#### 3. Emotions Not Changing
```python
# Check if emotion manager is available
if not hasattr(roboeyes, 'emotion_manager') or roboeyes.emotion_manager is None:
    print("Emotion manager not initialized!")
    # Reinitialize or check configuration

# Check if emotions are valid
available_emotions = roboeyes.get_available_emotions()
print(f"Available emotions: {available_emotions}")

# Check current state
current = roboeyes.get_current_emotion()
transitioning = roboeyes.emotion_manager.is_transitioning
print(f"Current: {current}, Transitioning: {transitioning}")
```

#### 4. Performance Issues
```python
# Monitor frame rate
target_fps = 30
actual_fps = roboeyes.clock.get_fps()

if actual_fps < target_fps * 0.8:  # 80% of target
    print(f"Performance warning: {actual_fps:.1f} FPS (target: {target_fps})")
    
    # Reduce detection frequency
    detection_interval = 0.5  # Check emotions every 500ms instead of every frame
    
    # Or reduce frame rate
    roboeyes.clock.tick(20)  # Lower frame rate
```

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check system health
health = roboeyes.emotion_manager.is_animation_system_healthy()
print(f"System health: {health}")

# Force recovery if needed
if not health:
    recovery_result = roboeyes.emotion_manager.recover_from_error()
    print(f"Recovery result: {recovery_result}")
```

## Complete Integration Template

Here's a complete template you can use as a starting point:

```python
#!/usr/bin/env python3
"""
Complete RoboEyes Emotion Animation Integration Template

Replace the emotion detection placeholder with your actual implementation.
"""

import pygame
import time
import threading
import queue
from roboeyes.desktop_roboeyes import DesktopRoboEyes
from roboeyes.emotion_animation import *
from desktop.config import RoboEyesConfig

class EmotionIntegration:
    def __init__(self):
        # Initialize RoboEyes
        self.config = RoboEyesConfig(
            display_width=128,
            display_height=64,
            window_width=800,
            window_height=600,
            frame_rate=30,
            auto_blinker=True
        )
        
        self.roboeyes = DesktopRoboEyes(self.config)
        self.emotion_queue = queue.Queue()
        self.running = True
        
        # Start with neutral emotion
        self.roboeyes.trigger_emotion(EMOTION_NEUTRAL)
        
        # Start emotion detection thread
        self.detection_thread = threading.Thread(target=self._emotion_detection_loop)
        self.detection_thread.daemon = True
        self.detection_thread.start()
    
    def _emotion_detection_loop(self):
        """Background emotion detection (replace with your implementation)."""
        while self.running:
            try:
                # REPLACE THIS with your actual emotion detection
                detected_emotion = self._your_emotion_detection_function()
                
                if detected_emotion:
                    self.emotion_queue.put(detected_emotion)
                
                time.sleep(0.2)  # Detection every 200ms
                
            except Exception as e:
                print(f"Emotion detection error: {e}")
                time.sleep(1)  # Wait before retrying
    
    def _your_emotion_detection_function(self):
        """
        REPLACE THIS with your actual emotion detection logic.
        
        This should return one of:
        - EMOTION_NEUTRAL
        - EMOTION_HAPPY  
        - EMOTION_URGENT
        - EMOTION_CONCERNED
        - EMOTION_REQUEST
        - None (if no emotion detected)
        """
        # Example placeholder - replace with your implementation
        import random
        emotions = [EMOTION_NEUTRAL, EMOTION_HAPPY, EMOTION_CONCERNED, None, None]
        return random.choice(emotions)
    
    def _process_detected_emotions(self):
        """Process emotions from detection thread."""
        try:
            while not self.emotion_queue.empty():
                emotion = self.emotion_queue.get_nowait()
                if emotion:
                    self.roboeyes.trigger_emotion(emotion)
        except queue.Empty:
            pass
    
    def run(self):
        """Main rendering loop."""
        print("Starting RoboEyes with emotion detection...")
        print("Press ESC to exit")
        
        try:
            while self.roboeyes.running and self.running:
                # Handle window events
                self.roboeyes.handle_events()
                
                # Process any detected emotions
                self._process_detected_emotions()
                
                # Handle manual controls (for testing)
                keys = pygame.key.get_pressed()
                if keys[pygame.K_1]:
                    self.roboeyes.trigger_emotion(EMOTION_NEUTRAL)
                elif keys[pygame.K_2]:
                    self.roboeyes.trigger_emotion(EMOTION_HAPPY)
                elif keys[pygame.K_3]:
                    self.roboeyes.trigger_emotion(EMOTION_URGENT)
                elif keys[pygame.K_4]:
                    self.roboeyes.trigger_emotion(EMOTION_CONCERNED)
                elif keys[pygame.K_5]:
                    self.roboeyes.trigger_emotion(EMOTION_REQUEST)
                
                # Update and render face (CRITICAL)
                self.roboeyes.update()
                
                # Maintain frame rate
                self.roboeyes.clock.tick(self.config.frame_rate)
                
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.running = False

def main():
    integration = EmotionIntegration()
    integration.run()

if __name__ == "__main__":
    main()
```

## Summary

The key points for successful integration:

1. **Keep the rendering loop running** - Always call `roboeyes.update()` and `roboeyes.handle_events()`
2. **Don't block the main thread** - Use threading for slow emotion detection
3. **Trigger emotions as needed** - Call `roboeyes.trigger_emotion(emotion)` when you detect emotions
4. **Handle errors gracefully** - Use try/catch and fallback emotions
5. **Monitor performance** - Keep frame rate stable for smooth animations
6. **Test thoroughly** - Use the provided examples and debug tools

The emotion animation system is designed to work seamlessly with continuous face rendering while providing smooth, contextually appropriate animations based on detected emotions.