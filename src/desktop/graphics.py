"""
Graphics utilities for desktop RoboEyes implementation.

This module provides Pygame-based implementations of graphics operations
that replace the FBUtil functionality from the original MicroPython version.
"""

import pygame
import math
from typing import Tuple

from .exceptions import GraphicsError
from .logging import get_logger


class PygameGraphicsUtil:
    """
    Pygame implementation of FBUtil graphics operations.
    
    This class provides graphics utility functions that replace the FBUtil
    functionality from the original MicroPython RoboEyes library, using
    Pygame drawing functions for desktop compatibility.
    """
    
    def __init__(self, pygame_surface: pygame.Surface, dirty_tracker=None):
        """
        Initialize the graphics utility with a Pygame surface.
        
        Args:
            pygame_surface: The Pygame Surface to draw on
            dirty_tracker: Optional DirtyRectTracker for performance optimization
        """
        self.surface = pygame_surface
        self.dirty_tracker = dirty_tracker
    
    def fill_rrect(self, x: int, y: int, w: int, h: int, radius: int, color: int) -> None:
        """
        Draw a filled rounded rectangle.
        
        Args:
            x: X coordinate of the top-left corner
            y: Y coordinate of the top-left corner
            w: Width of the rectangle
            h: Height of the rectangle
            radius: Corner radius for rounding
            color: Color value (0 for black/background, 1 for white/foreground)
            
        Raises:
            GraphicsError: If drawing operation fails
        """
        logger = get_logger()
        
        try:
            # Validate parameters
            if w <= 0 or h <= 0:
                logger.warning(f"Invalid rectangle dimensions: w={w}, h={h}")
                return
            
            if radius < 0:
                logger.warning(f"Invalid radius: {radius}, using 0")
                radius = 0
            
            # Convert MicroPython color values (0/1) to RGB
            rgb_color = (255, 255, 255) if color else (0, 0, 0)
            
            # Clamp radius to prevent invalid shapes
            max_radius = min(w // 2, h // 2)
            radius = min(radius, max_radius)
            
            # Track dirty rectangle for performance optimization
            if self.dirty_tracker:
                self.dirty_tracker.add_dirty_rect(x, y, w, h)
            
            if radius <= 0:
                # Draw regular rectangle if no radius
                pygame.draw.rect(self.surface, rgb_color, (x, y, w, h))
                return
            
            # Draw the rounded rectangle using multiple shapes
            # Main rectangle (center area)
            pygame.draw.rect(self.surface, rgb_color, (x + radius, y, w - 2 * radius, h))
            pygame.draw.rect(self.surface, rgb_color, (x, y + radius, w, h - 2 * radius))
            
            # Draw corner circles
            pygame.draw.circle(self.surface, rgb_color, (x + radius, y + radius), radius)  # Top-left
            pygame.draw.circle(self.surface, rgb_color, (x + w - radius, y + radius), radius)  # Top-right
            pygame.draw.circle(self.surface, rgb_color, (x + radius, y + h - radius), radius)  # Bottom-left
            pygame.draw.circle(self.surface, rgb_color, (x + w - radius, y + h - radius), radius)  # Bottom-right
            
        except pygame.error as e:
            error_msg = f"Pygame error drawing rounded rectangle: {e}"
            logger.error(error_msg)
            raise GraphicsError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error drawing rounded rectangle: {e}"
            logger.exception(error_msg)
            raise GraphicsError(error_msg)
    
    def fill_triangle(self, x1: int, y1: int, x2: int, y2: int, x3: int, y3: int, color: int, suppress_warnings: bool = True) -> None:
        """
        Draw a filled triangle.
        
        Args:
            x1: X coordinate of first vertex
            y1: Y coordinate of first vertex
            x2: X coordinate of second vertex
            y2: Y coordinate of second vertex
            x3: X coordinate of third vertex
            y3: Y coordinate of third vertex
            color: Color value (0 for black/background, 1 for white/foreground)
            suppress_warnings: Whether to suppress warnings for degenerate triangles
            
        Raises:
            GraphicsError: If drawing operation fails
        """
        logger = get_logger()
        
        try:
            # Convert MicroPython color values (0/1) to RGB
            rgb_color = (255, 255, 255) if color else (0, 0, 0)
            
            # Define triangle vertices
            points = [(x1, y1), (x2, y2), (x3, y3)]
            
            # Validate that we have at least 3 distinct points
            if len(set(points)) < 3:
                if not suppress_warnings:
                    logger.warning(f"Triangle has duplicate vertices: {points}")
                return
            
            # Track dirty rectangle for triangle bounding box
            if self.dirty_tracker:
                min_x = min(x1, x2, x3)
                max_x = max(x1, x2, x3)
                min_y = min(y1, y2, y3)
                max_y = max(y1, y2, y3)
                self.dirty_tracker.add_dirty_rect(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)
            
            # Draw filled triangle
            pygame.draw.polygon(self.surface, rgb_color, points)
            
        except pygame.error as e:
            error_msg = f"Pygame error drawing triangle: {e}"
            logger.error(error_msg)
            raise GraphicsError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error drawing triangle: {e}"
            logger.exception(error_msg)
            raise GraphicsError(error_msg)