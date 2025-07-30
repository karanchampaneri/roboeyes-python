#!/usr/bin/env python3
"""
Real-time Emotion Chaining Demo

This example demonstrates seamless emotion transitions during pygame rendering,
showing how emotions can be chained together for TTS integration scenarios.
Perfect for understanding how to coordinate emotions with speech playback.

Key Features:
- Real-time emotion updates without interrupting animation loop
- Seamless transitions between emotions during pygame rendering
- Emotion chaining patterns for TTS integration
- Clear team integration patterns with detailed comments

Team Integration Patterns:
1. emotion_manager.trigger_emotion() - Primary API for triggering emotions
2. emotion_manager.update() - MUST be called every frame for smooth transitions
3. Emotion chaining - Chain emotions together for complex interactions
4. TTS coordination - Time emotions with speech synthesis playback
5. Animation continuity - Never interrupts pygame rendering loop

Usage for TTS Integration:
```python
# Initialize emotion system
emotion_manager = EmotionAnimationManager(roboeyes_instance)

# During TTS playback, coordinate emotions with speech timing
emotion_manager.trigger_emotion('happy')    # Start of greeting
# ... TTS plays "Hello!"
emotion_manager.trigger_emotion('request')  # Transition to listening
# ... TTS plays "How can I help?"
emotion_manager.trigger_emotion('neutral')  # Return to neutral

# CRITICAL: Call update() every frame in your main loop
while running:
    emotion_manager.update()  # Enables smooth transitions
    roboeyes.update()         # Updates animations
    clock.tick(30)           # Control frame rate
```
"""

import pygame
import time
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


class EmotionChainDemo:
    """
    Demonstrates real-time emotion chaining for TTS integration.
    
    This class shows how to coordinate emotions with speech playback,
    maintaining smooth animations throughout the entire interaction.
    """
    
    def __init__(self):
        """Initialize the demo with RoboEyes and emotion manager."""
        # Configure RoboEyes for smooth real-time rendering
        self.config = RoboEyesConfig(
            display_width=128,
            display_height=64,
            window_width=800,
            window_height=600,
            frame_rate=30,  # 30 FPS for smooth transitions
            auto_blinker=True
        )
        
        # Initialize RoboEyes and emotion system
        self.roboeyes = DesktopRoboEyes(self.config)
        self.emotion_manager = EmotionAnimationManager(self.roboeyes)
        
        # Demo state tracking
        self.demo_start_time = time.time()
        self.current_demo_step = 0
        self.step_start_time = time.time()
        
        # Define emotion chain scenarios for TTS integration
        self.emotion_chains = [
            {
                'name': 'Greeting Sequence',
                'description': 'Typical greeting with TTS: "Hello! How can I help you today?"',
                'chain': [
                    (EMOTION_NEUTRAL, 1.0, "Starting neutral - system ready"),
                    (EMOTION_HAPPY, 2.0, "Happy greeting - 'Hello!'"),
                    (EMOTION_REQUEST, 2.5, "Attentive listening - 'How can I help?'"),
                    (EMOTION_NEUTRAL, 1.0, "Return to neutral - waiting for response")
                ]
            },
            {
                'name': 'Concern and Reassurance',
                'description': 'Responding to user concern: "I understand your worry. Let me help."',
                'chain': [
                    (EMOTION_CONCERNED, 2.0, "Empathetic - 'I understand your worry'"),
                    (EMOTION_NEUTRAL, 0.5, "Brief transition"),
                    (EMOTION_HAPPY, 2.0, "Reassuring - 'Let me help'"),
                    (EMOTION_NEUTRAL, 1.0, "Ready for next interaction")
                ]
            },
            {
                'name': 'Urgent Information',
                'description': 'Delivering urgent info: "This is important! Please pay attention."',
                'chain': [
                    (EMOTION_URGENT, 1.5, "Alert - 'This is important!'"),
                    (EMOTION_URGENT, 2.0, "Maintaining urgency - 'Please pay attention'"),
                    (EMOTION_NEUTRAL, 1.5, "Calming down after urgent message")
                ]
            },
            {
                'name': 'Question and Response',
                'description': 'Interactive Q&A: "Do you have questions?" -> "Great! I\'m listening."',
                'chain': [
                    (EMOTION_REQUEST, 2.0, "Asking - 'Do you have questions?'"),
                    (EMOTION_NEUTRAL, 1.0, "Waiting for user response"),
                    (EMOTION_HAPPY, 1.5, "Positive response - 'Great!'"),
                    (EMOTION_REQUEST, 2.0, "Active listening - 'I'm listening'")
                ]
            }
        ]
    
    def run_demo(self):
        """
        Run the real-time emotion chaining demonstration.
        
        This method shows how emotions update seamlessly during pygame rendering,
        demonstrating patterns that teams can use for TTS integration.
        
        Key Integration Patterns Demonstrated:
        1. Emotion triggering with emotion_manager.trigger_emotion()
        2. Real-time updates with emotion_manager.update() every frame
        3. Emotion chaining for complex interaction scenarios
        4. Animation continuity during emotion transitions
        5. TTS coordination timing patterns
        """
        print("=== Real-time Emotion Chaining Demo ===")
        print("This demo shows seamless emotion transitions for TTS integration")
        print("Watch how emotions chain together without interrupting animations")
        print()
        print("TEAM INTEGRATION PATTERNS:")
        print("• emotion_manager.trigger_emotion(name) - Primary API")
        print("• emotion_manager.update() - Call every frame for smooth transitions")
        print("• Emotion chaining - Coordinate multiple emotions with TTS timing")
        print("• Animation continuity - Never breaks pygame rendering loop")
        print()
        print("Press SPACE to advance to next demo, ESC to exit")
        print()
        
        # Start with neutral emotion
        self.emotion_manager.trigger_emotion(EMOTION_NEUTRAL)
        current_chain = None
        current_step = 0
        step_start_time = time.time()
        waiting_for_input = True
        
        try:
            while self.roboeyes.running:
                current_time = time.time()
                
                # Handle pygame events (essential for window management)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.roboeyes.running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.roboeyes.running = False
                        elif event.key == pygame.K_SPACE:
                            # Advance to next demo chain
                            if waiting_for_input:
                                current_chain = self.emotion_chains[self.current_demo_step % len(self.emotion_chains)]
                                current_step = 0
                                step_start_time = current_time
                                waiting_for_input = False
                                self._print_chain_info(current_chain)
                
                # Execute current emotion chain
                if current_chain and not waiting_for_input:
                    if current_step < len(current_chain['chain']):
                        emotion, duration, description = current_chain['chain'][current_step]
                        
                        # Check if it's time to trigger this emotion
                        if current_step == 0 or (current_time - step_start_time) >= 0.1:
                            if current_step == 0:
                                # First emotion in chain - trigger immediately
                                self.emotion_manager.trigger_emotion(emotion)
                                print(f"  → {emotion.upper()}: {description}")
                                step_start_time = current_time
                                current_step += 1
                            else:
                                # Check if previous emotion duration has elapsed
                                prev_emotion, prev_duration, _ = current_chain['chain'][current_step - 1]
                                if (current_time - step_start_time) >= prev_duration:
                                    # Trigger next emotion in chain
                                    self.emotion_manager.trigger_emotion(emotion)
                                    print(f"  → {emotion.upper()}: {description}")
                                    step_start_time = current_time
                                    current_step += 1
                    else:
                        # Chain completed - wait for next input
                        print(f"  ✓ Chain '{current_chain['name']}' completed!")
                        print("  Press SPACE for next demo...")
                        print()
                        self.current_demo_step += 1
                        current_chain = None
                        waiting_for_input = True
                
                # ========================================
                # CRITICAL TEAM INTEGRATION PATTERN #1:
                # Update emotion manager every frame for real-time transitions
                # This is the key to seamless emotion chaining during pygame rendering
                # WITHOUT this call, emotions won't transition smoothly!
                # ========================================
                self.emotion_manager.update()
                
                # ========================================
                # CRITICAL TEAM INTEGRATION PATTERN #2:
                # Update and render RoboEyes every frame
                # This maintains the animation loop and prevents freezing
                # The emotion system works WITH the animation system, not against it
                # ========================================
                self.roboeyes.update()
                
                # ========================================
                # CRITICAL TEAM INTEGRATION PATTERN #3:
                # Control frame rate for smooth animations
                # 30 FPS provides smooth transitions without excessive CPU usage
                # Perfect for TTS integration where timing matters
                # ========================================
                self.roboeyes.clock.tick(self.config.frame_rate)
                
        except KeyboardInterrupt:
            print("\nDemo interrupted by user")
        
        print("Real-time emotion chaining demo completed")
    
    def _print_chain_info(self, chain):
        """Print information about the current emotion chain."""
        print(f"▶ Starting: {chain['name']}")
        print(f"  Scenario: {chain['description']}")
        print(f"  Emotions: {' → '.join([step[0].upper() for step in chain['chain']])}")
        print("  Transitions:")


def simulate_tts_integration():
    """
    Simulate how emotion chaining works with TTS integration.
    
    This function demonstrates the pattern teams should use when
    coordinating emotions with text-to-speech playback.
    
    TEAM INTEGRATION GUIDE:
    This is the exact pattern to use in your TTS applications!
    """
    print("\n=== TTS Integration Pattern ===")
    print("This shows how to coordinate emotions with speech synthesis")
    print("COPY THIS PATTERN for your TTS applications!")
    print()
    
    # Example TTS integration pattern
    tts_scenarios = [
        {
            'text': "Hello! Welcome to our healthcare system.",
            'emotions': [
                (EMOTION_NEUTRAL, 0.5),  # Brief neutral start
                (EMOTION_HAPPY, 2.0),    # Happy greeting
                (EMOTION_NEUTRAL, 1.0)   # Return to neutral
            ],
            'integration_notes': [
                "Start neutral to establish baseline",
                "Trigger happy emotion as TTS says 'Hello!'",
                "Return to neutral after greeting completes"
            ]
        },
        {
            'text': "I notice you seem concerned. How can I help?",
            'emotions': [
                (EMOTION_CONCERNED, 1.5),  # Acknowledge concern
                (EMOTION_REQUEST, 2.0),    # Offer help
                (EMOTION_NEUTRAL, 0.5)     # Wait for response
            ],
            'integration_notes': [
                "Show empathy with concerned emotion",
                "Transition to attentive listening for 'How can I help?'",
                "Return to neutral while waiting for user response"
            ]
        },
        {
            'text': "This is important! Please pay attention to these instructions.",
            'emotions': [
                (EMOTION_URGENT, 1.0),     # Alert for "This is important!"
                (EMOTION_URGENT, 2.5),     # Maintain urgency during instructions
                (EMOTION_NEUTRAL, 1.0)     # Calm down after message
            ],
            'integration_notes': [
                "Immediately trigger urgent emotion for attention",
                "Maintain urgent state during critical information",
                "Gradually return to neutral after message delivery"
            ]
        }
    ]
    
    for i, scenario in enumerate(tts_scenarios, 1):
        print(f"\n--- TTS SCENARIO {i} ---")
        print(f"Speech Text: '{scenario['text']}'")
        print("Emotion Timeline:")
        total_time = 0
        for j, (emotion, duration) in enumerate(scenario['emotions']):
            print(f"  {total_time:.1f}s - {total_time + duration:.1f}s: {emotion.upper()}")
            print(f"    → {scenario['integration_notes'][j]}")
            total_time += duration
        print(f"Total Duration: {total_time:.1f}s")
        print()
        
        # Show the actual code pattern
        print("CODE PATTERN:")
        print("```python")
        print("# In your TTS integration:")
        for j, (emotion, duration) in enumerate(scenario['emotions']):
            if j == 0:
                print(f"emotion_manager.trigger_emotion('{emotion}')")
                print(f"# TTS starts playing...")
            else:
                print(f"# After {sum(d for _, d in scenario['emotions'][:j]):.1f}s:")
                print(f"emotion_manager.trigger_emotion('{emotion}')")
        print("```")
        print()


def demonstrate_advanced_patterns():
    """
    Demonstrate advanced emotion chaining patterns for complex interactions.
    
    These patterns show how to handle more sophisticated TTS scenarios
    that teams might encounter in real applications.
    """
    print("\n=== ADVANCED TEAM INTEGRATION PATTERNS ===")
    print("Complex scenarios for sophisticated TTS applications")
    print()
    
    advanced_patterns = [
        {
            'name': 'Error Recovery Pattern',
            'description': 'Handle TTS errors gracefully without breaking animation',
            'code': '''
# Error-safe TTS integration
try:
    emotion_manager.trigger_emotion('happy')
    tts_engine.speak("Hello!")
    # Wait for TTS completion...
    emotion_manager.trigger_emotion('neutral')
except TTSError:
    # Always return to neutral on error
    emotion_manager.trigger_emotion('neutral')
    # Animation continues smoothly even if TTS fails
'''
        },
        {
            'name': 'Interrupt Handling Pattern',
            'description': 'Handle user interruptions during TTS playback',
            'code': '''
# Handle user interruptions
def handle_user_interrupt():
    tts_engine.stop()  # Stop current speech
    emotion_manager.trigger_emotion('request')  # Show listening
    # Emotion system continues smoothly during interruption
'''
        },
        {
            'name': 'Emotion State Checking Pattern',
            'description': 'Check emotion state before triggering new emotions',
            'code': '''
# Check current state before changing
current_emotion = emotion_manager.get_current_emotion()
if current_emotion != 'urgent':
    emotion_manager.trigger_emotion('urgent')
    # Only change if not already in target state
'''
        }
    ]
    
    for pattern in advanced_patterns:
        print(f"PATTERN: {pattern['name']}")
        print(f"Purpose: {pattern['description']}")
        print("Implementation:")
        print(pattern['code'])
        print("-" * 50)


def main():
    """
    Main function demonstrating real-time emotion chaining.
    
    This example shows teams how to:
    1. Initialize emotion system for real-time use
    2. Chain emotions seamlessly during pygame rendering
    3. Coordinate emotions with TTS playback timing
    4. Maintain animation continuity throughout interactions
    5. Handle advanced scenarios like errors and interruptions
    """
    print("Real-time Emotion Chaining Demo")
    print("===============================")
    print()
    print("COMPREHENSIVE GUIDE for TTS Integration Teams")
    print("This demo shows how to chain emotions for TTS integration.")
    print()
    print("KEY CONCEPTS FOR TEAM INTEGRATION:")
    print("• Emotions update in real-time without breaking animation loop")
    print("• Seamless transitions between emotions during speech")
    print("• emotion_manager.update() called every frame for smooth chaining")
    print("• Perfect for coordinating with TTS playback timing")
    print("• Error-safe patterns that maintain animation continuity")
    print()
    
    # Show TTS integration patterns
    simulate_tts_integration()
    
    # Show advanced patterns
    demonstrate_advanced_patterns()
    
    print("\n" + "="*60)
    print("INTERACTIVE DEMONSTRATION")
    print("="*60)
    print("Now you'll see these patterns in action with live animations.")
    print("Watch how emotions transition smoothly during pygame rendering.")
    input("Press Enter to begin real-time demonstration...")
    
    # Run the interactive demo
    demo = EmotionChainDemo()
    demo.run_demo()


if __name__ == "__main__":
    main()