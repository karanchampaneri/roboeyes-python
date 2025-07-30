#!/usr/bin/env python3
"""
Simple Emotion Integration Example

This example shows the minimal code needed to integrate emotion detection
with continuous face rendering using the streamlined EmotionAnimationManager.

Perfect for team members new to the system - demonstrates core functionality
without complex configuration or advanced features.

Key Features:
- Simple EmotionAnimationManager initialization
- Basic emotion triggering patterns
- Real-time animation updates
- Manual testing controls for development
- Clear error handling that maintains animation continuity
"""

import pygame
import time
import random
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from roboeyes.desktop_roboeyes import DesktopRoboEyes
from roboeyes.emotion_animation_streamlined import (
    EmotionAnimationManager,
    EMOTION_HAPPY, EMOTION_NEUTRAL, EMOTION_URGENT, 
    EMOTION_CONCERNED, EMOTION_REQUEST
)
from desktop.config import RoboEyesConfig

def your_emotion_detection_function():
    """
    REPLACE THIS with your actual emotion detection logic.
    
    This function demonstrates the pattern for integrating your AI/ML models
    with the emotion animation system. Replace this placeholder with your
    actual emotion detection implementation.
    
    Integration Steps:
    1. Capture/analyze input (camera, audio, sensors, etc.)
    2. Process the data through your AI/ML model
    3. Return the detected emotion using the emotion constants
    
    Returns:
        str: One of the emotion constants (EMOTION_HAPPY, etc.) or None
        
    Example Integration:
        def your_emotion_detection_function():
            # Your actual implementation might look like:
            # image = capture_camera_frame()
            # emotion_scores = your_ml_model.predict(image)
            # return map_scores_to_emotion(emotion_scores)
            pass
    """
    # DEMO PLACEHOLDER - Replace with your implementation
    # This randomly returns emotions for demonstration purposes
    demo_emotions = [
        EMOTION_NEUTRAL,    # Most common - calm/idle state
        EMOTION_HAPPY,      # Detected joy/satisfaction/positive response
        EMOTION_CONCERNED,  # Detected worry/uncertainty/empathy needed
        EMOTION_URGENT,     # Detected need for immediate attention
        EMOTION_REQUEST,    # Detected question/request for information
        None,               # No clear emotion detected
        None,               # No clear emotion detected (more common)
    ]
    
    # Simulate realistic detection patterns (30% detection rate)
    if random.random() < 0.3:
        return random.choice(demo_emotions[:-2])  # Exclude None values
    return None

def main():
    """
    Main application demonstrating simple emotion integration.
    
    This function shows the essential pattern for integrating emotion
    animations with your application. Follow this structure for basic
    emotion-driven eye animations.
    
    Key Integration Points:
    1. Initialize RoboEyes and EmotionAnimationManager
    2. Set up emotion detection timing
    3. Call emotion_manager.update() every frame
    4. Handle errors gracefully to maintain animation continuity
    """
    print("Simple Emotion Integration Example")
    print("=================================")
    print("This example shows basic emotion animation integration for teams.")
    print("Replace the placeholder emotion detection with your AI/ML model.")
    print()
    
    # 1. Initialize RoboEyes with standard configuration
    try:
        config = RoboEyesConfig(
            display_width=128,
            display_height=64,
            window_width=800,
            window_height=600,
            frame_rate=30,        # 30 FPS for smooth animations
            auto_blinker=True     # Keep natural blinking behavior
        )
        
        roboeyes = DesktopRoboEyes(config)
        print("✓ RoboEyes initialized successfully")
        
    except Exception as e:
        print(f"✗ Failed to initialize RoboEyes: {e}")
        return
    
    # 2. Initialize emotion animation manager (streamlined version)
    try:
        emotion_manager = EmotionAnimationManager(roboeyes)
        print("✓ EmotionAnimationManager initialized")
        
        # Show available emotions for reference
        available = emotion_manager.get_available_emotions()
        print(f"✓ Available emotions: {available}")
        
    except Exception as e:
        print(f"✗ Failed to initialize EmotionAnimationManager: {e}")
        return
    
    # 3. Start with neutral emotion (good practice)
    try:
        success = emotion_manager.trigger_emotion(EMOTION_NEUTRAL)
        if success:
            print("✓ Started with neutral emotion")
        else:
            print("⚠ Failed to set initial neutral emotion, continuing anyway")
    except Exception as e:
        print(f"⚠ Error setting initial emotion: {e}, continuing anyway")
    
    # 4. Setup emotion detection timing
    last_detection_time = 0
    detection_interval = 1.0  # Check for emotions every 1 second (adjust as needed)
    
    print("\n🤖 RoboEyes running with emotion detection...")
    print("📝 Integration Notes:")
    print("   • Replace your_emotion_detection_function() with your AI/ML model")
    print("   • emotion_manager.update() is called every frame for smooth transitions")
    print("   • Error handling maintains animation continuity")
    print("   • Manual controls available for testing (see below)")
    print()
    print("🎮 Manual Testing Controls:")
    print("   1 = Neutral  |  2 = Happy  |  3 = Urgent  |  4 = Concerned  |  5 = Request")
    print("   ESC = Exit")
    print()
    
    # 5. Main rendering loop - CRITICAL PATTERN FOR TEAMS
    try:
        while roboeyes.running:
            current_time = time.time()
            
            # Handle pygame events (essential for window management)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    roboeyes.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        roboeyes.running = False
            
            # Periodic emotion detection (don't run every frame for performance)
            if current_time - last_detection_time >= detection_interval:
                try:
                    detected_emotion = your_emotion_detection_function()
                    
                    if detected_emotion:
                        success = emotion_manager.trigger_emotion(detected_emotion)
                        if success:
                            print(f"😊 Detected and triggered: {detected_emotion}")
                        else:
                            print(f"⚠ Detected {detected_emotion} but trigger failed")
                    
                    last_detection_time = current_time
                    
                except Exception as e:
                    print(f"⚠ Error in emotion detection: {e}")
                    # Continue running - don't let detection errors break the loop
            
            # Manual testing controls (useful for development - remove in production)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_1]:
                emotion_manager.trigger_emotion(EMOTION_NEUTRAL)
                print("🎮 Manual trigger: Neutral")
            elif keys[pygame.K_2]:
                emotion_manager.trigger_emotion(EMOTION_HAPPY)
                print("🎮 Manual trigger: Happy")
            elif keys[pygame.K_3]:
                emotion_manager.trigger_emotion(EMOTION_URGENT)
                print("🎮 Manual trigger: Urgent")
            elif keys[pygame.K_4]:
                emotion_manager.trigger_emotion(EMOTION_CONCERNED)
                print("🎮 Manual trigger: Concerned")
            elif keys[pygame.K_5]:
                emotion_manager.trigger_emotion(EMOTION_REQUEST)
                print("🎮 Manual trigger: Request")
            
            # CRITICAL: Update emotion manager every frame for smooth transitions
            # This is essential for real-time emotion chaining and seamless animations
            try:
                emotion_manager.update()
            except Exception as e:
                print(f"⚠ Error updating emotion manager: {e}")
                # Continue - don't let update errors break the animation loop
            
            # CRITICAL: Update and render RoboEyes every frame
            # This maintains the animation loop and prevents window freezing
            try:
                roboeyes.update()
            except Exception as e:
                print(f"⚠ Error updating RoboEyes: {e}")
                # Continue - try to maintain the loop even with render errors
            
            # Control frame rate for smooth animations
            roboeyes.clock.tick(config.frame_rate)
            
    except KeyboardInterrupt:
        print("\n⏹ Shutting down gracefully...")
    
    except Exception as e:
        print(f"\n✗ Unexpected error in main loop: {e}")
        print("This demonstrates error handling that maintains system stability")
    
    finally:
        print("✓ RoboEyes stopped cleanly")
        print("\n📚 Next Steps for Your Team:")
        print("1. Replace your_emotion_detection_function() with your AI/ML model")
        print("2. Adjust detection_interval based on your model's performance")
        print("3. Remove manual testing controls for production deployment")
        print("4. Consider using team_integration_guide.py for TTS coordination")

if __name__ == "__main__":
    main()