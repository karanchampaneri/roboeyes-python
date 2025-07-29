#!/usr/bin/env python3
"""
Emotion Configuration System Demo

This example demonstrates how to use the emotion animation configuration system,
including loading configurations from JSON files, creating custom mappings,
and managing emotion-to-animation mappings.
"""

import json
import os
import sys
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from roboeyes.emotion_animation import (
    EmotionAnimationManager,
    AnimationConfig,
    load_emotion_mappings_from_json,
    save_emotion_mappings_to_json,
    create_default_config_file,
    find_config_file,
    get_default_emotion_mapping,
    VALID_EMOTIONS
)


class MockRoboEyes:
    """Mock RoboEyes class for demonstration purposes."""
    
    def __init__(self):
        self.mood = 0
        self.sequences = MockSequences()
        print("MockRoboEyes initialized")
    
    def set_mood(self, mood):
        self.mood = mood
        print(f"Mood set to: {mood}")


class MockSequences:
    """Mock sequences class for demonstration purposes."""
    
    def idle_gentle(self):
        print("Playing idle_gentle animation sequence")
    
    def gentle_joy(self):
        print("Playing gentle_joy animation sequence")
    
    def alert_focused(self):
        print("Playing alert_focused animation sequence")
    
    def empathetic_support(self):
        print("Playing empathetic_support animation sequence")
    
    def attentive_listening(self):
        print("Playing attentive_listening animation sequence")
    
    def custom_idle(self):
        print("Playing custom_idle animation sequence")
    
    def custom_joy(self):
        print("Playing custom_joy animation sequence")


def demo_basic_configuration():
    """Demonstrate basic configuration loading and usage."""
    print("\n" + "="*60)
    print("DEMO: Basic Configuration System")
    print("="*60)
    
    # Create a mock RoboEyes instance
    roboeyes = MockRoboEyes()
    
    # Initialize EmotionAnimationManager with default configuration
    print("\n1. Initializing EmotionAnimationManager with default configuration...")
    manager = EmotionAnimationManager(roboeyes)
    
    # Show available emotions
    print(f"\nAvailable emotions: {manager.get_available_emotions()}")
    
    # Trigger some emotions
    print("\n2. Triggering different emotions...")
    emotions_to_test = ["neutral", "happy", "urgent", "concerned", "request"]
    
    for emotion in emotions_to_test:
        print(f"\nTriggering emotion: {emotion}")
        success = manager.trigger_emotion(emotion)
        print(f"Success: {success}")
        
        # Show current emotion
        print(f"Current emotion: {manager.current_emotion}")
    
    # Test invalid emotion
    print(f"\n3. Testing invalid emotion...")
    success = manager.trigger_emotion("invalid_emotion")
    print(f"Triggered invalid emotion, success: {success}")
    print(f"Current emotion (should be fallback): {manager.current_emotion}")


def demo_json_configuration():
    """Demonstrate loading configuration from JSON files."""
    print("\n" + "="*60)
    print("DEMO: JSON Configuration Loading")
    print("="*60)
    
    # Create a custom configuration
    custom_config = {
        "emotion_mappings": {
            "neutral": {
                "sequence_name": "custom_idle",
                "mood": 0,
                "duration_ms": None,
                "transition_duration_ms": 800,
                "loop": True,
                "priority": 1
            },
            "happy": {
                "sequence_name": "custom_joy",
                "mood": 3,
                "duration_ms": 3000,
                "transition_duration_ms": 1200,
                "loop": False,
                "priority": 3
            },
            "urgent": {
                "sequence_name": "alert_focused",
                "mood": 0,
                "duration_ms": None,
                "transition_duration_ms": 400,
                "loop": True,
                "priority": 5
            },
            "concerned": {
                "sequence_name": "empathetic_support",
                "mood": 0,
                "duration_ms": 4000,
                "transition_duration_ms": 1000,
                "loop": False,
                "priority": 4
            },
            "request": {
                "sequence_name": "attentive_listening",
                "mood": 0,
                "duration_ms": 2500,
                "transition_duration_ms": 600,
                "loop": False,
                "priority": 3
            }
        },
        "default_emotion": "neutral",
        "metadata": {
            "version": "1.0",
            "description": "Custom emotion configuration for demo"
        }
    }
    
    # Save custom configuration to a temporary file
    temp_config_path = "temp_emotion_config.json"
    print(f"\n1. Creating custom configuration file: {temp_config_path}")
    
    with open(temp_config_path, 'w') as f:
        json.dump(custom_config, f, indent=2)
    
    print("Custom configuration created with the following mappings:")
    for emotion, config in custom_config["emotion_mappings"].items():
        print(f"  {emotion}: {config['sequence_name']} (transition: {config['transition_duration_ms']}ms)")
    
    # Load configuration from file
    print(f"\n2. Loading configuration from JSON file...")
    try:
        roboeyes = MockRoboEyes()
        manager = EmotionAnimationManager(roboeyes, config_file_path=temp_config_path)
        
        print("Configuration loaded successfully!")
        
        # Test the custom configuration
        print(f"\n3. Testing custom configuration...")
        
        # Show the custom neutral configuration
        neutral_config = manager.get_emotion_config("neutral")
        print(f"Neutral emotion config:")
        print(f"  Sequence: {neutral_config.sequence_name}")
        print(f"  Transition duration: {neutral_config.transition_duration_ms}ms")
        
        # Trigger emotions with custom configuration
        print(f"\n4. Triggering emotions with custom configuration...")
        for emotion in ["neutral", "happy"]:
            print(f"\nTriggering {emotion}...")
            manager.trigger_emotion(emotion)
        
    except Exception as e:
        print(f"Error loading configuration: {e}")
    
    finally:
        # Clean up temporary file
        if os.path.exists(temp_config_path):
            os.remove(temp_config_path)
            print(f"\nCleaned up temporary file: {temp_config_path}")


def demo_configuration_management():
    """Demonstrate configuration management features."""
    print("\n" + "="*60)
    print("DEMO: Configuration Management")
    print("="*60)
    
    roboeyes = MockRoboEyes()
    manager = EmotionAnimationManager(roboeyes)
    
    # Show current mappings
    print("\n1. Current emotion mappings:")
    mappings = manager.get_emotion_mappings()
    for emotion, config in mappings.items():
        print(f"  {emotion}: {config.sequence_name} (priority: {config.priority})")
    
    # Create a custom animation config
    print(f"\n2. Creating custom animation configuration...")
    custom_config = AnimationConfig(
        sequence_name="custom_celebration",
        mood=3,
        duration_ms=2000,
        transition_duration_ms=500,
        loop=False,
        priority=4
    )
    
    # Register the custom mapping (this would fail since 'celebration' is not a valid emotion)
    # Instead, let's update an existing emotion
    print(f"\n3. Updating existing emotion configuration...")
    success = manager.update_emotion_config("happy", custom_config)
    print(f"Update success: {success}")
    
    if success:
        # Show the updated configuration
        updated_config = manager.get_emotion_config("happy")
        print(f"Updated happy emotion config:")
        print(f"  Sequence: {updated_config.sequence_name}")
        print(f"  Duration: {updated_config.duration_ms}ms")
        print(f"  Priority: {updated_config.priority}")
    
    # Save the updated configuration
    print(f"\n4. Saving updated configuration...")
    temp_save_path = "updated_emotion_config.json"
    success = manager.save_emotion_mappings(temp_save_path)
    print(f"Save success: {success}")
    
    if success and os.path.exists(temp_save_path):
        print(f"Configuration saved to: {temp_save_path}")
        
        # Show a snippet of the saved file
        with open(temp_save_path, 'r') as f:
            saved_data = json.load(f)
        
        print("Saved configuration snippet (happy emotion):")
        if "emotion_mappings" in saved_data:
            happy_config = saved_data["emotion_mappings"]["happy"]
        else:
            happy_config = saved_data["happy"]
        
        print(json.dumps(happy_config, indent=2))
        
        # Clean up
        os.remove(temp_save_path)
        print(f"Cleaned up: {temp_save_path}")


def demo_config_file_discovery():
    """Demonstrate automatic configuration file discovery."""
    print("\n" + "="*60)
    print("DEMO: Configuration File Discovery")
    print("="*60)
    
    # Check if there's an existing config file
    print("\n1. Searching for existing configuration files...")
    found_config = find_config_file()
    
    if found_config:
        print(f"Found configuration file: {found_config}")
        
        # Try to load it
        try:
            roboeyes = MockRoboEyes()
            manager = EmotionAnimationManager(roboeyes)  # Should auto-discover the config
            print("Successfully initialized with discovered configuration")
            
            # Show some details
            available_emotions = manager.get_available_emotions()
            print(f"Available emotions: {available_emotions}")
            
        except Exception as e:
            print(f"Error loading discovered configuration: {e}")
    else:
        print("No configuration file found in common locations")
        print("Searched locations:")
        print("  - Current directory")
        print("  - ~/.roboeyes/")
        print("  - ../config/")
    
    # Demonstrate creating a default config file
    print(f"\n2. Creating default configuration file...")
    default_config_path = "demo_default_config.json"
    
    try:
        create_default_config_file(default_config_path)
        print(f"Created default configuration: {default_config_path}")
        
        # Show the structure
        with open(default_config_path, 'r') as f:
            config_data = json.load(f)
        
        print("Configuration structure:")
        for key in config_data.keys():
            if key == "emotion_mappings":
                print(f"  {key}: {len(config_data[key])} emotions")
            else:
                print(f"  {key}: {type(config_data[key]).__name__}")
        
    except Exception as e:
        print(f"Error creating default configuration: {e}")
    
    finally:
        # Clean up
        if os.path.exists(default_config_path):
            os.remove(default_config_path)
            print(f"Cleaned up: {default_config_path}")


def main():
    """Run all configuration system demos."""
    print("Emotion Animation Configuration System Demo")
    print("=" * 80)
    
    try:
        # Run all demos
        demo_basic_configuration()
        demo_json_configuration()
        demo_configuration_management()
        demo_config_file_discovery()
        
        print("\n" + "="*80)
        print("All demos completed successfully!")
        print("="*80)
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()