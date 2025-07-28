"""
Input handling system for desktop RoboEyes application.

This module provides keyboard and mouse input processing, mapping input events
to RoboEyes functions and providing interactive controls for testing and demonstration.
"""

import pygame
from typing import Dict, Callable, Optional, List, Tuple
from dataclasses import dataclass, field

from .exceptions import InputError
from .logging import get_logger


@dataclass
class InputMapping:
    """Configuration for input mappings."""
    key_mappings: Dict[int, Callable] = field(default_factory=dict)
    mouse_mappings: Dict[str, Callable] = field(default_factory=dict)


class InputManager:
    """
    Manages keyboard and mouse input for the RoboEyes desktop application.
    
    This class handles mapping keyboard keys and mouse events to RoboEyes functions,
    providing interactive controls for mood changes, animations, and positioning.
    """
    
    def __init__(self, roboeyes_instance):
        """
        Initialize the InputManager.
        
        Args:
            roboeyes_instance: The DesktopRoboEyes instance to control
        """
        self.roboeyes = roboeyes_instance
        self.help_visible = False
        self.help_surface = None
        self._setup_default_mappings()
    
    def _setup_default_mappings(self) -> None:
        """Set up default keyboard and mouse mappings."""
        # Import mood constants from the roboeyes module
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        
        from roboeyes.desktop_roboeyes import (
            DEFAULT, TIRED, ANGRY, HAPPY, FROZEN, SCARY, CURIOUS,
            N, NE, E, SE, S, SW, W, NW
        )
        
        # Mood mappings
        self.key_mappings = {
            pygame.K_1: lambda: self.roboeyes.set_mood(DEFAULT),
            pygame.K_2: lambda: self.roboeyes.set_mood(TIRED),
            pygame.K_3: lambda: self.roboeyes.set_mood(ANGRY),
            pygame.K_4: lambda: self.roboeyes.set_mood(HAPPY),
            pygame.K_5: lambda: self.roboeyes.set_mood(FROZEN),
            pygame.K_6: lambda: self.roboeyes.set_mood(SCARY),
            pygame.K_7: lambda: self.roboeyes.set_mood(CURIOUS),
            
            # Position mappings (numpad)
            pygame.K_KP8: lambda: self.roboeyes.set_position(N),      # North
            pygame.K_KP9: lambda: self.roboeyes.set_position(NE),     # North-East
            pygame.K_KP6: lambda: self.roboeyes.set_position(E),      # East
            pygame.K_KP3: lambda: self.roboeyes.set_position(SE),     # South-East
            pygame.K_KP2: lambda: self.roboeyes.set_position(S),      # South
            pygame.K_KP1: lambda: self.roboeyes.set_position(SW),     # South-West
            pygame.K_KP4: lambda: self.roboeyes.set_position(W),      # West
            pygame.K_KP7: lambda: self.roboeyes.set_position(NW),     # North-West
            pygame.K_KP5: lambda: self.roboeyes.set_position(DEFAULT), # Center
            
            # Alternative position mappings (arrow keys + WASD)
            pygame.K_UP: lambda: self.roboeyes.set_position(N),
            pygame.K_DOWN: lambda: self.roboeyes.set_position(S),
            pygame.K_LEFT: lambda: self.roboeyes.set_position(W),
            pygame.K_RIGHT: lambda: self.roboeyes.set_position(E),
            pygame.K_w: lambda: self.roboeyes.set_position(N),
            pygame.K_s: lambda: self.roboeyes.set_position(S),
            pygame.K_a: lambda: self.roboeyes.set_position(W),
            pygame.K_d: lambda: self.roboeyes.set_position(E),
            
            # Animation controls
            pygame.K_SPACE: lambda: self.roboeyes.blink(),
            pygame.K_q: lambda: self.roboeyes.wink(left=True),
            pygame.K_e: lambda: self.roboeyes.wink(right=True),
            pygame.K_c: lambda: self.roboeyes.confuse(),
            pygame.K_l: lambda: self.roboeyes.laugh(),
            
            # Eye state controls
            pygame.K_o: lambda: self.roboeyes.open(),
            pygame.K_x: lambda: self.roboeyes.close(),
            
            # Mode toggles
            pygame.K_b: self._toggle_auto_blinker,
            pygame.K_i: self._toggle_idle_mode,
            pygame.K_y: self._toggle_cyclops,
            pygame.K_r: self._toggle_curious,
            
            # Help display
            pygame.K_h: self._toggle_help,
            pygame.K_F1: self._toggle_help,
            
            # Performance monitoring
            pygame.K_p: self._toggle_performance_display,
        }
        
        # Mouse mappings
        self.mouse_mappings = {
            'left_click': lambda pos: self._handle_mouse_click(pos),
            'right_click': lambda pos: self._handle_right_click(pos),
        }
    
    def _toggle_auto_blinker(self) -> None:
        """Toggle auto-blinker mode."""
        current_state = self.roboeyes.autoblinker
        self.roboeyes.set_auto_blinker(not current_state)
        print(f"Auto-blinker: {'ON' if not current_state else 'OFF'}")
    
    def _toggle_idle_mode(self) -> None:
        """Toggle idle mode."""
        current_state = self.roboeyes.idle
        self.roboeyes.set_idle_mode(not current_state)
        print(f"Idle mode: {'ON' if not current_state else 'OFF'}")
    
    def _toggle_cyclops(self) -> None:
        """Toggle cyclops mode."""
        current_state = self.roboeyes.cyclops
        self.roboeyes.set_cyclops(not current_state)
        print(f"Cyclops mode: {'ON' if not current_state else 'OFF'}")
    
    def _toggle_curious(self) -> None:
        """Toggle curious mode."""
        current_state = self.roboeyes.curious
        self.roboeyes.set_curious(not current_state)
        print(f"Curious mode: {'ON' if not current_state else 'OFF'}")
    
    def _toggle_help(self) -> None:
        """Toggle help display."""
        self.help_visible = not self.help_visible
        if self.help_visible:
            self._create_help_surface()
    
    def _toggle_performance_display(self) -> None:
        """Toggle performance monitoring display."""
        if hasattr(self.roboeyes, 'performance_monitor'):
            self.roboeyes.performance_monitor.toggle_performance_display()
            state = "ON" if self.roboeyes.performance_monitor.show_performance else "OFF"
            print(f"Performance display: {state}")
    
    def _handle_mouse_click(self, pos: Tuple[int, int]) -> None:
        """
        Handle left mouse click events.
        
        Args:
            pos: Mouse click position (x, y)
        """
        # Convert window coordinates to eye display coordinates
        eye_pos = self._window_to_eye_coords(pos)
        if eye_pos:
            # Move eyes to look at the clicked position
            self._look_at_position(eye_pos)
    
    def _handle_right_click(self, pos: Tuple[int, int]) -> None:
        """
        Handle right mouse click events.
        
        Args:
            pos: Mouse click position (x, y)
        """
        # Right click triggers a blink
        self.roboeyes.blink()
    
    def _window_to_eye_coords(self, window_pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """
        Convert window coordinates to eye display coordinates.
        
        Args:
            window_pos: Position in window coordinates (x, y)
            
        Returns:
            Position in eye display coordinates, or None if outside display area
        """
        x, y = window_pos
        
        # Check if click is within the scaled eye display area
        if (x < self.roboeyes.offset_x or x >= self.roboeyes.offset_x + self.roboeyes.scaled_width or
            y < self.roboeyes.offset_y or y >= self.roboeyes.offset_y + self.roboeyes.scaled_height):
            return None
        
        # Convert to eye display coordinates
        eye_x = int((x - self.roboeyes.offset_x) / self.roboeyes.scale)
        eye_y = int((y - self.roboeyes.offset_y) / self.roboeyes.scale)
        
        return (eye_x, eye_y)
    
    def _look_at_position(self, eye_pos: Tuple[int, int]) -> None:
        """
        Make the eyes look at a specific position.
        
        Args:
            eye_pos: Position in eye display coordinates (x, y)
        """
        x, y = eye_pos
        
        # Calculate relative position for eye movement
        center_x = self.roboeyes.display_width // 2
        center_y = self.roboeyes.display_height // 2
        
        # Determine the closest predefined position
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        
        from roboeyes.desktop_roboeyes import N, NE, E, SE, S, SW, W, NW, DEFAULT
        
        if y < center_y // 2:  # Top third
            if x < center_x // 2:
                position = NW
            elif x > center_x + center_x // 2:
                position = NE
            else:
                position = N
        elif y > center_y + center_y // 2:  # Bottom third
            if x < center_x // 2:
                position = SW
            elif x > center_x + center_x // 2:
                position = SE
            else:
                position = S
        else:  # Middle third
            if x < center_x // 2:
                position = W
            elif x > center_x + center_x // 2:
                position = E
            else:
                position = DEFAULT
        
        self.roboeyes.set_position(position)
    
    def _create_help_surface(self) -> None:
        """Create the help display surface."""
        logger = get_logger()
        
        try:
            # Initialize font if not already done
            if not hasattr(self, 'font'):
                pygame.font.init()
                self.font = pygame.font.Font(None, 24)
                self.small_font = pygame.font.Font(None, 18)
            
            # Help text content
            help_lines = [
                "RoboEyes Desktop Controls",
                "",
                "Moods:",
                "  1 - Default    2 - Tired     3 - Angry",
                "  4 - Happy      5 - Frozen    6 - Scary",
                "  7 - Curious",
                "",
                "Positions:",
                "  Arrow Keys / WASD - Move eyes",
                "  Numpad 1-9 - Precise positioning",
                "",
                "Animations:",
                "  SPACE - Blink    Q - Wink Left   E - Wink Right",
                "  C - Confuse      L - Laugh",
                "  O - Open Eyes    X - Close Eyes",
                "",
                "Modes:",
                "  B - Toggle Auto-Blinker",
                "  I - Toggle Idle Mode",
                "  Y - Toggle Cyclops Mode",
                "  R - Toggle Curious Mode",
                "",
                "Mouse:",
                "  Left Click - Look at position",
                "  Right Click - Blink",
                "",
                "Other:",
                "  H / F1 - Toggle this help",
                "  P - Toggle performance display",
                "  F11 - Toggle fullscreen",
                "  ESC - Exit fullscreen",
            ]
            
            # Calculate surface size
            line_height = 25
            max_width = 0
            for line in help_lines:
                text_surface = self.small_font.render(line, True, (255, 255, 255))
                max_width = max(max_width, text_surface.get_width())
            
            surface_width = max_width + 40
            surface_height = len(help_lines) * line_height + 40
            
            # Create semi-transparent background
            self.help_surface = pygame.Surface((surface_width, surface_height))
            self.help_surface.set_alpha(200)
            self.help_surface.fill((0, 0, 0))
            
            # Add border
            pygame.draw.rect(self.help_surface, (255, 255, 255), 
                            (0, 0, surface_width, surface_height), 2)
            
            # Render text lines
            y_offset = 20
            for i, line in enumerate(help_lines):
                if i == 0:  # Title
                    text_surface = self.font.render(line, True, (255, 255, 255))
                else:
                    text_surface = self.small_font.render(line, True, (255, 255, 255))
                
                self.help_surface.blit(text_surface, (20, y_offset))
                y_offset += line_height
                
        except pygame.error as e:
            error_msg = f"Pygame error creating help surface: {e}"
            logger.error(error_msg)
            # Create a simple fallback surface
            self.help_surface = pygame.Surface((400, 300))
            self.help_surface.fill((0, 0, 0))
        except Exception as e:
            error_msg = f"Unexpected error creating help surface: {e}"
            logger.exception(error_msg)
            # Create a simple fallback surface
            self.help_surface = pygame.Surface((400, 300))
            self.help_surface.fill((0, 0, 0))
    
    def process_event(self, event) -> bool:
        """
        Process a Pygame event for input handling.
        
        Args:
            event: Pygame event to process
            
        Returns:
            True if the event was handled, False otherwise
        """
        logger = get_logger()
        
        try:
            if event.type == pygame.KEYDOWN:
                return self._handle_keydown(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                return self._handle_mouse_button(event)
            return False
        except Exception as e:
            # Gracefully handle any input processing errors
            error_msg = f"Input processing error: {e}"
            logger.error(error_msg)
            return False
    
    def _handle_keydown(self, event) -> bool:
        """
        Handle keyboard input events.
        
        Args:
            event: Pygame KEYDOWN event
            
        Returns:
            True if the key was handled, False otherwise
        """
        logger = get_logger()
        
        try:
            if event.key in self.key_mappings:
                logger.debug(f"Processing key: {pygame.key.name(event.key)}")
                self.key_mappings[event.key]()
                return True
            return False
        except Exception as e:
            error_msg = f"Error handling keydown event for key {pygame.key.name(event.key)}: {e}"
            logger.error(error_msg)
            return False
    
    def _handle_mouse_button(self, event) -> bool:
        """
        Handle mouse button events.
        
        Args:
            event: Pygame MOUSEBUTTONDOWN event
            
        Returns:
            True if the mouse event was handled, False otherwise
        """
        logger = get_logger()
        
        try:
            if event.button == 1:  # Left click
                if 'left_click' in self.mouse_mappings:
                    logger.debug(f"Processing left mouse click at {event.pos}")
                    self.mouse_mappings['left_click'](event.pos)
                    return True
            elif event.button == 3:  # Right click
                if 'right_click' in self.mouse_mappings:
                    logger.debug(f"Processing right mouse click at {event.pos}")
                    self.mouse_mappings['right_click'](event.pos)
                    return True
            return False
        except Exception as e:
            error_msg = f"Error handling mouse button {event.button} at {event.pos}: {e}"
            logger.error(error_msg)
            return False
    
    def add_key_mapping(self, key: int, action: Callable) -> None:
        """
        Add or update a keyboard mapping.
        
        Args:
            key: Pygame key constant
            action: Callable to execute when key is pressed
        """
        self.key_mappings[key] = action
    
    def remove_key_mapping(self, key: int) -> None:
        """
        Remove a keyboard mapping.
        
        Args:
            key: Pygame key constant to remove
        """
        if key in self.key_mappings:
            del self.key_mappings[key]
    
    def add_mouse_mapping(self, button: str, action: Callable) -> None:
        """
        Add or update a mouse mapping.
        
        Args:
            button: Mouse button name ('left_click', 'right_click')
            action: Callable to execute when button is pressed
        """
        self.mouse_mappings[button] = action
    
    def remove_mouse_mapping(self, button: str) -> None:
        """
        Remove a mouse mapping.
        
        Args:
            button: Mouse button name to remove
        """
        if button in self.mouse_mappings:
            del self.mouse_mappings[button]
    
    def get_key_mappings(self) -> Dict[int, Callable]:
        """
        Get current keyboard mappings.
        
        Returns:
            Dictionary of key mappings
        """
        return self.key_mappings.copy()
    
    def get_mouse_mappings(self) -> Dict[str, Callable]:
        """
        Get current mouse mappings.
        
        Returns:
            Dictionary of mouse mappings
        """
        return self.mouse_mappings.copy()
    
    def render_help(self, screen: pygame.Surface) -> None:
        """
        Render the help display on the screen.
        
        Args:
            screen: Pygame surface to render help on
        """
        if self.help_visible and self.help_surface:
            # Center the help surface on the screen
            screen_width, screen_height = screen.get_size()
            help_width, help_height = self.help_surface.get_size()
            
            x = (screen_width - help_width) // 2
            y = (screen_height - help_height) // 2
            
            screen.blit(self.help_surface, (x, y))
    
    def is_help_visible(self) -> bool:
        """
        Check if help display is currently visible.
        
        Returns:
            True if help is visible, False otherwise
        """
        return self.help_visible
    
    def get_help_text(self) -> List[str]:
        """
        Get the help text as a list of strings.
        
        Returns:
            List of help text lines
        """
        return [
            "RoboEyes Desktop Controls",
            "",
            "Moods: 1-7 (Default, Tired, Angry, Happy, Frozen, Scary, Curious)",
            "Positions: Arrow Keys, WASD, or Numpad 1-9",
            "Animations: SPACE (Blink), Q/E (Wink), C (Confuse), L (Laugh)",
            "Eye State: O (Open), X (Close)",
            "Modes: B (Auto-Blinker), I (Idle), Y (Cyclops), R (Curious)",
            "Mouse: Left Click (Look), Right Click (Blink)",
            "Help: H or F1, Fullscreen: F11, Exit Fullscreen: ESC"
        ]