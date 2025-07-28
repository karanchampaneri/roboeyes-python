#!/usr/bin/env python3
"""
RoboEyes Desktop - Configuration Demo

This example demonstrates different eye shapes, behaviors, and configuration options.
It shows how to customize the appearance and behavior of RoboEyes through various
configuration parameters and runtime settings.

This example is inspired by the original MicroPython test_interactive.py but focuses
specifically on demonstrating configuration options and eye customization.
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

class ConfigurationDemo:
    """Demonstration of RoboEyes configuration options."""
    
    def __init__(self):
        """Initialize the configuration demo."""
        # Configuration presets
        self.config_presets = [
            {
                "name": "Default Eyes",
                "width": 36, "height": 36, "radius": 8, "spacing": 10,
                "description": "Standard robot eyes"
            },
            {
                "name": "Round Eyes", 
                "width": 36, "height": 36, "radius": 18, "spacing": 10,
                "description": "Perfectly round eyes"
            },
            {
                "name": "Wide Eyes",
                "width": 50, "height": 30, "radius": 5, "spacing": 8,
                "description": "Wide, alert expression"
            },
            {
                "name": "Narrow Eyes",
                "width": 20, "height": 40, "radius": 10, "spacing": 15,
                "description": "Tall, narrow eyes"
            },
            {
                "name": "Tiny Eyes",
                "width": 15, "height": 15, "radius": 7, "spacing": 20,
                "description": "Small, cute eyes"
            },
            {
                "name": "Large Eyes",
                "width": 55, "height": 55, "radius": 12, "spacing": 5,
                "description": "Big, expressive eyes"
            },
            {
                "name": "Square Eyes",
                "width": 35, "height": 35, "radius": 2, "spacing": 12,
                "description": "Angular, robotic look"
            },
            {
                "name": "Overlapping Eyes",
                "width": 40, "height": 35, "radius": 15, "spacing": -5,
                "description": "Eyes that overlap slightly"
            }
        ]
        
        self.current_preset = 0
        self.auto_cycle = False
        self.cycle_timer = 0
        self.cycle_interval = 3000  # 3 seconds per preset
        
        # Behavior presets
        self.behavior_presets = [
            {
                "name": "Calm",
                "auto_blink": (ON, 4, 2),
                "idle": (OFF,),
                "mood": DEFAULT,
                "description": "Relaxed, occasional blinking"
            },
            {
                "name": "Alert",
                "auto_blink": (ON, 2, 1),
                "idle": (ON, 3, 2),
                "mood": CURIOUS,
                "description": "Active, looking around"
            },
            {
                "name": "Sleepy",
                "auto_blink": (ON, 6, 3),
                "idle": (OFF,),
                "mood": TIRED,
                "description": "Slow blinking, tired"
            },
            {
                "name": "Excited",
                "auto_blink": (ON, 1, 0),
                "idle": (ON, 1, 1),
                "mood": HAPPY,
                "description": "Fast blinking, active movement"
            },
            {
                "name": "Angry",
                "auto_blink": (ON, 3, 1),
                "idle": (OFF,),
                "mood": ANGRY,
                "description": "Aggressive expression"
            },
            {
                "name": "Frozen",
                "auto_blink": (OFF,),
                "idle": (OFF,),
                "mood": FROZEN,
                "description": "Frozen with horizontal flicker"
            },
            {
                "name": "Scary",
                "auto_blink": (ON, 5, 4),
                "idle": (OFF,),
                "mood": SCARY,
                "description": "Menacing with vertical flicker"
            }
        ]
        
        self.current_behavior = 0
        
        # Create configuration
        self.config = RoboEyesConfig(
            display_width=128,
            display_height=64,
            window_width=1100,
            window_height=750,
            frame_rate=60,
            resizable=True,
            fullscreen=False
        )
        
        # Initialize RoboEyes
        self.robo = DesktopRoboEyes(config=self.config)
        
        # Status display
        self.show_info = True
        self.info_timer = 0
    
    def apply_eye_preset(self, preset_index):
        """Apply an eye shape preset."""
        if 0 <= preset_index < len(self.config_presets):
            preset = self.config_presets[preset_index]
            self.robo.eyes_width(preset["width"], preset["width"])
            self.robo.eyes_height(preset["height"], preset["height"])
            self.robo.eyes_radius(preset["radius"], preset["radius"])
            self.robo.eyes_spacing(preset["spacing"])
            self.current_preset = preset_index
            print(f"Applied preset: {preset['name']} - {preset['description']}")
    
    def apply_behavior_preset(self, preset_index):
        """Apply a behavior preset."""
        if 0 <= preset_index < len(self.behavior_presets):
            preset = self.behavior_presets[preset_index]
            
            # Apply auto-blinker settings
            if len(preset["auto_blink"]) == 3:
                self.robo.set_auto_blinker(*preset["auto_blink"])
            else:
                self.robo.set_auto_blinker(preset["auto_blink"][0])
            
            # Apply idle settings
            if len(preset["idle"]) == 3:
                self.robo.set_idle_mode(*preset["idle"])
            else:
                self.robo.set_idle_mode(preset["idle"][0])
            
            # Apply mood
            self.robo.mood = preset["mood"]
            
            self.current_behavior = preset_index
            print(f"Applied behavior: {preset['name']} - {preset['description']}")
    
    def show_instructions(self):
        """Display instructions for the demo."""
        print("=" * 70)
        print("RoboEyes Desktop - Configuration Demo")
        print("=" * 70)
        print()
        print("EYE SHAPE PRESETS (Q/W to cycle):")
        for i, preset in enumerate(self.config_presets):
            print(f"  {i+1}. {preset['name']} - {preset['description']}")
        print()
        print("BEHAVIOR PRESETS (A/S to cycle):")
        for i, preset in enumerate(self.behavior_presets):
            print(f"  {i+1}. {preset['name']} - {preset['description']}")
        print()
        print("CONTROLS:")
        print("  Q/W: Previous/Next eye shape preset")
        print("  A/S: Previous/Next behavior preset")
        print("  1-8: Jump to specific eye shape preset")
        print("  F1-F7: Jump to specific behavior preset")
        print("  C: Toggle auto-cycle through eye shapes")
        print("  R: Reset to defaults")
        print("  T: Test cyclops mode")
        print("  Y: Test curious mode")
        print("  I: Show current configuration info")
        print("  H: Show help overlay")
        print("  ESC or close window: Exit")
        print()
        print("You can also use normal RoboEyes controls while testing configurations.")
        print("=" * 70)
    
    def show_current_config(self):
        """Display current configuration information."""
        eye_preset = self.config_presets[self.current_preset]
        behavior_preset = self.behavior_presets[self.current_behavior]
        
        print("\n" + "=" * 50)
        print("CURRENT CONFIGURATION:")
        print("=" * 50)
        print(f"Eye Shape: {eye_preset['name']}")
        print(f"  Width: {eye_preset['width']}, Height: {eye_preset['height']}")
        print(f"  Radius: {eye_preset['radius']}, Spacing: {eye_preset['spacing']}")
        print(f"Behavior: {behavior_preset['name']}")
        print(f"  Description: {behavior_preset['description']}")
        print(f"  Mood: {['DEFAULT', 'TIRED', 'ANGRY', 'HAPPY', 'FROZEN', 'SCARY', 'CURIOUS'][self.robo.mood]}")
        print(f"  Auto-blink: {'ON' if self.robo.autoblinker else 'OFF'}")
        print(f"  Idle mode: {'ON' if self.robo.idle else 'OFF'}")
        print(f"  Cyclops: {'ON' if self.robo._cyclops else 'OFF'}")
        print(f"  Curious: {'ON' if self.robo.curious else 'OFF'}")
        print("=" * 50)
    
    def handle_config_input(self, event):
        """Handle input for configuration changes."""
        if event.type == pygame.KEYDOWN:
            # Eye shape preset controls
            if event.key == pygame.K_q:
                new_preset = (self.current_preset - 1) % len(self.config_presets)
                self.apply_eye_preset(new_preset)
                return True
            elif event.key == pygame.K_w:
                new_preset = (self.current_preset + 1) % len(self.config_presets)
                self.apply_eye_preset(new_preset)
                return True
            
            # Behavior preset controls
            elif event.key == pygame.K_a:
                new_behavior = (self.current_behavior - 1) % len(self.behavior_presets)
                self.apply_behavior_preset(new_behavior)
                return True
            elif event.key == pygame.K_s:
                new_behavior = (self.current_behavior + 1) % len(self.behavior_presets)
                self.apply_behavior_preset(new_behavior)
                return True
            
            # Direct preset selection (1-8)
            elif pygame.K_1 <= event.key <= pygame.K_8:
                preset_num = event.key - pygame.K_1
                if preset_num < len(self.config_presets):
                    self.apply_eye_preset(preset_num)
                return True
            
            # Direct behavior selection (F1-F7)
            elif pygame.K_F1 <= event.key <= pygame.K_F7:
                behavior_num = event.key - pygame.K_F1
                if behavior_num < len(self.behavior_presets):
                    self.apply_behavior_preset(behavior_num)
                return True
            
            # Special controls
            elif event.key == pygame.K_c:
                self.auto_cycle = not self.auto_cycle
                if self.auto_cycle:
                    print("Auto-cycle enabled - eye shapes will change automatically")
                    self.cycle_timer = ticks_ms()
                else:
                    print("Auto-cycle disabled")
                return True
            
            elif event.key == pygame.K_r:
                print("Resetting to default configuration...")
                self.apply_eye_preset(0)  # Default eyes
                self.apply_behavior_preset(0)  # Calm behavior
                self.robo.set_cyclops(False)
                self.robo.curious = False
                return True
            
            elif event.key == pygame.K_t:
                cyclops_state = not self.robo._cyclops
                self.robo.set_cyclops(cyclops_state)
                print(f"Cyclops mode: {'ON' if cyclops_state else 'OFF'}")
                return True
            
            elif event.key == pygame.K_y:
                curious_state = not self.robo.curious
                self.robo.curious = curious_state
                print(f"Curious mode: {'ON' if curious_state else 'OFF'}")
                return True
            
            elif event.key == pygame.K_i:
                self.show_current_config()
                return True
        
        return False
    
    def update_auto_cycle(self):
        """Update auto-cycling through eye presets."""
        if not self.auto_cycle:
            return
        
        current_time = ticks_ms()
        if ticks_diff(current_time, self.cycle_timer) >= self.cycle_interval:
            self.cycle_timer = current_time
            new_preset = (self.current_preset + 1) % len(self.config_presets)
            self.apply_eye_preset(new_preset)
    
    def run(self):
        """Run the configuration demo."""
        self.show_instructions()
        
        try:
            # Add custom input handler
            original_handle_events = self.robo.handle_events
            
            def enhanced_handle_events():
                for event in pygame.event.get():
                    # Try config input first
                    if not self.handle_config_input(event):
                        # Put the event back for normal processing
                        pygame.event.post(event)
                        break
                # Call original handler
                original_handle_events()
            
            self.robo.handle_events = enhanced_handle_events
            
            # Apply initial presets
            self.apply_eye_preset(0)  # Default eyes
            self.apply_behavior_preset(0)  # Calm behavior
            
            # Give eyes time to open
            start_time = ticks_ms()
            while ticks_diff(ticks_ms(), start_time) < 1000:
                self.robo.handle_events()
                self.robo.update()
                if not self.robo.running:
                    return 0
            
            print("Configuration demo ready!")
            print("Use Q/W to cycle through eye shapes, A/S for behaviors")
            print("Press I to show current configuration details")
            
            # Main loop
            while self.robo.running:
                self.robo.handle_events()
                self.update_auto_cycle()
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
    demo = ConfigurationDemo()
    return demo.run()

if __name__ == "__main__":
    sys.exit(main())