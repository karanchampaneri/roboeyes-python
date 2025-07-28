#!/usr/bin/env python3
"""
RoboEyes Desktop - Animation Sequence Demo

This example demonstrates how to create and use animation sequences in RoboEyes.
It shows how to create complex, timed animations without using delays.

This is the desktop port of the original MicroPython test_anim_sequence.py example.
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

class AnimationSequenceDemo:
    """Demonstration of RoboEyes animation sequences."""
    
    def __init__(self):
        """Initialize the animation sequence demo."""
        # Create configuration for the demo
        self.config = RoboEyesConfig(
            display_width=128,
            display_height=64,
            window_width=900,
            window_height=650,
            frame_rate=60,
            resizable=True,
            fullscreen=False
        )
        
        # Initialize RoboEyes
        self.robo = DesktopRoboEyes(config=self.config)
        
        # Demo state
        self.current_sequence = 0
        self.sequences_created = False
    
    def create_sequences(self):
        """Create various animation sequences."""
        print("Creating animation sequences...")
        
        # Sequence 1: Basic mood demonstration
        seq1 = self.robo.sequences.add("mood_demo")
        seq1.step(1000, lambda robo: robo.open())
        seq1.step(2000, lambda robo: robo.set_mood(HAPPY))
        seq1.step(2100, lambda robo: robo.laugh())
        seq1.step(4000, lambda robo: robo.set_mood(TIRED))
        seq1.step(6000, lambda robo: robo.set_mood(ANGRY))
        seq1.step(6100, lambda robo: robo.confuse())
        seq1.step(8000, lambda robo: robo.set_mood(CURIOUS))
        seq1.step(10000, lambda robo: robo.set_mood(DEFAULT))
        seq1.step(11000, lambda robo: print("Mood demo sequence complete!"))
        
        # Sequence 2: Position and movement demonstration
        seq2 = self.robo.sequences.add("position_demo")
        seq2.step(500, lambda robo: robo.open())
        seq2.step(1000, lambda robo: robo.set_position(N))
        seq2.step(1500, lambda robo: robo.set_position(NE))
        seq2.step(2000, lambda robo: robo.set_position(E))
        seq2.step(2500, lambda robo: robo.set_position(SE))
        seq2.step(3000, lambda robo: robo.set_position(S))
        seq2.step(3500, lambda robo: robo.set_position(SW))
        seq2.step(4000, lambda robo: robo.set_position(W))
        seq2.step(4500, lambda robo: robo.set_position(NW))
        seq2.step(5000, lambda robo: robo.set_position(DEFAULT))
        seq2.step(6000, lambda robo: print("Position demo sequence complete!"))
        
        # Sequence 3: Animation and effects demonstration
        seq3 = self.robo.sequences.add("effects_demo")
        seq3.step(500, lambda robo: robo.open())
        seq3.step(1000, lambda robo: robo.wink(left=True))
        seq3.step(2000, lambda robo: robo.wink(right=True))
        seq3.step(3000, lambda robo: robo.set_mood(FROZEN))  # Enables horizontal flicker
        seq3.step(5000, lambda robo: robo.set_mood(SCARY))   # Enables vertical flicker
        seq3.step(7000, lambda robo: robo.set_mood(DEFAULT))
        seq3.step(7500, lambda robo: robo.horiz_flicker(True, 3))
        seq3.step(9000, lambda robo: robo.horiz_flicker(False))
        seq3.step(9500, lambda robo: robo.vert_flicker(True, 2))
        seq3.step(11000, lambda robo: robo.vert_flicker(False))
        seq3.step(12000, lambda robo: print("Effects demo sequence complete!"))
        
        # Sequence 4: Cyclops and curious mode demonstration
        seq4 = self.robo.sequences.add("special_modes_demo")
        seq4.step(500, lambda robo: robo.open())
        seq4.step(1000, lambda robo: robo.set_cyclops(True))
        seq4.step(2000, lambda robo: robo.set_mood(HAPPY))
        seq4.step(2100, lambda robo: robo.laugh())
        seq4.step(4000, lambda robo: robo.set_cyclops(False))
        seq4.step(5000, lambda robo: robo.set_mood(CURIOUS))
        seq4.step(5100, lambda robo: setattr(robo, 'curious', True))
        seq4.step(6000, lambda robo: robo.set_position(E))
        seq4.step(7000, lambda robo: robo.set_position(W))
        seq4.step(8000, lambda robo: robo.set_position(DEFAULT))
        seq4.step(9000, lambda robo: setattr(robo, 'curious', False))
        seq4.step(10000, lambda robo: robo.set_mood(DEFAULT))
        seq4.step(11000, lambda robo: print("Special modes demo sequence complete!"))
        
        # Sequence 5: Auto features demonstration
        seq5 = self.robo.sequences.add("auto_features_demo")
        seq5.step(500, lambda robo: robo.open())
        seq5.step(1000, lambda robo: robo.set_auto_blinker(ON, 1, 0))  # Fast blinking
        seq5.step(1100, lambda robo: print("Auto-blinker enabled (fast)"))
        seq5.step(4000, lambda robo: robo.set_auto_blinker(ON, 3, 2))  # Normal blinking
        seq5.step(4100, lambda robo: print("Auto-blinker set to normal speed"))
        seq5.step(6000, lambda robo: robo.set_idle_mode(ON, 1, 1))     # Enable idle mode
        seq5.step(6100, lambda robo: print("Idle mode enabled"))
        seq5.step(12000, lambda robo: robo.set_auto_blinker(OFF))
        seq5.step(12100, lambda robo: robo.set_idle_mode(OFF))
        seq5.step(12200, lambda robo: print("Auto features disabled"))
        seq5.step(13000, lambda robo: print("Auto features demo sequence complete!"))
        
        # Sequence 6: Eye shape customization demonstration
        seq6 = self.robo.sequences.add("shape_demo")
        seq6.step(500, lambda robo: robo.open())
        seq6.step(1000, lambda robo: robo.eyes_width(20, 20))
        seq6.step(1100, lambda robo: print("Narrow eyes"))
        seq6.step(3000, lambda robo: robo.eyes_width(50, 50))
        seq6.step(3100, lambda robo: print("Wide eyes"))
        seq6.step(5000, lambda robo: robo.eyes_height(20, 20))
        seq6.step(5100, lambda robo: print("Short eyes"))
        seq6.step(7000, lambda robo: robo.eyes_height(50, 50))
        seq6.step(7100, lambda robo: print("Tall eyes"))
        seq6.step(9000, lambda robo: robo.eyes_radius(2, 2))
        seq6.step(9100, lambda robo: print("Sharp corners"))
        seq6.step(11000, lambda robo: robo.eyes_radius(20, 20))
        seq6.step(11100, lambda robo: print("Very round eyes"))
        seq6.step(13000, lambda robo: robo.eyes_spacing(30))
        seq6.step(13100, lambda robo: print("Wide spacing"))
        seq6.step(15000, lambda robo: robo.eyes_spacing(-5))
        seq6.step(15100, lambda robo: print("Overlapping eyes"))
        seq6.step(17000, lambda robo: self.reset_eye_shape())
        seq6.step(17100, lambda robo: print("Reset to default shape"))
        seq6.step(18000, lambda robo: print("Shape demo sequence complete!"))
        
        self.sequences_created = True
        print(f"Created {len(self.robo.sequences)} animation sequences")
    
    def reset_eye_shape(self):
        """Reset eye shape to defaults."""
        self.robo.eyes_width(36, 36)
        self.robo.eyes_height(36, 36)
        self.robo.eyes_radius(8, 8)
        self.robo.eyes_spacing(10)
    
    def show_instructions(self):
        """Display instructions for the demo."""
        print("=" * 60)
        print("RoboEyes Desktop - Animation Sequence Demo")
        print("=" * 60)
        print()
        print("This demo showcases various animation sequences:")
        print("1. Mood Demo - Different emotional expressions")
        print("2. Position Demo - Eye movement in all directions")
        print("3. Effects Demo - Flickering and animation effects")
        print("4. Special Modes Demo - Cyclops and curious modes")
        print("5. Auto Features Demo - Auto-blinker and idle mode")
        print("6. Shape Demo - Eye shape customization")
        print()
        print("CONTROLS:")
        print("  1-6: Start specific sequence")
        print("  SPACE: Start next sequence in order")
        print("  R: Restart current sequence")
        print("  S: Stop all sequences")
        print("  H: Show help overlay")
        print("  ESC or close window: Exit")
        print()
        print("The sequences will run automatically once started.")
        print("You can interact with the eyes using normal controls while sequences run.")
        print("=" * 60)
    
    def handle_sequence_input(self, event):
        """Handle input for sequence control."""
        import pygame
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.start_sequence(0, "mood_demo")
                return True
            elif event.key == pygame.K_2:
                self.start_sequence(1, "position_demo")
                return True
            elif event.key == pygame.K_3:
                self.start_sequence(2, "effects_demo")
                return True
            elif event.key == pygame.K_4:
                self.start_sequence(3, "special_modes_demo")
                return True
            elif event.key == pygame.K_5:
                self.start_sequence(4, "auto_features_demo")
                return True
            elif event.key == pygame.K_6:
                self.start_sequence(5, "shape_demo")
                return True
            elif event.key == pygame.K_SPACE:
                self.start_next_sequence()
                return True
            elif event.key == pygame.K_r:
                self.restart_current_sequence()
                return True
            elif event.key == pygame.K_s:
                self.stop_all_sequences()
                return True
        
        return False
    
    def start_sequence(self, index, name):
        """Start a specific sequence."""
        if index < len(self.robo.sequences):
            # Stop all sequences first
            for seq in self.robo.sequences:
                seq.reset()
            self.robo.sequences[index].start()
            self.current_sequence = index
            print(f"Started sequence {index + 1}: {name}")
        else:
            print(f"Sequence {index + 1} not found")
    
    def start_next_sequence(self):
        """Start the next sequence in order."""
        self.current_sequence = (self.current_sequence + 1) % len(self.robo.sequences)
        sequence = self.robo.sequences[self.current_sequence]
        # Stop all sequences first
        for seq in self.robo.sequences:
            seq.reset()
        sequence.start()
        print(f"Started sequence {self.current_sequence + 1}: {sequence.name}")
    
    def restart_current_sequence(self):
        """Restart the current sequence."""
        if self.current_sequence < len(self.robo.sequences):
            sequence = self.robo.sequences[self.current_sequence]
            sequence.reset()
            sequence.start()
            print(f"Restarted sequence {self.current_sequence + 1}: {sequence.name}")
    
    def stop_all_sequences(self):
        """Stop all running sequences."""
        for seq in self.robo.sequences:
            seq.reset()
        print("All sequences stopped")
    
    def run(self):
        """Run the animation sequence demo."""
        self.show_instructions()
        
        try:
            # Create all sequences
            self.create_sequences()
            
            # Add custom input handler
            original_handle_events = self.robo.handle_events
            
            def enhanced_handle_events():
                import pygame
                for event in pygame.event.get():
                    # Try sequence input first
                    if not self.handle_sequence_input(event):
                        # Put the event back for normal processing
                        pygame.event.post(event)
                        break
                # Call original handler
                original_handle_events()
            
            self.robo.handle_events = enhanced_handle_events
            
            # Initial setup
            self.robo.set_auto_blinker(OFF)
            self.robo.set_idle_mode(OFF)
            self.robo.mood = DEFAULT
            self.robo.close()  # Start with closed eyes
            
            print("Animation sequence demo ready!")
            print("Press SPACE to start the first sequence, or 1-6 for specific sequences")
            
            # Main loop
            while self.robo.running:
                self.robo.handle_events()
                self.robo.update()
                
                # Check if current sequence is done and auto-advance
                if (self.current_sequence < len(self.robo.sequences) and 
                    self.robo.sequences[self.current_sequence].done):
                    # Wait a moment then start next sequence
                    import time
                    time.sleep(1)
                    if self.robo.running:  # Check if still running after sleep
                        self.start_next_sequence()
                
                self.robo.clock.tick(60)
            
        except KeyboardInterrupt:
            print("\nShutting down...")
        except Exception as e:
            print(f"Error: {e}")
            return 1
        
        return 0

def main():
    """Main function."""
    demo = AnimationSequenceDemo()
    return demo.run()

if __name__ == "__main__":
    sys.exit(main())