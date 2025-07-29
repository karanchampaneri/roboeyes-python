#!/usr/bin/env python3
"""
Configuration Hot-Reloading Demo

This example demonstrates the configuration management and hot-reloading
functionality implemented in Task 8. It shows how to:

1. Load emotion mappings from a configuration file
2. Start automatic file watching for configuration changes
3. Dynamically update individual emotion mappings
4. Monitor configuration reload events through logging

Run this script and then modify the config/emotion_config.json file
to see the hot-reloading in action.
"""

import os
import sys
import json
import time
import logging
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from roboeyes.emotion_animation import (
    EmotionAnimationManager, AnimationConfig,
    EMOTION_HAPPY, EMOTION_NEUTRAL, EMOTION_URGENT, EMOTION_CONCERNED, EMOTION_REQUEST
)
from roboeyes.desktop_roboeyes import DesktopRoboEyes
from desktop.config import RoboEyesConfig


def setup_logging():
    """Set up logging to see configuration reload events."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Enable debug logging for emotion animation module
    emotion_logger = logging.getLogger('roboeyes.emotion_animation')
    emotion_logger.setLevel(logging.INFO)


def config_reload_callback(config_file_path):
    """Callback function called when configuration is reloaded."""
    print(f"\n🔄 Configuration reloaded from: {config_file_path}")
    print("   The system has automatically updated with new emotion mappings!")


def demonstrate_hot_reloading():
    """Demonstrate the hot-reloading functionality."""
    print("=" * 70)
    print("Configuration Hot-Reloading Demo")
    print("=" * 70)
    
    # Set up logging
    setup_logging()
    
    # Initialize RoboEyes with configuration
    config = RoboEyesConfig()
    roboeyes = DesktopRoboEyes(config)
    
    print("✓ RoboEyes initialized")
    
    # Get the emotion manager (should be automatically created)
    emotion_manager = roboeyes.emotion_manager
    
    if not emotion_manager:
        print("✗ Emotion manager not found. Please ensure Task 4 integration is complete.")
        return
    
    print("✓ Emotion animation manager found")
    
    # Display current configuration info
    config_info = emotion_manager.get_configuration_info()
    print(f"\nCurrent Configuration:")
    print(f"  📁 Config file: {config_info['config_file_path']}")
    print(f"  🎭 Emotions available: {len(config_info['available_emotions'])}")
    print(f"  🔧 Available emotions: {', '.join(config_info['available_emotions'])}")
    print(f"  🏠 Fallback emotion: {config_info['fallback_emotion']}")
    
    # Start configuration file watcher
    print(f"\n🔍 Starting configuration file watcher...")
    watcher_started = emotion_manager.start_config_file_watcher(callback=config_reload_callback)
    
    if watcher_started:
        print("✓ Configuration file watcher started successfully!")
        print(f"   Watching: {config_info['config_file_path']}")
    else:
        print("✗ Failed to start configuration file watcher")
        return
    
    # Test current emotion triggering
    print(f"\n🎭 Testing current emotion mappings...")
    for emotion in [EMOTION_NEUTRAL, EMOTION_HAPPY, EMOTION_URGENT]:
        result = emotion_manager.trigger_emotion(emotion)
        print(f"   {emotion}: {'✓' if result else '✗'}")
        time.sleep(0.5)
    
    # Demonstrate dynamic emotion mapping updates
    print(f"\n🔧 Demonstrating dynamic emotion mapping updates...")
    
    # Add a custom emotion mapping
    custom_config = AnimationConfig(
        sequence_name="custom_demo_sequence",
        mood=0,
        duration_ms=2000,
        transition_duration_ms=1000,
        loop=True,
        priority=2
    )
    
    result = emotion_manager.update_emotion_mapping("demo_emotion", custom_config)
    if result:
        print("✓ Added custom 'demo_emotion' mapping")
        
        # Test the new emotion
        result = emotion_manager.trigger_emotion("demo_emotion")
        print(f"   Testing demo_emotion: {'✓' if result else '✗'}")
    else:
        print("✗ Failed to add custom emotion mapping")
    
    # Show updated configuration
    updated_info = emotion_manager.get_configuration_info()
    print(f"\nUpdated Configuration:")
    print(f"  🎭 Emotions available: {len(updated_info['available_emotions'])}")
    print(f"  🔧 Available emotions: {', '.join(updated_info['available_emotions'])}")
    
    # Interactive demonstration
    print(f"\n" + "=" * 70)
    print("INTERACTIVE HOT-RELOADING DEMONSTRATION")
    print("=" * 70)
    print(f"The configuration file watcher is now active!")
    print(f"Config file: {config_info['config_file_path']}")
    print(f"")
    print(f"To see hot-reloading in action:")
    print(f"1. Open the config file in another editor")
    print(f"2. Modify any emotion mapping (e.g., change duration_ms values)")
    print(f"3. Save the file")
    print(f"4. Watch this console for automatic reload messages!")
    print(f"")
    print(f"You can also test individual emotion updates by typing commands:")
    print(f"  'test <emotion>' - Test triggering an emotion")
    print(f"  'info' - Show current configuration info")
    print(f"  'reload' - Manually reload configuration")
    print(f"  'quit' - Exit the demo")
    print(f"")
    
    # Interactive loop
    try:
        while True:
            try:
                command = input("Enter command (or 'quit' to exit): ").strip().lower()
                
                if command == 'quit':
                    break
                elif command == 'info':
                    info = emotion_manager.get_configuration_info()
                    print(f"📊 Configuration Info:")
                    print(f"   Emotions: {len(info['available_emotions'])}")
                    print(f"   Available: {', '.join(info['available_emotions'])}")
                    print(f"   Current: {info['current_emotion'] or 'None'}")
                    print(f"   Watcher running: {info['config_watcher_running']}")
                elif command == 'reload':
                    result = emotion_manager.reload_configuration()
                    print(f"🔄 Manual reload: {'✓ Success' if result else '✗ Failed'}")
                elif command.startswith('test '):
                    emotion = command[5:].strip()
                    if emotion:
                        result = emotion_manager.trigger_emotion(emotion)
                        print(f"🎭 Testing '{emotion}': {'✓ Success' if result else '✗ Failed'}")
                    else:
                        print("❌ Please specify an emotion to test")
                elif command:
                    print(f"❓ Unknown command: {command}")
                    
            except KeyboardInterrupt:
                print(f"\n👋 Interrupted by user")
                break
            except EOFError:
                print(f"\n👋 End of input")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    finally:
        # Clean up
        print(f"\n🧹 Cleaning up...")
        
        # Remove custom emotion mapping
        if "demo_emotion" in emotion_manager._emotion_mappings:
            emotion_manager.remove_emotion_mapping("demo_emotion")
            print("✓ Removed custom demo emotion mapping")
        
        # Stop file watcher
        emotion_manager.stop_config_file_watcher()
        print("✓ Stopped configuration file watcher")
        
        print(f"\n" + "=" * 70)
        print("Hot-Reloading Demo Complete!")
        print("=" * 70)
        print(f"Key features demonstrated:")
        print(f"✓ Automatic configuration file watching")
        print(f"✓ Dynamic emotion mapping updates")
        print(f"✓ Configuration validation and error handling")
        print(f"✓ Logging of configuration reload events")
        print(f"✓ Individual emotion mapping management")


def main():
    """Main function to run the hot-reloading demo."""
    try:
        demonstrate_hot_reloading()
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)