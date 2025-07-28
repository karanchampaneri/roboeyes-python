#!/usr/bin/env python3
"""
RoboEyes Desktop - Interactive Demo

This example demonstrates interactive control of RoboEyes using keyboard and mouse input.
It provides a comprehensive demonstration of all available features and controls.

This is the desktop port of the original MicroPython test_interactive.py example,
adapted for desktop use with keyboard and mouse controls.
"""

import sys
import os

# Add the src directory to the path so we can import the desktop modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from roboeyes.desktop_roboeyes import (
    DesktopRoboEyes, DEFAULT, TIRED, ANGRY, HAPPY, FROZEN, SCARY, CURIOUS,
    ON, OFF, N, NE, E, SE, S, SW, W, NW
)
from desktop.config import RoboEyesConfig
from desktop.timing import ticks_ms, ticks_diff
import pygame

class InteractiveDemo:
    """Interactive demonstration of RoboEyes features."""
    
    def __init__(self):
        """Initialize the interactive demo."""
        self.mood_names = ["DEFAULT", "TIRED", "ANGRY", "HAPPY", "FROZEN", "SCARY", "CURIOUS"]
        self.position_names = ["DEFAULT", "N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        
        # Create configuration for the demo
        self.config = RoboEyesConfig(
            display_width=128,
            display_height=64,
            window_width=1000,
            window_height=700,
            frame_rate=60,
            resizable=True,
            fullscreen=False
        )
        
        # Initialize RoboEyes
        self.robo = DesktopRoboEyes(config=self.config)
        
        # Demo state
        self.demo_mode = False
        self.demo_step = 0
        self.demo_timer = 0
        self.demo_interval = 2000  # 2 seconds per step
        
        # Status display
        self.show_status = True
        self.status_timer = 0
        self.status_duration = 3000  # Show status for 3 seconds
        self.current_status = ""
    
    def show_welcome_message(self):
        """Display welcome message and instructions."""
        print("=" * 60)
        print("RoboEyes Desktop - Interactive Demo")
        print("=" * 60)
        print()
        print("KEYBOARD CONTROLS:")
        print("  Moods: 1=Default, 2=Tired, 3=Angry, 4=Happy, 5=Frozen, 6=Scary, 7=Curious")
        print("  Movement: Arrow keys or WASD")
        print("  Animations: Space=Blink, Q=Wink Left, E=Wink Right, C=Confuse, L=Laugh")
        print("  Eye State: O=Open, X=Close")
        print("  Modes: B=Auto-blink, I=Idle mode, Y=Cyclops, R=Curious")
        print("  Demo: D=Start/Stop auto demo")
        print("  Help: H or F1=Toggle help overlay")
        print("  Window: F11=Fullscreen, ESC=Exit fullscreen")
        print()
        print("MOUSE CONTROLS:")
        print("  Left Click: Make eyes look at cursor position")
        print("  Right Click: Trigger blink animation")
        print()
        print("Press H or F1 to show/hide the help overlay")
        print("Press D to start the automatic demonstration")
        print("Press ESC or close the window to exit")
        print("=" * 60)
    
    def update_status(self, message):
        """Update the status message."""
        self.current_status = message
        self.status_timer = ticks_ms()
        print(f"Status: {message}")
    
    def run_demo_sequence(self):
        """Run the automatic demonstration sequence."""
        if not self.demo_mode:
            return
        
        current_time = ticks_ms()
        if ticks_diff(current_time, self.demo_timer) < self.demo_interval:
            return
        
        # Move to next demo step
        self.demo_timer = current_time
        self.demo_step += 1
        
        # Demo sequence
        if self.demo_step == 1:
            self.update_status("Demo: Opening eyes")
            self.robo.open()
        elif self.demo_step == 2:
            self.update_status("Demo: Happy mood")
            self.robo.mood = HAPPY
        elif self.demo_step == 3:
            self.update_status("Demo: Laugh animation")
            self.robo.laugh()
        elif self.demo_step == 4:
            self.update_status("Demo: Tired mood")
            self.robo.mood = TIRED
        elif self.demo_step == 5:
            self.update_status("Demo: Moving eyes around")
            self.robo.position = NE
        elif self.demo_step == 6:
            self.robo.position = SE
        elif self.demo_step == 7:
            self.robo.position = SW
        elif self.demo_step == 8:
            self.robo.position = NW
        elif self.demo_step == 9:
            self.robo.position = DEFAULT
        elif self.demo_step == 10:
            self.update_status("Demo: Angry mood")
            self.robo.mood = ANGRY
        elif self.demo_step == 11:
            self.update_status("Demo: Confuse animation")
            self.robo.confuse()
        elif self.demo_step == 12:
            self.update_status("Demo: Frozen mood (with flicker)")
            self.robo.mood = FROZEN
        elif self.demo_step == 13:
            self.update_status("Demo: Scary mood (with vertical flicker)")
            self.robo.mood = SCARY
        elif self.demo_step == 14:
            self.update_status("Demo: Curious mode")
            self.robo.mood = CURIOUS
            self.robo.curious = True
        elif self.demo_step == 15:
            self.update_status("Demo: Winking")
            self.robo.wink(left=True)
        elif self.demo_step == 16:
            self.robo.wink(right=True)
        elif self.demo_step == 17:
            self.update_status("Demo: Cyclops mode")
            self.robo.set_cyclops(True)
        elif self.demo_step == 18:
            self.update_status("Demo: Back to normal")
            self.robo.set_cyclops(False)
            self.robo.mood = DEFAULT
            self.robo.curious = False
        elif self.demo_step == 19:
            self.update_status("Demo: Auto-blinker enabled")
            self.robo.set_auto_blinker(ON, 2, 1)
        elif self.demo_step == 20:
            self.update_status("Demo: Idle mode enabled")
            self.robo.set_idle_mode(ON, 1, 1)
        elif self.demo_step >= 21:
            # Reset demo
            self.demo_step = 0
            self.update_status("Demo: Restarting sequence...")
    
    def handle_custom_input(self, event):
        """Handle custom input events for the demo."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                # Toggle demo mode
                self.demo_mode = not self.demo_mode
                if self.demo_mode:
                    self.update_status("Auto demo started")
                    self.demo_step = 0
                    self.demo_timer = ticks_ms()
                else:
                    self.update_status("Auto demo stopped")
                return True
            elif event.key == pygame.K_s:
                # Show current status
                mood_name = self.mood_names[self.robo.mood]
                pos_name = self.position_names[self.robo.position] if self.robo.position < len(self.position_names) else "CUSTOM"
                status = f"Mood: {mood_name}, Position: {pos_name}"
                if self.robo.autoblinker:
                    status += ", Auto-blink: ON"
                if self.robo.idle:
                    status += ", Idle: ON"
                if self.robo._cyclops:
                    status += ", Cyclops: ON"
                if self.robo.curious:
                    status += ", Curious: ON"
                self.update_status(status)
                return True
        
        return False
    
    def run(self):
        """Run the interactive demo."""
        self.show_welcome_message()
        
        try:
            # Add custom input handler
            original_handle_events = self.robo.handle_events
            
            def enhanced_handle_events():
                for event in pygame.event.get():
                    # Try custom input first
                    if not self.handle_custom_input(event):
                        # Put the event back for normal processing
                        pygame.event.post(event)
                        break
                # Call original handler
                original_handle_events()
            
            self.robo.handle_events = enhanced_handle_events
            
            # Initial setup
            self.robo.set_auto_blinker(OFF)  # Start with manual control
            self.robo.set_idle_mode(OFF)
            self.robo.mood = DEFAULT
            
            # Give eyes time to open
            start_time = ticks_ms()
            while ticks_diff(ticks_ms(), start_time) < 1000:
                self.robo.handle_events()
                self.robo.update()
                if not self.robo.running:
                    return 0
            
            self.update_status("Interactive demo ready! Press D for auto demo, H for help")
            
            # Main loop with demo sequence
            while self.robo.running:
                self.robo.handle_events()
                self.run_demo_sequence()
                self.robo.update()
                self.robo.clock.tick(60)
            
        except KeyboardInterrupt:
            print("\nShutting down...")
        except Exception as e:
            print(f"Error: {e}")
            return 1
        
        return 0

def main():
    """Main function."""
    demo = InteractiveDemo()
    return demo.run()

if __name__ == "__main__":
    sys.exit(main())