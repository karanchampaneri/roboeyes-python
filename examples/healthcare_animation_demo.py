#!/usr/bin/env python3
"""
Healthcare Animation Demonstration

This script demonstrates the healthcare-appropriate animation sequences
implemented for the RoboEyes emotion system. It cycles through each
emotion category to show how the animations look in practice.
"""

import sys
import os
import time
import pygame

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from roboeyes.desktop_roboeyes import DesktopRoboEyes
from roboeyes.emotion_animation import (
    EMOTION_HAPPY, EMOTION_NEUTRAL, EMOTION_URGENT, 
    EMOTION_CONCERNED, EMOTION_REQUEST
)
from desktop.config import RoboEyesConfig

def main():
    """Run the healthcare animation demonstration."""
    print("Healthcare Animation Demonstration")
    print("=" * 50)
    print("This demo shows healthcare-appropriate animations for patient emotions.")
    print("Press SPACE to cycle through emotions, ESC to exit, H for help.")
    print()
    
    # Create configuration for the demo
    config = RoboEyesConfig(
        display_width=128,
        display_height=64,
        window_width=800,
        window_height=600,
        frame_rate=30,
        auto_blinker=True,
        blink_interval=3,
        blink_variation=2
    )
    
    try:
        # Initialize RoboEyes
        roboeyes = DesktopRoboEyes(config)
        print("✓ RoboEyes initialized successfully")
        
        # Healthcare emotion demonstrations
        emotions_demo = [
            {
                'emotion': EMOTION_NEUTRAL,
                'name': 'Neutral (Idle)',
                'description': 'Calm, reassuring animation for baseline state',
                'context': 'Patient is calm and comfortable',
                'duration': 8
            },
            {
                'emotion': EMOTION_HAPPY,
                'name': 'Happy (Gentle Joy)',
                'description': 'Warm, supportive animation for positive emotions',
                'context': 'Patient is expressing satisfaction or joy',
                'duration': 6
            },
            {
                'emotion': EMOTION_URGENT,
                'name': 'Urgent (Alert Focused)',
                'description': 'Attentive, focused animation for urgent situations',
                'context': 'Patient needs immediate attention',
                'duration': 5
            },
            {
                'emotion': EMOTION_CONCERNED,
                'name': 'Concerned (Empathetic Support)',
                'description': 'Caring, understanding animation for worried patients',
                'context': 'Patient is expressing worry or uncertainty',
                'duration': 7
            },
            {
                'emotion': EMOTION_REQUEST,
                'name': 'Request (Attentive Listening)',
                'description': 'Engaged, listening animation for patient requests',
                'context': 'Patient is making a request or asking for help',
                'duration': 5
            }
        ]
        
        current_demo = 0
        auto_cycle = False
        last_cycle_time = time.time()
        
        # Display initial emotion
        demo = emotions_demo[current_demo]
        roboeyes.trigger_emotion(demo['emotion'])
        print(f"Showing: {demo['name']}")
        print(f"Description: {demo['description']}")
        print(f"Context: {demo['context']}")
        
        # Main demonstration loop
        while roboeyes.running:
            # Handle events
            roboeyes.handle_events()
            
            # Handle keyboard input for manual control
            keys = pygame.key.get_pressed()
            
            # Check for space key press to cycle emotions
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # Cycle to next emotion
                        current_demo = (current_demo + 1) % len(emotions_demo)
                        demo = emotions_demo[current_demo]
                        roboeyes.trigger_emotion(demo['emotion'])
                        
                        print(f"\nShowing: {demo['name']}")
                        print(f"Description: {demo['description']}")
                        print(f"Context: {demo['context']}")
                        
                    elif event.key == pygame.K_a:
                        # Toggle auto-cycle mode
                        auto_cycle = not auto_cycle
                        print(f"\nAuto-cycle mode: {'ON' if auto_cycle else 'OFF'}")
                        last_cycle_time = time.time()
                        
                    elif event.key == pygame.K_h:
                        # Show help
                        print("\nControls:")
                        print("  SPACE - Cycle through emotions")
                        print("  A - Toggle auto-cycle mode")
                        print("  H - Show this help")
                        print("  ESC - Exit")
                        print("  F11 - Toggle fullscreen")
                        
                    elif event.key == pygame.K_1:
                        roboeyes.trigger_emotion(EMOTION_NEUTRAL)
                        print(f"\nManual trigger: {emotions_demo[0]['name']}")
                        
                    elif event.key == pygame.K_2:
                        roboeyes.trigger_emotion(EMOTION_HAPPY)
                        print(f"\nManual trigger: {emotions_demo[1]['name']}")
                        
                    elif event.key == pygame.K_3:
                        roboeyes.trigger_emotion(EMOTION_URGENT)
                        print(f"\nManual trigger: {emotions_demo[2]['name']}")
                        
                    elif event.key == pygame.K_4:
                        roboeyes.trigger_emotion(EMOTION_CONCERNED)
                        print(f"\nManual trigger: {emotions_demo[3]['name']}")
                        
                    elif event.key == pygame.K_5:
                        roboeyes.trigger_emotion(EMOTION_REQUEST)
                        print(f"\nManual trigger: {emotions_demo[4]['name']}")
            
            # Auto-cycle through emotions if enabled
            if auto_cycle:
                current_time = time.time()
                demo = emotions_demo[current_demo]
                
                if current_time - last_cycle_time >= demo['duration']:
                    current_demo = (current_demo + 1) % len(emotions_demo)
                    demo = emotions_demo[current_demo]
                    roboeyes.trigger_emotion(demo['emotion'])
                    
                    print(f"\nAuto-cycle: {demo['name']}")
                    print(f"Description: {demo['description']}")
                    print(f"Context: {demo['context']}")
                    
                    last_cycle_time = current_time
            
            # Update animations
            roboeyes.update()
            
            # Limit frame rate
            roboeyes.clock.tick(config.frame_rate)
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"Demo error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nHealthcare Animation Demo Complete")

if __name__ == "__main__":
    print("Starting Healthcare Animation Demo...")
    print("This demo showcases animations appropriate for medical environments.")
    print()
    main()