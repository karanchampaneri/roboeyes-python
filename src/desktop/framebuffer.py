"""
FrameBuffer compatibility layer for desktop RoboEyes implementation.

This module provides a compatibility wrapper that mimics MicroPython's FrameBuffer API
using Pygame Surface as the underlying graphics backend.
"""

import pygame
from typing import Optional, Tuple

from .exceptions import GraphicsError
from .logging import get_logger
from .performance import OptimizedFrameBuffer


class FrameBufferCompat:
    """
    Compatibility wrapper that mimics MicroPython FrameBuffer API using Pygame Surface.
    
    This class provides the same interface as MicroPython's FrameBuffer but uses
    Pygame Surface for rendering operations, enabling desktop compatibility.
    """
    
    def __init__(self, pygame_surface: pygame.Surface, use_optimization: bool = True):
        """
        Initialize the FrameBuffer compatibility wrapper.
        
        Args:
            pygame_surface: The Pygame Surface to wrap
            use_optimization: Whether to use performance optimizations
        """
        self.surface = pygame_surface
        self.width = pygame_surface.get_width()
        self.height = pygame_surface.get_height()
        
        # Use optimized framebuffer if requested
        if use_optimization:
            self.optimized_fb = OptimizedFrameBuffer(pygame_surface)
        else:
            self.optimized_fb = None
    
    def fill(self, color: int) -> None:
        """
        Fill the entire framebuffer with the specified color.
        
        Args:
            color: Color value (0 for black/background, 1 for white/foreground)
            
        Raises:
            GraphicsError: If fill operation fails
        """
        logger = get_logger()
        
        try:
            if self.optimized_fb:
                self.optimized_fb.fill(color)
            else:
                # Convert MicroPython color values (0/1) to RGB
                rgb_color = (255, 255, 255) if color else (0, 0, 0)
                self.surface.fill(rgb_color)
            
        except pygame.error as e:
            error_msg = f"Pygame error filling framebuffer: {e}"
            logger.error(error_msg)
            raise GraphicsError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error filling framebuffer: {e}"
            logger.exception(error_msg)
            raise GraphicsError(error_msg)
    
    def pixel(self, x: int, y: int, color: Optional[int] = None) -> Optional[int]:
        """
        Set or get a pixel value at the specified coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate  
            color: Color value to set (0 or 1). If None, returns current pixel color.
            
        Returns:
            If color is None, returns the current pixel color (0 or 1).
            Otherwise returns None.
            
        Raises:
            GraphicsError: If pixel operation fails
        """
        logger = get_logger()
        
        try:
            if self.optimized_fb:
                return self.optimized_fb.pixel(x, y, color)
            else:
                if color is None:
                    # Get pixel color
                    if 0 <= x < self.width and 0 <= y < self.height:
                        rgb = self.surface.get_at((x, y))[:3]  # Get RGB, ignore alpha
                        # Convert RGB back to 0/1 (consider white-ish as 1, dark as 0)
                        return 1 if sum(rgb) > 384 else 0  # 384 = 128 * 3 (mid-gray threshold)
                    else:
                        logger.warning(f"Pixel get coordinates out of bounds: ({x}, {y})")
                    return 0
                else:
                    # Set pixel color
                    if 0 <= x < self.width and 0 <= y < self.height:
                        rgb_color = (255, 255, 255) if color else (0, 0, 0)
                        self.surface.set_at((x, y), rgb_color)
                    else:
                        logger.warning(f"Pixel set coordinates out of bounds: ({x}, {y})")
                    
        except pygame.error as e:
            error_msg = f"Pygame error accessing pixel at ({x}, {y}): {e}"
            logger.error(error_msg)
            raise GraphicsError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error accessing pixel at ({x}, {y}): {e}"
            logger.exception(error_msg)
            raise GraphicsError(error_msg)
    
    def show(self) -> None:
        """
        Trigger display update. 
        
        Note: This method exists for API compatibility but doesn't perform
        any action since the actual display update is handled by the 
        on_show callback in the RoboEyes class.
        """
        pass
    
    def get_dirty_rects(self):
        """Get dirty rectangles for optimized updates."""
        if self.optimized_fb:
            return self.optimized_fb.get_dirty_rects()
        return []
    
    def get_update_efficiency(self):
        """Get the current update efficiency percentage."""
        if self.optimized_fb:
            return self.optimized_fb.get_update_efficiency()
        return 100.0  # Full screen update
    
    def should_use_dirty_rects(self):
        """Determine if dirty rectangle updates should be used."""
        if self.optimized_fb:
            return self.optimized_fb.should_use_dirty_rects()
        return False
    
    def mark_dirty_rect(self, x: int, y: int, width: int, height: int):
        """Manually mark a rectangular region as dirty."""
        if self.optimized_fb:
            self.optimized_fb.mark_dirty_rect(x, y, width, height)
    
    def mark_dirty_circle(self, center_x: int, center_y: int, radius: int):
        """Mark a circular region as dirty."""
        if self.optimized_fb:
            self.optimized_fb.mark_dirty_circle(center_x, center_y, radius)