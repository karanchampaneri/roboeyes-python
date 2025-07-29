#!/usr/bin/env python3
"""
Emotion Animation System Usage Demonstration

This example script demonstrates how to use the RoboEyes emotion animation system
in various scenarios. It shows basic usage, advanced configuration, integration
with AI emotion detection, and best practices for healthcare applications.

This script serves as both documentation and a practical example for developers
integrating the emotion system into their applications.
"""

import sys
import os
import time
import json
import pygame
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from roboeyes.desktop_roboeyes import DesktopRoboEyes
from roboeyes.emotion_animation import (
    EmotionAnimationManager, AnimationConfig,
    EMOTION_HAPPY, EMOTION_NEUTRAL, EMOTION_URGENT, EMOTION_CONCERNED, EMOTION_REQUEST,
    get_default_emotion_mapping, create_default_config_file
)
from desktop.config import RoboEyesConfig


class EmotionSystemDemo:
    """Comprehensive demonstration of the emotion animation system."""
    
    def __init__(self):
        """Initialize the demo with RoboEyes and emotion system."""
        print("Initializing Emotion Animation System Demo...")
        
        # Create configuration for the demo
        self.config = RoboEyesConfig(
            display_width=128,
            display_height=64,
            window_width=1000,
            window_height=700,
            frame_rate=30,
            auto_blinker=True,
            blink_interval=4,
            blink_variation=2
        )
        
        # Initialize RoboEyes (this will also initialize the emotion system)
        try:
            self.roboeyes = DesktopRoboEyes(self.config)
            print("✓ RoboEyes initialized successfully")
            
            # Access the emotion manager
            self.emotion_manager = self.roboeyes.emotion_manager
            if self.emotion_manager:
                print("✓ Emotion animation system ready")
                print(f"  Available emotions: {self.emotion_manager.get_available_emotions()}")
            else:
                print("⚠ Emotion system not available")
                
        except Exception as e:
            print(f"✗ Initialization failed: {e}")
            raise
    
    def basic_usage_demo(self):
        """Demonstrate basic emotion triggering."""
        print("\n" + "="*50)
        print("BASIC USAGE DEMONSTRATION")
        print("="*50)
        
        print("\n1. Basic Emotion Triggering")
        print("-" * 30)
        
        # Simple emotion triggering
        emotions_to_demo = [
            (EMOTION_NEUTRAL, "Patient is calm and comfortable"),
            (EMOTION_HAPPY, "Patient expressing satisfaction"),
            (EMOTION_CONCERNED, "Patient showing worry"),
            (EMOTION_URGENT, "Patient needs immediate attention"),
            (EMOTION_REQUEST, "Patient making a request")
        ]
        
        for emotion, description in emotions_to_demo:
            print(f"\nTriggering: {emotion}")
            print(f"Context: {description}")
            
            # Method 1: Using the emotion manager directly
            result = self.emotion_manager.trigger_emotion(emotion)
            print(f"Result: {result}")
            
            # Method 2: Using the convenience method on RoboEyes
            # result = self.roboeyes.trigger_emotion(emotion)
            
            # Show current state
            print(f"Current emotion: {self.emotion_manager.current_emotion}")
            print(f"Is transitioning: {self.emotion_manager.is_transitioning}")
            
            # Wait for transition to complete
            self.wait_for_transition()
            
            # Pause between demonstrations
            time.sleep(1.5)
    
    def advanced_configuration_demo(self):
        """Demonstrate advanced configuration options."""
        print("\n" + "="*50)
        print("ADVANCED CONFIGURATION DEMONSTRATION")
        print("="*50)
        
        print("\n1. Custom Emotion Mappings")
        print("-" * 30)
        
        # Create custom animation configurations
        custom_configs = {
            "excited": AnimationConfig(
                sequence_name="gentle_joy",
                mood=3,  # HAPPY mood
                duration_ms=2000,
                transition_duration_ms=800,
                loop=False,
                priority=4
            ),
            "focused": AnimationConfig(
                sequence_name="alert_focused",
                mood=0,  # DEFAULT mood
                duration_ms=None,  # Indefinite
                transition_duration_ms=300,
                loop=True,
                priority=3
            )
        }
        
        # Register custom emotions
        for emotion_name, config in custom_configs.items():
            self.emotion_manager.register_emotion_mapping(emotion_name, config)
            print(f"✓ Registered custom emotion: {emotion_name}")
        
        # Test custom emotions
        print(f"\nAvailable emotions now: {self.emotion_manager.get_available_emotions()}")
        
        print("\nTesting custom emotions...")
        self.emotion_manager.trigger_emotion("excited")
        print("Triggered 'excited' emotion")
        self.wait_for_transition()
        
        self.emotion_manager.trigger_emotion("focused")
        print("Triggered 'focused' emotion")
        self.wait_for_transition()
        
        print("\n2. Configuration File Management")
        print("-" * 30)
        
        # Create a custom configuration file
        config_path = Path("temp_emotion_config.json")
        try:
            create_default_config_file(str(config_path))
            print(f"✓ Created configuration file: {config_path}")
            
            # Load configuration from file
            new_emotion_manager = EmotionAnimationManager(
                self.roboeyes, 
                config_file_path=str(config_path)
            )
            print("✓ Loaded emotion manager from configuration file")
            
        finally:
            # Clean up
            if config_path.exists():
                config_path.unlink()
                print("✓ Cleaned up temporary configuration file")
    
    def ai_integration_simulation(self):
        """Simulate integration with AI emotion detection."""
        print("\n" + "="*50)
        print("AI EMOTION DETECTION INTEGRATION SIMULATION")
        print("="*50)
        
        # Simulate AI emotion detection results
        ai_detections = [
            {"emotion": EMOTION_HAPPY, "confidence": 0.85, "context": "Patient smiled during conversation"},
            {"emotion": EMOTION_CONCERNED, "confidence": 0.72, "context": "Patient asked about test results"},
            {"emotion": EMOTION_URGENT, "confidence": 0.91, "context": "Patient reported pain level 8/10"},
            {"emotion": EMOTION_REQUEST, "confidence": 0.68, "context": "Patient asked for water"},
            {"emotion": EMOTION_NEUTRAL, "confidence": 0.55, "context": "Patient listening quietly"}
        ]
        
        print("Simulating AI emotion detection workflow...")
        
        for i, detection in enumerate(ai_detections, 1):
            print(f"\n--- AI Detection {i} ---")
            print(f"Detected emotion: {detection['emotion']}")
            print(f"Confidence: {detection['confidence']:.2f}")
            print(f"Context: {detection['context']}")
            
            # This is how you would integrate with real AI emotion detection
            if detection['confidence'] > 0.6:  # Confidence threshold
                result = self.emotion_manager.trigger_emotion(
                    detection['emotion'], 
                    confidence=detection['confidence']
                )
                print(f"Animation triggered: {result}")
                print(f"Current emotion: {self.emotion_manager.current_emotion}")
            else:
                print("Confidence too low, maintaining current emotion")
            
            # Wait for animation to settle
            self.wait_for_transition()
            time.sleep(1)
    
    def error_handling_demo(self):
        """Demonstrate error handling and recovery."""
        print("\n" + "="*50)
        print("ERROR HANDLING AND RECOVERY DEMONSTRATION")
        print("="*50)
        
        print("\n1. Invalid Emotion Handling")
        print("-" * 30)
        
        # Test invalid emotion names
        invalid_emotions = ["invalid_emotion", "", None, 123, "HAPPY"]  # Note: case sensitive
        
        for invalid_emotion in invalid_emotions:
            print(f"\nTesting invalid emotion: {repr(invalid_emotion)}")
            result = self.emotion_manager.trigger_emotion(invalid_emotion)
            print(f"Result: {result}")
            print(f"Current emotion (should be fallback): {self.emotion_manager.current_emotion}")
        
        print("\n2. System Health and Recovery")
        print("-" * 30)
        
        # Check system health
        health = self.emotion_manager.is_animation_system_healthy()
        print(f"System health: {health}")
        
        # Test recovery mechanism
        recovery_result = self.emotion_manager.recover_from_error()
        print(f"Recovery result: {recovery_result}")
        print(f"Post-recovery emotion: {self.emotion_manager.current_emotion}")
    
    def healthcare_workflow_demo(self):
        """Demonstrate a realistic healthcare workflow with visual feedback."""
        print("\n" + "="*50)
        print("HEALTHCARE WORKFLOW DEMONSTRATION")
        print("="*50)
        
        # Simulate a patient interaction workflow
        workflow_steps = [
            {
                "step": "Patient enters room",
                "emotion": EMOTION_NEUTRAL,
                "duration": 3,
                "description": "Calm, welcoming presence"
            },
            {
                "step": "Patient expresses concern about symptoms",
                "emotion": EMOTION_CONCERNED,
                "duration": 4,
                "description": "Empathetic, understanding response"
            },
            {
                "step": "Patient reports severe pain",
                "emotion": EMOTION_URGENT,
                "duration": 2,
                "description": "Alert, focused attention"
            },
            {
                "step": "Patient asks for pain medication",
                "emotion": EMOTION_REQUEST,
                "duration": 3,
                "description": "Attentive listening"
            },
            {
                "step": "Patient feels better after treatment",
                "emotion": EMOTION_HAPPY,
                "duration": 4,
                "description": "Gentle joy, supportive"
            },
            {
                "step": "Patient ready to rest",
                "emotion": EMOTION_NEUTRAL,
                "duration": 3,
                "description": "Calm, peaceful presence"
            }
        ]
        
        print("Simulating patient care workflow with visual animations...")
        print("Watch the eye animations change to match each healthcare scenario!")
        
        for i, step in enumerate(workflow_steps, 1):
            print(f"\n--- Step {i}: {step['step']} ---")
            print(f"Appropriate emotion: {step['emotion']}")
            print(f"Description: {step['description']}")
            
            # Trigger the appropriate emotion
            result = self.emotion_manager.trigger_emotion(step['emotion'])
            print(f"Animation result: {result}")
            
            # Show transition progress with visual updates
            if self.emotion_manager.is_transitioning:
                print("Transitioning", end="")
                transition_start = time.time()
                while self.emotion_manager.is_transitioning and (time.time() - transition_start) < 3.0:
                    print(".", end="", flush=True)
                    self.emotion_manager.update()
                    self.roboeyes.update()  # Update visual display
                    self.roboeyes.clock.tick(30)  # Maintain frame rate
                    time.sleep(0.1)
                print(" Complete!")
            
            print(f"Current emotion: {self.emotion_manager.current_emotion}")
            
            # Maintain emotion for specified duration with visual updates
            print(f"Maintaining emotion for {step['duration']} seconds...")
            maintain_start = time.time()
            while (time.time() - maintain_start) < step['duration']:
                self.emotion_manager.update()
                self.roboeyes.update()  # Keep visual display active
                self.roboeyes.clock.tick(30)
                
                # Handle window events to prevent freezing
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        print("\nDemo interrupted by window close")
                        return
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            print("\nDemo interrupted by ESC key")
                            return
                        elif event.key == pygame.K_SPACE:
                            print(f"\n  [Status: {self.emotion_manager.current_emotion}, "
                                  f"Transitioning: {self.emotion_manager.is_transitioning}]")
        
        print("\n✓ Healthcare workflow demonstration complete!")
        print("The eye animations showed appropriate responses for each patient scenario.")
    
    def interactive_demo(self):
        """Run an interactive visual demonstration with live eye animations."""
        print("\n" + "="*50)
        print("INTERACTIVE VISUAL DEMONSTRATION")
        print("="*50)
        
        print("\nInteractive Controls:")
        print("  1 - Neutral emotion (calm, reassuring)")
        print("  2 - Happy emotion (gentle joy)")
        print("  3 - Urgent emotion (alert, focused)")
        print("  4 - Concerned emotion (empathetic support)")
        print("  5 - Request emotion (attentive listening)")
        print("  A - Auto-cycle through emotions")
        print("  H - Show help")
        print("  Q - Quit interactive mode")
        print("  SPACE - Show current status")
        print("  ESC - Exit application")
        
        emotion_map = {
            pygame.K_1: (EMOTION_NEUTRAL, "Neutral (calm, reassuring)"),
            pygame.K_2: (EMOTION_HAPPY, "Happy (gentle joy)"),
            pygame.K_3: (EMOTION_URGENT, "Urgent (alert, focused)"),
            pygame.K_4: (EMOTION_CONCERNED, "Concerned (empathetic support)"),
            pygame.K_5: (EMOTION_REQUEST, "Request (attentive listening)")
        }
        
        # Auto-cycle setup
        auto_cycle = False
        auto_cycle_emotions = [
            (EMOTION_NEUTRAL, "Neutral", 4),
            (EMOTION_HAPPY, "Happy", 3),
            (EMOTION_CONCERNED, "Concerned", 4),
            (EMOTION_URGENT, "Urgent", 3),
            (EMOTION_REQUEST, "Request", 3)
        ]
        current_auto_emotion = 0
        last_auto_time = time.time()
        
        print("\nPress keys to trigger emotions (window must have focus)...")
        print("Watch the eye animations change based on the emotions!")
        
        # Start with neutral emotion
        self.emotion_manager.trigger_emotion(EMOTION_NEUTRAL)
        print(f"\nStarting with: Neutral emotion")
        
        while self.roboeyes.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.roboeyes.running = False
                    
                elif event.type == pygame.KEYDOWN:
                    if event.key in emotion_map:
                        emotion, description = emotion_map[event.key]
                        print(f"\nTriggering: {description}")
                        result = self.emotion_manager.trigger_emotion(emotion)
                        print(f"Result: {result}")
                        current = self.emotion_manager.current_emotion
                        transitioning = self.emotion_manager.is_transitioning
                        print(f"Current: {current}, Transitioning: {transitioning}")
                        
                        # Disable auto-cycle when manual input is used
                        if auto_cycle:
                            auto_cycle = False
                            print("Auto-cycle disabled (manual input detected)")
                        
                    elif event.key == pygame.K_SPACE:
                        print(f"\n--- Current Status ---")
                        print(f"  Emotion: {self.emotion_manager.current_emotion}")
                        print(f"  Transitioning: {self.emotion_manager.is_transitioning}")
                        print(f"  Available emotions: {self.emotion_manager.get_available_emotions()}")
                        print(f"  Auto-cycle: {'ON' if auto_cycle else 'OFF'}")
                        
                    elif event.key == pygame.K_a:
                        auto_cycle = not auto_cycle
                        print(f"\nAuto-cycle mode: {'ON' if auto_cycle else 'OFF'}")
                        if auto_cycle:
                            last_auto_time = time.time()
                            print("Watch as emotions automatically cycle through healthcare scenarios...")
                        
                    elif event.key == pygame.K_h:
                        print("\n--- Help - Available Commands ---")
                        print("  1: Neutral - Calm, reassuring presence")
                        print("  2: Happy - Gentle joy for positive moments")
                        print("  3: Urgent - Alert, focused attention")
                        print("  4: Concerned - Empathetic support")
                        print("  5: Request - Attentive listening")
                        print("  A: Toggle auto-cycle mode")
                        print("  SPACE: Show current status")
                        print("  Q: Quit interactive mode")
                        print("  ESC: Exit application")
                        
                    elif event.key == pygame.K_q:
                        print("\nExiting interactive mode...")
                        return
                        
                    elif event.key == pygame.K_ESCAPE:
                        print("\nExiting application...")
                        self.roboeyes.running = False
            
            # Auto-cycle through emotions
            if auto_cycle:
                current_time = time.time()
                emotion_data = auto_cycle_emotions[current_auto_emotion]
                emotion, name, duration = emotion_data
                
                if current_time - last_auto_time >= duration:
                    current_auto_emotion = (current_auto_emotion + 1) % len(auto_cycle_emotions)
                    next_emotion_data = auto_cycle_emotions[current_auto_emotion]
                    next_emotion, next_name, next_duration = next_emotion_data
                    
                    print(f"\nAuto-cycle: {next_name} emotion")
                    self.emotion_manager.trigger_emotion(next_emotion)
                    last_auto_time = current_time
            
            # Update and render animations
            self.roboeyes.update()
            self.roboeyes.clock.tick(self.config.frame_rate)
    
    def wait_for_transition(self, timeout=3.0):
        """Wait for current transition to complete."""
        start_time = time.time()
        while self.emotion_manager.is_transitioning and (time.time() - start_time) < timeout:
            self.emotion_manager.update()
            time.sleep(0.01)  # 10ms updates
    
    def run_all_demos(self):
        """Run all demonstration modes."""
        try:
            print("Choose demo mode:")
            print("1. Run all demos sequentially (non-visual)")
            print("2. Interactive visual demo (recommended)")
            print("3. Healthcare workflow demo")
            
            choice = input("\nEnter choice (1-3, or press Enter for interactive): ").strip()
            
            if choice == "1":
                print("\nRunning all demos sequentially...")
                self.basic_usage_demo()
                self.advanced_configuration_demo()
                self.ai_integration_simulation()
                self.error_handling_demo()
                self.healthcare_workflow_demo()
                
                print("\n" + "="*50)
                print("ALL DEMONSTRATIONS COMPLETE")
                print("="*50)
                print("\nStarting interactive visual mode...")
                
            elif choice == "3":
                print("\nRunning healthcare workflow demo...")
                self.healthcare_workflow_demo()
                print("\nStarting interactive visual mode...")
                
            else:  # Default to interactive mode
                print("\nStarting interactive visual demo...")
            
            print("Close the window or press ESC to exit.")
            print("Press H for help once the window opens.")
            
            self.interactive_demo()
            
        except KeyboardInterrupt:
            print("\nDemo interrupted by user")
        except Exception as e:
            print(f"\nDemo error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print("\nEmotion System Demo Complete")


def main():
    """Main entry point for the demonstration."""
    print("RoboEyes Emotion Animation System - Usage Demonstration")
    print("=" * 60)
    print()
    print("This demo shows how to integrate and use the emotion animation system")
    print("in various scenarios including AI emotion detection integration.")
    print()
    
    try:
        demo = EmotionSystemDemo()
        demo.run_all_demos()
        
    except Exception as e:
        print(f"Failed to start demo: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())