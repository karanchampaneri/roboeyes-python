#!/usr/bin/env python3
"""
RoboEyes Desktop - Basic Example

This example demonstrates the basic functionality of the RoboEyes desktop library.
It shows how to initialize the desktop version and run basic eye animations.

This is the desktop port of the original MicroPython test_basic.py example.
"""

import sys
import os

# Add the src directory to the path so we can import the desktop modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from roboeyes.desktop_roboeyes import DesktopRoboEyes, DEFAULT, TIRED, ANGRY, HAPPY, ON, OFF
from desktop.config import RoboEyesConfig
from desktop.timing import ticks_ms, ticks_diff
import time

def main():
    """Main function demonstrating basic RoboEyes functionality."""
    print("RoboEyes Desktop - Basic Example")
    print("Press Ctrl+C to exit")
    
    # Create configuration for the desktop version
    config = RoboEyesConfig(
        display_width=128,
        display_height=64,
        window_width=800,
        window_height=600,
        frame_rate=60,
        resizable=True,
        fullscreen=False
    )
    
    try:
        # Initialize RoboEyes desktop version
        robo = DesktopRoboEyes(config=config)
        
        # Define some automated eyes behaviour
        robo.set_auto_blinker(ON, 3, 2)  # Start auto blinker: active, interval, variation
        robo.set_idle_mode(ON, 2, 2)     # Start idle mode: active, interval, variation
        
        # Optional: Configure eye shapes (uncomment to customize)
        # robo.eyes_width(28, 28)    # left eye width, right eye width
        # robo.eyes_height(45, 45)   # left eye height, right eye height
        # robo.eyes_radius(8, 8)     # left eye radius, right eye radius
        # robo.eyes_spacing(10)      # space between eyes
        
        # Optional: Enable cyclops mode (uncomment to test)
        # robo.set_cyclops(True)
        
        print("Starting RoboEyes animation...")
        print("Use keyboard controls to interact with the eyes:")
        print("- Number keys 1-7: Change mood")
        print("- Arrow keys: Move eyes")
        print("- Space: Blink")
        print("- H: Show help")
        print("- ESC or close window: Exit")
        
        # Initial setup animation - give eyes time to open
        start_time = ticks_ms()
        while ticks_diff(ticks_ms(), start_time) < 1000:
            robo.handle_events()
            robo.update()
            if not robo.running:
                break
        
        # Optional: Demonstrate programmatic control (uncomment to test)
        # robo.close()  # Close eyes
        # time.sleep(1)
        # robo.open()   # Open eyes
        
        # Optional: Set mood and position (uncomment to test)
        # robo.mood = HAPPY
        # robo.position = DEFAULT
        # robo.curious = True
        
        # Optional: Set flickering (uncomment to test)
        # robo.horiz_flicker(True, 2)  # horizontal flicker: on/off, amplitude
        # robo.vert_flicker(True, 2)   # vertical flicker: on/off, amplitude
        
        # Optional: Play animations (uncomment to test)
        # robo.confuse()  # confused - eyes shaking left and right
        # robo.laugh()    # laughing - eyes shaking up and down
        # robo.wink(right=True)  # make the right eye wink
        
        # Main animation loop
        robo.run()
        
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())