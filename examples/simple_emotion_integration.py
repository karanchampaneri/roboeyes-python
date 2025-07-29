#!/usr/bin/env python3
"""
Simple Emotion Integration Example

This example shows the minimal code needed to integrate emotion detection
with continuous face rendering. Replace the placeholder emotion detection
with your actual implementation.
"""

import pygame
import time
import random
from roboeyes.desktop_roboeyes import DesktopRoboEyes
from roboeyes.emotion_animation import (
    EMOTION_HAPPY, EMOTION_NEUTRAL, EMOTION_URGENT, 
    EMOTION_CONCERNED, EMOTION_REQUEST
)
from desktop.config import RoboEyesConfig

def your_emotion_detection_function():
    """
    REPLACE THIS with your actual emotion detection logic.
    
    This function should:
    1. Capture/analyze input (camera, audio, sensors, etc.)
    2. Process the data through your AI/ML model
    3. Return the detected emotion or None
    
    Returns:
        str: One of the emotion constants (EMOTION_HAPPY, etc.) or None
    """
    # Example placeholder - replace with your implementation
    # This randomly returns emotions for demonstration
    emotions = [
        EMOTION_NEUTRAL,    # Most common - calm state
        EMOTION_HAPPY,      # Detected joy/satisfaction  
        EMOTION_CONCERNED,  # Detected worry/uncertainty
        EMOTION_URGENT,     # Detected need for attention
        EMOTION_REQUEST,    # Detected request/question
        None,               # No clear emotion detected
        None,               # No clear emotion detected
    ]
    
    # Simulate detection delay and randomness
    if random.random() < 0.3:  # 30% chance of detecting emotion
        return random.choice(emotions[:-2])  # Exclude None values
    return None

def main():
    """Main application with continuous rendering and emotion detection."""
    
    # 1. Initialize RoboEyes with emotion system
    config = RoboEyesConfig(
        display_width=128,
        display_height=64,
        window_width=800,
        window_height=600,
        frame_rate=30,
        auto_blinker=True  # Keep natural blinking
    )
    
    roboeyes = DesktopRoboEyes(config)
    
    # 2. Start with neutral emotion
    roboeyes.trigger_emotion(EMOTION_NEUTRAL)
    
    # 3. Setup emotion detection timing
    last_detection_time = 0
    detection_interval = 1.0  # Check for emotions every 1 second
    
    print("RoboEyes running with emotion detection...")
    print("Manual controls: 1=Neutral, 2=Happy, 3=Urgent, 4=Concerned, 5=Request")
    print("Press ESC to exit")
    
    # 4. Main rendering loop - KEEP THIS RUNNING CONTINUOUSLY
    try:
        while roboeyes.running:
            current_time = time.time()
            
            # Handle window events (prevents freezing)
            roboeyes.handle_events()
            
            # Periodic emotion detection (don't do this every frame)
            if current_time - last_detection_time >= detection_interval:
                detected_emotion = your_emotion_detection_function()
                
                if detected_emotion:
                    print(f"Detected emotion: {detected_emotion}")
                    roboeyes.trigger_emotion(detected_emotion)
                
                last_detection_time = current_time
            
            # Manual testing controls (remove in production)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_1]:
                roboeyes.trigger_emotion(EMOTION_NEUTRAL)
                print("Manual trigger: Neutral")
            elif keys[pygame.K_2]:
                roboeyes.trigger_emotion(EMOTION_HAPPY)
                print("Manual trigger: Happy")
            elif keys[pygame.K_3]:
                roboeyes.trigger_emotion(EMOTION_URGENT)
                print("Manual trigger: Urgent")
            elif keys[pygame.K_4]:
                roboeyes.trigger_emotion(EMOTION_CONCERNED)
                print("Manual trigger: Concerned")
            elif keys[pygame.K_5]:
                roboeyes.trigger_emotion(EMOTION_REQUEST)
                print("Manual trigger: Request")
            
            # Update and render the face (CRITICAL - always call this)
            roboeyes.update()
            
            # Control frame rate (keeps animations smooth)
            roboeyes.clock.tick(config.frame_rate)
            
    except KeyboardInterrupt:
        print("\nShutting down...")
    
    print("RoboEyes stopped")

if __name__ == "__main__":
    main()