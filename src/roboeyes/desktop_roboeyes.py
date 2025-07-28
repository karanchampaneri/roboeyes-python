"""
Desktop implementation of RoboEyes for standard Python environments.

This module provides a desktop-compatible version of the RoboEyes library that uses
Pygame for graphics rendering instead of MicroPython's FrameBuffer and OLED displays.
"""

import pygame
import sys
from typing import Optional, Callable, Tuple

# Import desktop compatibility layers
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from desktop.framebuffer import FrameBufferCompat
from desktop.graphics import PygameGraphicsUtil
from desktop.timing import ticks_ms, ticks_diff, ticks_add, FrameRateLimiter
from desktop.sequences import Sequences
from desktop.input_manager import InputManager
from desktop.config import RoboEyesConfig, ConfigManager
from desktop.platform_compat import get_platform_compat
from desktop.performance import PerformanceMonitor, DirtyRectTracker
from desktop.exceptions import (
    PygameInitializationError, DisplayError, WindowError, 
    AnimationError, ConfigurationError
)
from desktop.logging import get_logger

# Import constants and random from standard library
from random import randint
import time

# Usage of monochrome display colors
BGCOLOR = 0  # background and overlays
FGCOLOR = 1  # drawings

# For mood type switch
DEFAULT = 0
TIRED = 1
ANGRY = 2
HAPPY = 3
FROZEN = 4
SCARY = 5
CURIOUS = 6

# For turning things on or off
ON = 1
OFF = 0

# For switch "predefined positions"
N = 1   # north, top center
NE = 2  # north-east, top right
E = 3   # east, middle right
SE = 4  # south-east, bottom right
S = 5   # south, bottom center
SW = 6  # south-west, bottom left
W = 7   # west, middle left
NW = 8  # north-west, top left 
# for middle center set "DEFAULT"





class DesktopRoboEyes:
    """
    Desktop implementation of RoboEyes using Pygame.
    
    This class provides the same API as the original MicroPython RoboEyes
    but uses Pygame for graphics rendering and standard Python timing functions.
    """
    
    def __init__(self, config: Optional[RoboEyesConfig] = None, 
                 width: int = 128, height: int = 64, frame_rate: int = 20, 
                 window_width: int = 800, window_height: int = 600,
                 bgcolor: int = BGCOLOR, fgcolor: int = FGCOLOR,
                 resizable: bool = True, fullscreen: bool = False):
        """
        Initialize the desktop RoboEyes application.
        
        Args:
            config: Optional RoboEyesConfig instance for configuration
            width: Width of the eye display area in pixels (overridden by config)
            height: Height of the eye display area in pixels (overridden by config)
            frame_rate: Target frame rate for animations (overridden by config)
            window_width: Width of the application window (overridden by config)
            window_height: Height of the application window (overridden by config)
            bgcolor: Background color (0 or 1)
            fgcolor: Foreground color (0 or 1)
            resizable: Whether the window can be resized (overridden by config)
            fullscreen: Whether to start in fullscreen mode (overridden by config)
            
        Raises:
            PygameInitializationError: If Pygame initialization fails
            DisplayError: If display creation fails
            ConfigurationError: If configuration is invalid
        """
        logger = get_logger()
        
        try:
            # Apply platform-specific optimizations
            platform_compat = get_platform_compat()
            platform_compat.apply_pygame_hints()
            
            # Initialize Pygame
            logger.info("Initializing Pygame...")
            pygame.init()
            
            # Check if Pygame initialized successfully
            if not pygame.get_init():
                raise PygameInitializationError("Pygame failed to initialize")
                
            logger.info(f"Pygame initialized successfully on {platform_compat.platform.value}")
            logger.debug(f"Platform info: {platform_compat.platform_info}")
            
        except pygame.error as e:
            error_msg = f"Pygame initialization failed: {e}"
            logger.error(error_msg)
            raise PygameInitializationError(error_msg)
        
        # Use configuration if provided, otherwise use parameters
        if config is not None:
            self.config = config
            self.display_width = config.display_width
            self.display_height = config.display_height
            self.window_width = config.window_width
            self.window_height = config.window_height
            self.resizable = config.resizable
            self.fullscreen = config.fullscreen
            frame_rate = config.frame_rate
        else:
            # Create default config for backward compatibility
            self.config = RoboEyesConfig(
                display_width=width,
                display_height=height,
                window_width=window_width,
                window_height=window_height,
                resizable=resizable,
                fullscreen=fullscreen,
                frame_rate=frame_rate
            )
            self.display_width = width
            self.display_height = height
            self.window_width = window_width
            self.window_height = window_height
            self.resizable = resizable
            self.fullscreen = fullscreen
        
        # Window state tracking
        self.minimized = False
        self.window_focused = True
        
        try:
            # Create the main window with appropriate flags
            window_flags = 0
            if self.resizable:
                window_flags |= pygame.RESIZABLE
            if self.fullscreen:
                window_flags |= pygame.FULLSCREEN
            
            logger.info(f"Creating display window: {self.window_width}x{self.window_height}")
            self.screen = pygame.display.set_mode((self.window_width, self.window_height), window_flags)
            pygame.display.set_caption("RoboEyes Desktop")
            
            logger.info("Display window created successfully")
            
        except pygame.error as e:
            error_msg = f"Failed to create display window: {e}"
            logger.error(error_msg)
            raise DisplayError(error_msg)
        
        try:
            # Create the eye display surface (scaled to fit window)
            logger.debug(f"Creating eye surface: {self.display_width}x{self.display_height}")
            self.eye_surface = pygame.Surface((self.display_width, self.display_height))
            
            # Calculate initial scaling
            self._calculate_scaling()
            
            # Initialize performance monitoring
            self.performance_monitor = PerformanceMonitor()
            
            # Create FrameBuffer compatibility wrapper with optimization
            self.fb = FrameBufferCompat(self.eye_surface, use_optimization=True)
            
            # Create graphics utility with dirty rectangle tracking
            dirty_tracker = self.fb.optimized_fb.dirty_tracker if self.fb.optimized_fb else None
            self.gfx = PygameGraphicsUtil(self.eye_surface, dirty_tracker)
            
            logger.debug("Eye surface and graphics utilities created successfully")
            
        except pygame.error as e:
            error_msg = f"Failed to create eye surface: {e}"
            logger.error(error_msg)
            raise DisplayError(error_msg)
        
        # Store colors
        self.bgcolor = bgcolor
        self.fgcolor = fgcolor
        
        # Set up the on_show callback to handle display updates
        self.on_show = self._pygame_show
        
        # Initialize the core RoboEyes properties (copied from original)
        self.screenWidth = width
        self.screenHeight = height
        
        self.sequences = Sequences(self)
        
        self.fpsTimer = 0
        self._position = 0
        
        # Mood and expression properties
        self._mood = DEFAULT
        self.tired = False
        self.angry = False
        self.happy = False
        
        self._curious = False
        self._cyclops = False
        self.eyeL_open = False
        self.eyeR_open = False
        
        # Eyes Geometry
        self.spaceBetweenDefault = 10
        
        # EYE LEFT - size and border radius
        self.eyeLwidthDefault = 36
        self.eyeLheightDefault = 36
        self.eyeLwidthCurrent = self.eyeLwidthDefault
        self.eyeLheightCurrent = 1  # start with closed eye
        self.eyeLwidthNext = self.eyeLwidthDefault
        self.eyeLheightNext = self.eyeLheightDefault
        self.eyeLheightOffset = 0
        # Border Radius 
        self.eyeLborderRadiusDefault = 8
        self.eyeLborderRadiusCurrent = self.eyeLborderRadiusDefault
        self.eyeLborderRadiusNext = self.eyeLborderRadiusDefault
        
        # EYE RIGHT - size and border radius
        self.eyeRwidthDefault = self.eyeLwidthDefault
        self.eyeRheightDefault = self.eyeLheightDefault
        self.eyeRwidthCurrent = self.eyeRwidthDefault
        self.eyeRheightCurrent = 1  # start with closed eye
        self.eyeRwidthNext = self.eyeRwidthDefault
        self.eyeRheightNext = self.eyeRheightDefault
        self.eyeRheightOffset = 0
        # Border Radius
        self.eyeRborderRadiusDefault = 8
        self.eyeRborderRadiusCurrent = self.eyeRborderRadiusDefault
        self.eyeRborderRadiusNext = self.eyeRborderRadiusDefault
        
        # EYE LEFT - Coordinates
        self.eyeLxDefault = int(((self.screenWidth)-(self.eyeLwidthDefault+self.spaceBetweenDefault+self.eyeRwidthDefault))/2)
        self.eyeLyDefault = int((self.screenHeight-self.eyeLheightDefault)/2)
        self.eyeLx = self.eyeLxDefault
        self.eyeLy = self.eyeLyDefault
        self.eyeLxNext = self.eyeLx
        self.eyeLyNext = self.eyeLy
        
        # EYE RIGHT - Coordinates
        self.eyeRxDefault = self.eyeLx+self.eyeLwidthCurrent+self.spaceBetweenDefault
        self.eyeRyDefault = self.eyeLy
        self.eyeRx = self.eyeRxDefault
        self.eyeRy = self.eyeRyDefault
        self.eyeRxNext = self.eyeRx
        self.eyeRyNext = self.eyeRy
        
        # BOTH EYES - Eyelid properties
        self.eyelidsHeightMax = int(self.eyeLheightDefault/2)
        self.eyelidsTiredHeight = 0
        self.eyelidsTiredHeightNext = self.eyelidsTiredHeight
        self.eyelidsAngryHeight = 0
        self.eyelidsAngryHeightNext = self.eyelidsAngryHeight
        # Bottom happy eyelids offset
        self.eyelidsHappyBottomOffsetMax = int(self.eyeLheightDefault/2)+3
        self.eyelidsHappyBottomOffset = 0
        self.eyelidsHappyBottomOffsetNext = 0
        # Space between eyes
        self.spaceBetweenCurrent = self.spaceBetweenDefault
        self.spaceBetweenNext = 10
        
        # Macro Animations
        # Horizontal flicker/shiver
        self.hFlicker = False
        self.hFlickerAlternate = False
        self.hFlickerAmplitude = 2
        
        # Vertical flicker/shiver
        self.vFlicker = False
        self.vFlickerAlternate = False
        self.vFlickerAmplitude = 10
        
        # Auto blinking
        self.autoblinker = False
        self.blinkInterval = 1
        self.blinkIntervalVariation = 4
        self.blinktimer = 0
        
        # Idle mode
        self.idle = False
        self.idleInterval = 1
        self.idleIntervalVariation = 3
        self.idleAnimationTimer = 0
        
        # Eyes confused
        self._confused = False
        self.confusedAnimationTimer = 0
        self.confusedAnimationDuration = 500
        self.confusedToggle = True
        
        # Eyes laughing
        self._laugh = False
        self.laughAnimationTimer = 0
        self.laughAnimationDuration = 500
        self.laughToggle = True
        
        try:
            # Initialize display and frame rate
            logger.debug("Initializing display and animation system...")
            self.clear_display()
            self.on_show(self)
            self.eyeLheightCurrent = 1  # start with closed eyes
            self.eyeRheightCurrent = 1  # start with closed eyes
            self.set_framerate(frame_rate)
            
            # Initialize input manager
            logger.debug("Initializing input manager...")
            self.input_manager = InputManager(self)
            
            # Application state
            self.running = True
            self.clock = pygame.time.Clock()
            
            logger.info("RoboEyes Desktop initialized successfully")
            
        except Exception as e:
            error_msg = f"Failed to complete initialization: {e}"
            logger.exception(error_msg)
            # Clean up Pygame if initialization fails
            pygame.quit()
            raise PygameInitializationError(error_msg)
    
    def _calculate_scaling(self) -> None:
        """
        Calculate scaling factors and offsets for centering the eye display.
        
        This method recalculates the scaling when the window is resized.
        """
        # Calculate scaling for centering the eye display in the window
        self.scale_x = self.window_width / self.display_width
        self.scale_y = self.window_height / self.display_height
        self.scale = min(self.scale_x, self.scale_y)  # Maintain aspect ratio
        
        self.scaled_width = int(self.display_width * self.scale)
        self.scaled_height = int(self.display_height * self.scale)
        self.offset_x = (self.window_width - self.scaled_width) // 2
        self.offset_y = (self.window_height - self.scaled_height) // 2
    
    def _pygame_show(self, roboeyes_instance) -> None:
        """
        Handle Pygame display updates with performance optimizations.
        
        This method replaces the original on_show callback to handle
        Pygame-specific display operations with dirty rectangle tracking
        and performance monitoring.
        
        Args:
            roboeyes_instance: The RoboEyes instance (self)
        """
        logger = get_logger()
        
        try:
            # Skip rendering if window is minimized
            if self.minimized:
                return
            
            # Get dirty rectangles for optimized updates
            dirty_rects = self.fb.get_dirty_rects()
            total_pixels_updated = 0
            
            # Determine update strategy - disable dirty rects for now to fix frame clearing issue
            use_dirty_rects = False  # Force full screen updates to ensure proper clearing
            
            if use_dirty_rects:
                # Optimized update using dirty rectangles
                scaled_surface = pygame.transform.scale(self.eye_surface, (self.scaled_width, self.scaled_height))
                
                # Update only dirty regions
                update_rects = []
                for rect in dirty_rects:
                    # Scale dirty rectangle to window coordinates
                    scaled_rect = pygame.Rect(
                        int(rect.x * self.scale) + self.offset_x,
                        int(rect.y * self.scale) + self.offset_y,
                        int(rect.width * self.scale),
                        int(rect.height * self.scale)
                    )
                    
                    # Clear the region with black background
                    self.screen.fill((0, 0, 0), scaled_rect)
                    
                    # Blit the corresponding region from the scaled surface
                    source_rect = pygame.Rect(
                        int(rect.x * self.scale),
                        int(rect.y * self.scale),
                        int(rect.width * self.scale),
                        int(rect.height * self.scale)
                    )
                    
                    self.screen.blit(scaled_surface, scaled_rect, source_rect)
                    update_rects.append(scaled_rect)
                    total_pixels_updated += rect.width * rect.height
                
                # Update only the dirty regions
                pygame.display.update(update_rects)
                
            else:
                # Full screen update (fallback for large changes)
                scaled_surface = pygame.transform.scale(self.eye_surface, (self.scaled_width, self.scaled_height))
                
                # Clear the screen with black background
                self.screen.fill((0, 0, 0))
                
                # Blit the scaled eye surface to the center of the screen
                self.screen.blit(scaled_surface, (self.offset_x, self.offset_y))
                
                # Full screen update
                pygame.display.flip()
                total_pixels_updated = self.display_width * self.display_height
            
            # Render help overlay if visible (only if input_manager is initialized)
            if hasattr(self, 'input_manager'):
                self.input_manager.render_help(self.screen)
            
            # Update performance metrics
            metrics = self.performance_monitor.update(
                dirty_rects_count=len(dirty_rects),
                total_pixels_updated=total_pixels_updated
            )
            
            # Render performance overlay if enabled
            self.performance_monitor.render_performance_overlay(self.screen, metrics)
            
            # Log performance summary periodically
            self.performance_monitor.log_performance_summary()
            
        except pygame.error as e:
            logger.error(f"Pygame error during display update: {e}")
            # Don't re-raise to keep the application running
        except Exception as e:
            logger.error(f"Unexpected error during display update: {e}")
            # Don't re-raise to keep the application running
    
    def handle_events(self) -> None:
        """Handle Pygame events including window management and input."""
        logger = get_logger()
        
        try:
            for event in pygame.event.get():
                try:
                    if event.type == pygame.QUIT:
                        logger.info("Quit event received")
                        self.running = False
                    elif event.type == pygame.VIDEORESIZE:
                        self._handle_window_resize(event.w, event.h)
                    elif event.type == pygame.ACTIVEEVENT:
                        self._handle_window_focus(event)
                    elif event.type == pygame.KEYDOWN:
                        # Try input manager first, then fallback to window management
                        if not self.input_manager.process_event(event):
                            self._handle_keydown(event)
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        self.input_manager.process_event(event)
                except Exception as e:
                    logger.error(f"Error handling event {event.type}: {e}")
                    # Continue processing other events
                    continue
                    
        except pygame.error as e:
            logger.error(f"Pygame error in event handling: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error in event handling: {e}")
    
    def _handle_window_resize(self, new_width: int, new_height: int) -> None:
        """
        Handle window resize events.
        
        Args:
            new_width: New window width
            new_height: New window height
        """
        logger = get_logger()
        
        try:
            if not self.resizable:
                logger.debug("Window resize ignored - resizing disabled")
                return
            
            logger.debug(f"Handling window resize: {new_width}x{new_height}")
            
            # Validate new dimensions
            if new_width < 100 or new_height < 100:
                logger.warning(f"Window resize dimensions too small: {new_width}x{new_height}")
                return
                
            # Update window dimensions
            self.window_width = new_width
            self.window_height = new_height
            
            # Recreate the screen surface with new dimensions
            window_flags = 0
            if self.resizable:
                window_flags |= pygame.RESIZABLE
            if self.fullscreen:
                window_flags |= pygame.FULLSCREEN
                
            self.screen = pygame.display.set_mode((new_width, new_height), window_flags)
            
            # Recalculate scaling
            self._calculate_scaling()
            
            logger.debug(f"Window resized successfully to {new_width}x{new_height}")
            
        except pygame.error as e:
            error_msg = f"Pygame error during window resize: {e}"
            logger.error(error_msg)
            raise WindowError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error during window resize: {e}"
            logger.exception(error_msg)
            raise WindowError(error_msg)
    
    def _handle_window_focus(self, event) -> None:
        """
        Handle window focus and minimize events.
        
        Args:
            event: Pygame ACTIVEEVENT
        """
        if event.state == 1:  # Window focus/unfocus
            self.window_focused = bool(event.gain)
        elif event.state == 2:  # Window minimize/restore
            self.minimized = not bool(event.gain)
    
    def _handle_keydown(self, event) -> None:
        """
        Handle keyboard events for window management.
        
        Args:
            event: Pygame KEYDOWN event
        """
        # Toggle fullscreen with F11
        if event.key == pygame.K_F11:
            self.toggle_fullscreen()
        # Exit fullscreen with Escape
        elif event.key == pygame.K_ESCAPE and self.fullscreen:
            self.toggle_fullscreen()
    
    def toggle_fullscreen(self) -> None:
        """Toggle between fullscreen and windowed mode."""
        self.fullscreen = not self.fullscreen
        
        if self.fullscreen:
            # Get current display size for fullscreen
            display_info = pygame.display.Info()
            self.screen = pygame.display.set_mode((display_info.current_w, display_info.current_h), pygame.FULLSCREEN)
            self.window_width = display_info.current_w
            self.window_height = display_info.current_h
        else:
            # Return to windowed mode with original dimensions
            window_flags = 0
            if self.resizable:
                window_flags |= pygame.RESIZABLE
            self.screen = pygame.display.set_mode((800, 600), window_flags)  # Default window size
            self.window_width = 800
            self.window_height = 600
        
        # Recalculate scaling for new window size
        self._calculate_scaling()
    
    def set_window_size(self, width: int, height: int) -> None:
        """
        Set the window size programmatically.
        
        Args:
            width: New window width
            height: New window height
        """
        if self.fullscreen:
            return  # Cannot resize in fullscreen mode
            
        self._handle_window_resize(width, height)
    
    def get_window_size(self) -> Tuple[int, int]:
        """
        Get the current window size.
        
        Returns:
            Tuple of (width, height)
        """
        return (self.window_width, self.window_height)
    
    def get_display_scale(self) -> float:
        """
        Get the current display scaling factor.
        
        Returns:
            Current scaling factor
        """
        return self.scale
    
    def is_fullscreen(self) -> bool:
        """
        Check if the window is in fullscreen mode.
        
        Returns:
            True if in fullscreen mode, False otherwise
        """
        return self.fullscreen
    
    def is_minimized(self) -> bool:
        """
        Check if the window is minimized.
        
        Returns:
            True if minimized, False otherwise
        """
        return self.minimized
    
    def is_focused(self) -> bool:
        """
        Check if the window has focus.
        
        Returns:
            True if window has focus, False otherwise
        """
        return self.window_focused
    
    def get_display_dimensions(self) -> Tuple[int, int]:
        """
        Get the eye display dimensions (not window dimensions).
        
        Returns:
            Tuple of (width, height) for the eye display area
        """
        return (self.display_width, self.display_height)
    
    def get_scaled_dimensions(self) -> Tuple[int, int]:
        """
        Get the scaled eye display dimensions within the window.
        
        Returns:
            Tuple of (scaled_width, scaled_height)
        """
        return (self.scaled_width, self.scaled_height)
    
    def get_display_offset(self) -> Tuple[int, int]:
        """
        Get the offset for centering the eye display in the window.
        
        Returns:
            Tuple of (offset_x, offset_y)
        """
        return (self.offset_x, self.offset_y)
    
    def run(self) -> None:
        """
        Main application loop.
        
        Runs the RoboEyes animation loop with Pygame event handling.
        """
        logger = get_logger()
        logger.info("Starting RoboEyes main loop")
        
        try:
            while self.running:
                try:
                    self.handle_events()
                    self.update()
                    self.clock.tick(60)  # Limit to 60 FPS for smooth window handling
                except KeyboardInterrupt:
                    logger.info("Keyboard interrupt received, shutting down")
                    self.running = False
                except Exception as e:
                    logger.error(f"Error in main loop: {e}")
                    # Continue running unless it's a critical error
                    if isinstance(e, (DisplayError, PygameInitializationError)):
                        logger.critical("Critical error, shutting down")
                        self.running = False
                    
        except Exception as e:
            logger.exception(f"Fatal error in main loop: {e}")
        finally:
            logger.info("Shutting down RoboEyes")
            self._cleanup()
    
    def _cleanup(self) -> None:
        """Clean up resources before shutdown."""
        logger = get_logger()
        
        try:
            logger.debug("Cleaning up resources...")
            pygame.quit()
            logger.info("RoboEyes shutdown complete")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        finally:
            sys.exit()
    
    # --- METHODS FROM ORIGINAL ROBOEYES (with desktop timing) ---
    
    def update(self):
        """Check if a sequence step must be executed and update display."""
        logger = get_logger()
        
        try:
            self.sequences.update()
            # Limit drawing updates to defined max framerate
            if ticks_diff(ticks_ms(), self.fpsTimer) >= self.frameInterval:
                # Clear display before drawing to ensure clean frame
                self.clear_display()
                self.draw_eyes()
                self.fpsTimer = ticks_ms()
        except Exception as e:
            logger.error(f"Error in animation update: {e}")
            # Don't re-raise to keep the application running
    
    def clear_display(self):
        """Clear the display buffer."""
        self.fb.fill(self.bgcolor)
    
    def set_framerate(self, fps):
        """Calculate frame interval based on defined frameRate."""
        self.frameInterval = 1000//fps
    
    def eyes_width(self, leftEye=None, rightEye=None):
        """Set eye width for left and/or right eye."""
        if leftEye is not None:
            self.eyeLwidthNext = leftEye
            self.eyeLwidthDefault = leftEye
        if rightEye is not None:
            self.eyeRwidthNext = rightEye
            self.eyeRwidthDefault = rightEye
    
    def eyes_height(self, leftEye=None, rightEye=None):
        """Set eye height for left and/or right eye."""
        if leftEye is not None:
            self.eyeLheightNext = leftEye
            self.eyeLheightDefault = leftEye
        if rightEye is not None:
            self.eyeRheightNext = rightEye
            self.eyeRheightDefault = rightEye
    
    def eyes_radius(self, leftEye=None, rightEye=None):
        """Set border radius for left and right eye."""
        if leftEye is not None:
            self.eyeLborderRadiusNext = leftEye
            self.eyeLborderRadiusDefault = leftEye
        if rightEye is not None:
            self.eyeRborderRadiusNext = rightEye
            self.eyeRborderRadiusDefault = rightEye
    
    def eyes_spacing(self, space):
        """Set space between the eyes, can also be negative."""
        self.spaceBetweenNext = space
        self.spaceBetweenDefault = space
    
    @property
    def mood(self):
        """Return the current mood."""
        return self._mood
    
    @mood.setter
    def mood(self, mood):
        """Set mood expression."""
        # Handle mood transitions
        if (self._mood in (SCARY, FROZEN)) and not(mood in (SCARY, FROZEN)):
            self.horiz_flicker(False)
            self.vert_flicker(False)
        
        if self._curious and (mood != CURIOUS):
            self._curious = False
        
        if mood == TIRED:
            self.tired = True
            self.angry = False
            self.happy = False
        elif mood == ANGRY:
            self.tired = False
            self.angry = True
            self.happy = False
        elif mood == HAPPY:
            self.tired = False
            self.angry = False
            self.happy = True
        elif mood == FROZEN:
            self.tired = False
            self.angry = False
            self.happy = False
            self.horiz_flicker(True, 2)
            self.vert_flicker(False)
        elif mood == SCARY:
            self.tired = True
            self.angry = False
            self.happy = False
            self.horiz_flicker(False)
            self.vert_flicker(True, 2)
        elif mood == CURIOUS:
            self.tired = False
            self.angry = False
            self.happy = False
            self._curious = True
        else:
            self.tired = False
            self.angry = False
            self.happy = False
        self._mood = mood
    
    def set_mood(self, value):
        """Callable for lambda expression."""
        self.mood = value
    
    @property
    def position(self):
        """Return the current position."""
        return self._position
    
    @position.setter
    def position(self, direction):
        """Set predefined position."""
        if direction == N:  # North, top center
            self.eyeLxNext = self.get_screen_constraint_X()//2
            self.eyeLyNext = 0
        elif direction == NE:  # North-east, top right
            self.eyeLxNext = self.get_screen_constraint_X()
            self.eyeLyNext = 0
        elif direction == E:  # East, middle right
            self.eyeLxNext = self.get_screen_constraint_X()
            self.eyeLyNext = self.get_screen_constraint_Y()//2
        elif direction == SE:  # South-east, bottom right
            self.eyeLxNext = self.get_screen_constraint_X()
            self.eyeLyNext = self.get_screen_constraint_Y()
        elif direction == S:  # South, bottom center
            self.eyeLxNext = self.get_screen_constraint_X()//2
            self.eyeLyNext = self.get_screen_constraint_Y()
        elif direction == SW:  # South-west, bottom left
            self.eyeLxNext = 0
            self.eyeLyNext = self.get_screen_constraint_Y()
        elif direction == W:  # West, middle left
            self.eyeLxNext = 0
            self.eyeLyNext = self.get_screen_constraint_Y()//2
        elif direction == NW:  # North-west, top left
            self.eyeLxNext = 0
            self.eyeLyNext = 0
        else:  # Middle center
            self.eyeLxNext = self.get_screen_constraint_X()//2
            self.eyeLyNext = self.get_screen_constraint_Y()//2
        self._position = direction
    
    def set_position(self, value):
        """Callable for lambda expression."""
        self.position = value
    
    def set_auto_blinker(self, active, interval=None, variation=None):
        """Set automated eye blinking."""
        self.autoblinker = active
        if interval is not None:
            self.blinkInterval = interval
        if variation is not None:
            self.blinkIntervalVariation = variation
    
    def set_idle_mode(self, active, interval=None, variation=None):
        """Set idle mode - automated eye repositioning."""
        self.idle = active
        if interval is not None:
            self.idleInterval = interval
        if variation is not None:
            self.idleIntervalVariation = variation
    
    @property
    def curious(self):
        """Return curious mode state."""
        return self._curious
    
    @curious.setter
    def curious(self, enable):
        """Set curious mode."""
        self._curious = enable
    
    def set_curious(self, value):
        """Callable for lambda expression."""
        self.curious = value
    
    @property
    def cyclops(self):
        """Return cyclops mode state."""
        return self._cyclops
    
    @cyclops.setter
    def cyclops(self, enabled):
        """Set cyclops mode."""
        self._cyclops = enabled
    
    def set_cyclops(self, value):
        """Callable for lambda expression."""
        self.cyclops = value
    
    def horiz_flicker(self, enable, amplitude=None):
        """Set horizontal flickering."""
        self.hFlicker = enable
        if amplitude is not None:
            self.hFlickerAmplitude = amplitude
    
    def vert_flicker(self, enable, amplitude=None):
        """Set vertical flickering."""
        self.vFlicker = enable
        if amplitude is not None:
            self.vFlickerAmplitude = amplitude
    
    def get_screen_constraint_X(self):
        """Returns the max x position for left eye."""
        return self.screenWidth-self.eyeLwidthCurrent-self.spaceBetweenCurrent-self.eyeRwidthCurrent
    
    def get_screen_constraint_Y(self):
        """Returns the max y position for left eye."""
        return self.screenHeight-self.eyeLheightDefault
    
    def close(self, left=None, right=None):
        """Close both eyes or specific eye."""
        if (left is None) and (right is None):
            self.eyeLheightNext = 1
            self.eyeRheightNext = 1
            self.eyeL_open = False
            self.eyeR_open = False
        else:
            if left is not None:
                self.eyeLheightNext = 1
                self.eyeL_open = False
            if right is not None:
                self.eyeRheightNext = 1
                self.eyeR_open = False
    
    def open(self, left=None, right=None):
        """Open both eyes or specific eye."""
        if (left is None) and (right is None):
            self.eyeL_open = True
            self.eyeR_open = True
        else:
            if left is not None:
                self.eyeL_open = True
            if right is not None:
                self.eyeR_open = True
    
    def blink(self, left=None, right=None):
        """Trigger eyeblink animation."""
        if (left is None) and (right is None):
            self.close()
            self.open()
        else:
            self.close(left, right)
            self.open(left, right)
    
    def confuse(self):
        """Play confused animation."""
        self._confused = True
    
    def laugh(self):
        """Play laugh animation."""
        self._laugh = True
    
    def wink(self, left=None, right=None):
        """Wink with specified eye."""
        assert left or right, "Wink must be activated on right or left"
        self.autoblinker = False
        self.idle = False
        self.blink(left=left, right=right)
    
    def draw_eyes(self):
        """
        Draw the eyes with all animations and expressions.
        
        This is the core rendering method that handles all eye drawing logic,
        including animations, moods, and expressions.
        """
        # PRE-CALCULATIONS - EYE SIZES AND VALUES FOR ANIMATION TWEENINGS
        
        # Vertical size offset for larger eyes when looking left or right (curious gaze)
        if self._curious:
            if self.eyeLxNext <= 10:
                self.eyeLheightOffset = 8
            elif (self.eyeLxNext >= self.get_screen_constraint_X()-10) and self._cyclops:
                self.eyeLheightOffset = 8
            else:
                self.eyeLheightOffset = 0  # left eye
            
            if self.eyeRxNext >= (self.screenWidth-self.eyeRwidthCurrent-10):
                self.eyeRheightOffset = 8
            else:
                self.eyeRheightOffset = 0  # right eye
        else:
            self.eyeLheightOffset = 0  # reset height offset for left eye
            self.eyeRheightOffset = 0  # reset height offset for right eye
        
        # Left eye height
        self.eyeLheightCurrent = (self.eyeLheightCurrent + self.eyeLheightNext + self.eyeLheightOffset)//2
        self.eyeLy += (self.eyeLheightDefault-self.eyeLheightCurrent)//2  # vertical centering of eye when closing
        self.eyeLy -= self.eyeLheightOffset//2
        # Right eye height
        self.eyeRheightCurrent = (self.eyeRheightCurrent + self.eyeRheightNext + self.eyeRheightOffset)//2
        self.eyeRy += (self.eyeRheightDefault-self.eyeRheightCurrent)//2  # vertical centering of eye when closing
        self.eyeRy -= self.eyeRheightOffset//2
        
        # Open eyes again after closing them
        if self.eyeL_open:
            if self.eyeLheightCurrent <= (1 + self.eyeLheightOffset):
                self.eyeLheightNext = self.eyeLheightDefault
        
        if self.eyeR_open:
            if self.eyeRheightCurrent <= (1 + self.eyeRheightOffset):
                self.eyeRheightNext = self.eyeRheightDefault
        
        # Left eye width
        self.eyeLwidthCurrent = (self.eyeLwidthCurrent + self.eyeLwidthNext)//2
        # Right eye width
        self.eyeRwidthCurrent = (self.eyeRwidthCurrent + self.eyeRwidthNext)//2
        
        # Space between eyes
        self.spaceBetweenCurrent = (self.spaceBetweenCurrent + self.spaceBetweenNext)//2
        
        # Left eye coordinates
        self.eyeLx = (self.eyeLx + self.eyeLxNext)//2
        self.eyeLy = (self.eyeLy + self.eyeLyNext)//2
        # Right eye coordinates
        self.eyeRxNext = self.eyeLxNext+self.eyeLwidthCurrent+self.spaceBetweenCurrent  # right eye's x position depends on left eyes position + the space between
        self.eyeRyNext = self.eyeLyNext  # right eye's y position should be the same as for the left eye
        self.eyeRx = (self.eyeRx + self.eyeRxNext)//2
        self.eyeRy = (self.eyeRy + self.eyeRyNext)//2
        
        # Left eye border radius
        self.eyeLborderRadiusCurrent = (self.eyeLborderRadiusCurrent + self.eyeLborderRadiusNext)//2
        # Right eye border radius
        self.eyeRborderRadiusCurrent = (self.eyeRborderRadiusCurrent + self.eyeRborderRadiusNext)//2
        
        # APPLYING MACRO ANIMATIONS
        
        if self.autoblinker:
            if ticks_diff(ticks_ms(), self.blinktimer) >= 0:
                self.blink()
                self.blinktimer = ticks_add(ticks_ms(), (self.blinkInterval*1000)+(randint(0, self.blinkIntervalVariation)*1000))  # calculate next time for blinking
        
        # Laughing - eyes shaking up and down for the duration defined by laughAnimationDuration (default = 500ms)
        if self._laugh:
            if self.laughToggle:
                self.vert_flicker(1, 5)
                self.laughAnimationTimer = ticks_ms()
                self.laughToggle = False
            elif ticks_diff(ticks_ms(), self.laughAnimationTimer) >= self.laughAnimationDuration:
                self.vert_flicker(0, 0)
                self.laughToggle = True
                self._laugh = False
        
        # Confused - eyes shaking left and right for the duration defined by confusedAnimationDuration (default = 500ms)
        if self._confused:
            if self.confusedToggle:
                self.horiz_flicker(1, 20)
                self.confusedAnimationTimer = ticks_ms()
                self.confusedToggle = False
            elif ticks_diff(ticks_ms(), self.confusedAnimationTimer) >= self.confusedAnimationDuration:
                self.horiz_flicker(0, 0)
                self.confusedToggle = True
                self._confused = False
        
        # Idle - eyes moving to random positions on screen
        if self.idle:
            if ticks_diff(ticks_ms(), self.idleAnimationTimer) >= 0:
                self.eyeLxNext = randint(0, self.get_screen_constraint_X())
                self.eyeLyNext = randint(0, self.get_screen_constraint_Y())
                self.idleAnimationTimer = ticks_add(ticks_ms(), (self.idleInterval*1000)+(randint(0, self.idleIntervalVariation)*1000))  # calculate next time for eyes repositioning
        
        # Adding offsets for horizontal flickering/shivering
        if self.hFlicker:
            if self.hFlickerAlternate:
                self.eyeLx += self.hFlickerAmplitude
                self.eyeRx += self.hFlickerAmplitude
            else:
                self.eyeLx -= self.hFlickerAmplitude
                self.eyeRx -= self.hFlickerAmplitude
            self.hFlickerAlternate = not(self.hFlickerAlternate)
        
        # Adding offsets for vertical flickering/shivering
        if self.vFlicker:
            if self.vFlickerAlternate:
                self.eyeLy += self.vFlickerAmplitude
                self.eyeRy += self.vFlickerAmplitude
            else:
                self.eyeLy -= self.vFlickerAmplitude
                self.eyeRy -= self.vFlickerAmplitude
            
            self.vFlickerAlternate = not(self.vFlickerAlternate)
        
        # Cyclops mode, set second eye's size and space between to 0
        if self._cyclops:
            self.eyeRwidthCurrent = 0
            self.eyeRheightCurrent = 0
            self.spaceBetweenCurrent = 0
        
        # ACTUAL DRAWINGS
        
        # Draw basic eye rectangles
        self.gfx.fill_rrect(self.eyeLx, self.eyeLy, self.eyeLwidthCurrent, self.eyeLheightCurrent, self.eyeLborderRadiusCurrent, self.fgcolor)  # left eye
        
        if not self._cyclops:
            self.gfx.fill_rrect(self.eyeRx, self.eyeRy, self.eyeRwidthCurrent, self.eyeRheightCurrent, self.eyeRborderRadiusCurrent, self.fgcolor)  # right eye
        
        # Prepare mood type transitions
        if self.tired:
            self.eyelidsTiredHeightNext = self.eyeLheightCurrent//2
            self.eyelidsAngryHeightNext = 0
        else:
            self.eyelidsTiredHeightNext = 0
        if self.angry:
            self.eyelidsAngryHeightNext = self.eyeLheightCurrent//2
            self.eyelidsTiredHeightNext = 0
        else:
            self.eyelidsAngryHeightNext = 0
        if self.happy:
            self.eyelidsHappyBottomOffsetNext = self.eyeLheightCurrent//2
        else:
            self.eyelidsHappyBottomOffsetNext = 0
        
        # Draw tired top eyelids
        self.eyelidsTiredHeight = (self.eyelidsTiredHeight + self.eyelidsTiredHeightNext)//2
        if not self._cyclops:
            self.gfx.fill_triangle(self.eyeLx, self.eyeLy-1, self.eyeLx+self.eyeLwidthCurrent, self.eyeLy-1, self.eyeLx, self.eyeLy+self.eyelidsTiredHeight-1, self.bgcolor)  # left eye
            self.gfx.fill_triangle(self.eyeRx, self.eyeRy-1, self.eyeRx+self.eyeRwidthCurrent, self.eyeRy-1, self.eyeRx+self.eyeRwidthCurrent, self.eyeRy+self.eyelidsTiredHeight-1, self.bgcolor)  # right eye
        else:
            # Cyclops tired eyelids
            self.gfx.fill_triangle(self.eyeLx, self.eyeLy-1, self.eyeLx+(self.eyeLwidthCurrent//2), self.eyeLy-1, self.eyeLx, self.eyeLy+self.eyelidsTiredHeight-1, self.bgcolor)  # left eyelid half
            self.gfx.fill_triangle(self.eyeLx+(self.eyeLwidthCurrent//2), self.eyeLy-1, self.eyeLx+self.eyeLwidthCurrent, self.eyeLy-1, self.eyeLx+self.eyeLwidthCurrent, self.eyeLy+self.eyelidsTiredHeight-1, self.bgcolor)  # right eyelid half
        
        # Draw angry top eyelids
        self.eyelidsAngryHeight = (self.eyelidsAngryHeight + self.eyelidsAngryHeightNext)//2
        if not self._cyclops:
            self.gfx.fill_triangle(self.eyeLx, self.eyeLy-1, self.eyeLx+self.eyeLwidthCurrent, self.eyeLy-1, self.eyeLx+self.eyeLwidthCurrent, self.eyeLy+self.eyelidsAngryHeight-1, self.bgcolor)  # left eye
            self.gfx.fill_triangle(self.eyeRx, self.eyeRy-1, self.eyeRx+self.eyeRwidthCurrent, self.eyeRy-1, self.eyeRx, self.eyeRy+self.eyelidsAngryHeight-1, self.bgcolor)  # right eye
        else:
            # Cyclops angry eyelids
            self.gfx.fill_triangle(self.eyeLx, self.eyeLy-1, self.eyeLx+(self.eyeLwidthCurrent//2), self.eyeLy-1, self.eyeLx+(self.eyeLwidthCurrent//2), self.eyeLy+self.eyelidsAngryHeight-1, self.bgcolor)  # left eyelid half
            self.gfx.fill_triangle(self.eyeLx+(self.eyeLwidthCurrent//2), self.eyeLy-1, self.eyeLx+self.eyeLwidthCurrent, self.eyeLy-1, self.eyeLx+(self.eyeLwidthCurrent//2), self.eyeLy+self.eyelidsAngryHeight-1, self.bgcolor)  # right eyelid half
        
        # Draw happy bottom eyelids
        self.eyelidsHappyBottomOffset = (self.eyelidsHappyBottomOffset + self.eyelidsHappyBottomOffsetNext)//2
        self.gfx.fill_rrect(self.eyeLx-1, (self.eyeLy+self.eyeLheightCurrent)-self.eyelidsHappyBottomOffset+1, self.eyeLwidthCurrent+2, self.eyeLheightDefault, self.eyeLborderRadiusCurrent, self.bgcolor)  # left eye
        if not self._cyclops:
            self.gfx.fill_rrect(self.eyeRx-1, (self.eyeRy+self.eyeRheightCurrent)-self.eyelidsHappyBottomOffset+1, self.eyeRwidthCurrent+2, self.eyeRheightDefault, self.eyeRborderRadiusCurrent, self.bgcolor)  # right eye
        
        self.on_show(self)  # show drawings on display

def main():
    """
    Main entry point for the RoboEyes Desktop application.
    
    This function handles command-line argument parsing, configuration loading,
    and starts the RoboEyes application.
    """
    try:
        # Create configuration manager and parse command-line arguments
        config_manager = ConfigManager()
        config = config_manager.parse_command_line()
        
        # Create and run the RoboEyes application
        roboeyes = DesktopRoboEyes(config=config)
        
        # Apply configuration-specific settings
        if config.auto_blinker:
            roboeyes.set_auto_blinker(True, config.blink_interval, config.blink_variation)
        
        if config.idle_mode:
            roboeyes.set_idle_mode(True, config.idle_interval, config.idle_variation)
        
        # Start the application
        print(f"Starting RoboEyes Desktop...")
        print(f"Window size: {config.window_width}x{config.window_height}")
        print(f"Display size: {config.display_width}x{config.display_height}")
        print(f"Frame rate: {config.frame_rate} FPS")
        if config.debug:
            print(f"Configuration: {config}")
        
        roboeyes.run()
        
    except KeyboardInterrupt:
        print("\nShutting down RoboEyes Desktop...")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()