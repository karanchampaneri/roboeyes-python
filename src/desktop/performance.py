"""
Performance monitoring and optimization utilities for desktop RoboEyes.

This module provides performance monitoring, dirty rectangle tracking,
and frame rate optimization features to ensure smooth animation.
"""

import pygame
import time
import psutil
import os
from typing import List, Tuple, Optional, Dict, Any
from collections import deque
from dataclasses import dataclass

from .logging import get_logger


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    fps: float = 0.0
    frame_time: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    memory_usage_mb: float = 0.0
    dirty_rects_count: int = 0
    total_pixels_updated: int = 0
    update_efficiency: float = 0.0  # Percentage of screen actually updated


class DirtyRectTracker:
    """
    Tracks dirty rectangles for efficient screen updates.
    
    This class manages regions of the screen that need to be redrawn,
    allowing for optimized rendering by only updating changed areas.
    """
    
    def __init__(self, screen_width: int, screen_height: int):
        """
        Initialize the dirty rectangle tracker.
        
        Args:
            screen_width: Width of the screen/surface
            screen_height: Height of the screen/surface
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.dirty_rects: List[pygame.Rect] = []
        self.total_screen_pixels = screen_width * screen_height
        self.logger = get_logger()
    
    def add_dirty_rect(self, x: int, y: int, width: int, height: int) -> None:
        """
        Add a dirty rectangle to the update list.
        
        Args:
            x: X coordinate of the rectangle
            y: Y coordinate of the rectangle
            width: Width of the rectangle
            height: Height of the rectangle
        """
        # Clamp rectangle to screen bounds
        x = max(0, min(x, self.screen_width))
        y = max(0, min(y, self.screen_height))
        width = max(0, min(width, self.screen_width - x))
        height = max(0, min(height, self.screen_height - y))
        
        if width > 0 and height > 0:
            rect = pygame.Rect(x, y, width, height)
            self.dirty_rects.append(rect)
    
    def add_dirty_circle(self, center_x: int, center_y: int, radius: int) -> None:
        """
        Add a circular dirty region as a bounding rectangle.
        
        Args:
            center_x: X coordinate of circle center
            center_y: Y coordinate of circle center
            radius: Radius of the circle
        """
        x = center_x - radius
        y = center_y - radius
        width = height = radius * 2
        self.add_dirty_rect(x, y, width, height)
    
    def merge_overlapping_rects(self) -> None:
        """
        Merge overlapping dirty rectangles to reduce the number of updates.
        
        This optimization reduces the overhead of multiple small updates
        by combining them into larger rectangular regions.
        """
        if len(self.dirty_rects) <= 1:
            return
        
        merged = []
        sorted_rects = sorted(self.dirty_rects, key=lambda r: (r.x, r.y))
        
        for rect in sorted_rects:
            merged_with_existing = False
            
            for i, existing in enumerate(merged):
                # Check if rectangles overlap or are adjacent
                if (rect.colliderect(existing) or 
                    self._are_adjacent(rect, existing)):
                    # Merge rectangles
                    merged[i] = rect.union(existing)
                    merged_with_existing = True
                    break
            
            if not merged_with_existing:
                merged.append(rect)
        
        self.dirty_rects = merged
    
    def _are_adjacent(self, rect1: pygame.Rect, rect2: pygame.Rect) -> bool:
        """
        Check if two rectangles are adjacent (touching edges).
        
        Args:
            rect1: First rectangle
            rect2: Second rectangle
            
        Returns:
            True if rectangles are adjacent, False otherwise
        """
        # Check horizontal adjacency
        if (rect1.y == rect2.y and rect1.height == rect2.height and
            (rect1.right == rect2.left or rect2.right == rect1.left)):
            return True
        
        # Check vertical adjacency
        if (rect1.x == rect2.x and rect1.width == rect2.width and
            (rect1.bottom == rect2.top or rect2.bottom == rect1.top)):
            return True
        
        return False
    
    def get_dirty_rects(self) -> List[pygame.Rect]:
        """
        Get the list of dirty rectangles and clear the internal list.
        
        Returns:
            List of dirty rectangles that need updating
        """
        self.merge_overlapping_rects()
        rects = self.dirty_rects.copy()
        self.dirty_rects.clear()
        return rects
    
    def get_update_efficiency(self) -> float:
        """
        Calculate the efficiency of the current update (percentage of screen updated).
        
        Returns:
            Percentage of screen pixels that will be updated (0.0 to 100.0)
        """
        if not self.dirty_rects:
            return 0.0
        
        total_dirty_pixels = sum(rect.width * rect.height for rect in self.dirty_rects)
        return (total_dirty_pixels / self.total_screen_pixels) * 100.0
    
    def should_use_dirty_rects(self, threshold: float = 50.0) -> bool:
        """
        Determine if dirty rectangle updates are more efficient than full screen update.
        
        Args:
            threshold: Percentage threshold above which full screen update is preferred
            
        Returns:
            True if dirty rectangles should be used, False for full screen update
        """
        efficiency = self.get_update_efficiency()
        return efficiency < threshold and len(self.dirty_rects) > 0
    
    def clear(self) -> None:
        """Clear all dirty rectangles."""
        self.dirty_rects.clear()


class PerformanceMonitor:
    """
    Monitors and tracks performance metrics for the RoboEyes application.
    
    This class provides real-time performance monitoring including FPS,
    memory usage, CPU usage, and rendering efficiency metrics.
    """
    
    def __init__(self, history_size: int = 60):
        """
        Initialize the performance monitor.
        
        Args:
            history_size: Number of frames to keep in history for averaging
        """
        self.history_size = history_size
        self.frame_times = deque(maxlen=history_size)
        self.fps_history = deque(maxlen=history_size)
        self.cpu_history = deque(maxlen=history_size)
        self.memory_history = deque(maxlen=history_size)
        
        self.last_frame_time = time.time()
        self.frame_count = 0
        self.start_time = time.time()
        
        # Get process for memory monitoring
        self.process = psutil.Process(os.getpid())
        
        self.logger = get_logger()
        
        # Performance display settings
        self.show_performance = False
        self.performance_font = None
        self.performance_surface = None
    
    def update(self, dirty_rects_count: int = 0, total_pixels_updated: int = 0) -> PerformanceMetrics:
        """
        Update performance metrics for the current frame.
        
        Args:
            dirty_rects_count: Number of dirty rectangles updated this frame
            total_pixels_updated: Total number of pixels updated this frame
            
        Returns:
            Current performance metrics
        """
        current_time = time.time()
        frame_time = current_time - self.last_frame_time
        self.last_frame_time = current_time
        
        # Calculate FPS
        fps = 1.0 / frame_time if frame_time > 0 else 0.0
        
        # Update histories
        self.frame_times.append(frame_time)
        self.fps_history.append(fps)
        
        # Get system metrics (less frequently to reduce overhead)
        if self.frame_count % 10 == 0:  # Update every 10 frames
            try:
                cpu_usage = self.process.cpu_percent()
                memory_info = self.process.memory_info()
                memory_usage = memory_info.rss  # Resident Set Size in bytes
                memory_usage_mb = memory_usage / (1024 * 1024)  # Convert to MB
                
                self.cpu_history.append(cpu_usage)
                self.memory_history.append(memory_usage_mb)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Handle process monitoring errors gracefully
                cpu_usage = 0.0
                memory_usage_mb = 0.0
        else:
            # Use last known values
            cpu_usage = self.cpu_history[-1] if self.cpu_history else 0.0
            memory_usage_mb = self.memory_history[-1] if self.memory_history else 0.0
        
        self.frame_count += 1
        
        # Calculate update efficiency
        screen_pixels = 128 * 64  # Default RoboEyes screen size
        update_efficiency = (total_pixels_updated / screen_pixels * 100.0) if screen_pixels > 0 else 0.0
        
        return PerformanceMetrics(
            fps=fps,
            frame_time=frame_time * 1000,  # Convert to milliseconds
            cpu_usage=cpu_usage,
            memory_usage=memory_usage_mb * 1024 * 1024,  # Back to bytes for compatibility
            memory_usage_mb=memory_usage_mb,
            dirty_rects_count=dirty_rects_count,
            total_pixels_updated=total_pixels_updated,
            update_efficiency=update_efficiency
        )
    
    def get_average_fps(self) -> float:
        """
        Get the average FPS over the history window.
        
        Returns:
            Average FPS
        """
        return sum(self.fps_history) / len(self.fps_history) if self.fps_history else 0.0
    
    def get_average_frame_time(self) -> float:
        """
        Get the average frame time in milliseconds over the history window.
        
        Returns:
            Average frame time in milliseconds
        """
        if not self.frame_times:
            return 0.0
        avg_time = sum(self.frame_times) / len(self.frame_times)
        return avg_time * 1000  # Convert to milliseconds
    
    def get_average_cpu_usage(self) -> float:
        """
        Get the average CPU usage over the history window.
        
        Returns:
            Average CPU usage percentage
        """
        return sum(self.cpu_history) / len(self.cpu_history) if self.cpu_history else 0.0
    
    def get_average_memory_usage(self) -> float:
        """
        Get the average memory usage in MB over the history window.
        
        Returns:
            Average memory usage in MB
        """
        return sum(self.memory_history) / len(self.memory_history) if self.memory_history else 0.0
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get a comprehensive performance summary.
        
        Returns:
            Dictionary containing performance metrics
        """
        return {
            'avg_fps': self.get_average_fps(),
            'avg_frame_time_ms': self.get_average_frame_time(),
            'avg_cpu_usage': self.get_average_cpu_usage(),
            'avg_memory_mb': self.get_average_memory_usage(),
            'total_frames': self.frame_count,
            'uptime_seconds': time.time() - self.start_time,
            'history_size': len(self.fps_history)
        }
    
    def toggle_performance_display(self) -> None:
        """Toggle the performance display overlay."""
        self.show_performance = not self.show_performance
        
        if self.show_performance and self.performance_font is None:
            try:
                # Initialize font for performance display
                pygame.font.init()
                self.performance_font = pygame.font.Font(None, 24)
            except pygame.error:
                self.logger.warning("Could not initialize font for performance display")
                self.show_performance = False
    
    def render_performance_overlay(self, screen: pygame.Surface, metrics: PerformanceMetrics) -> None:
        """
        Render performance metrics overlay on the screen.
        
        Args:
            screen: Pygame surface to render on
            metrics: Current performance metrics
        """
        if not self.show_performance or self.performance_font is None:
            return
        
        try:
            # Performance text lines
            lines = [
                f"FPS: {metrics.fps:.1f} (avg: {self.get_average_fps():.1f})",
                f"Frame: {metrics.frame_time:.1f}ms",
                f"CPU: {metrics.cpu_usage:.1f}%",
                f"Memory: {metrics.memory_usage_mb:.1f}MB",
                f"Dirty Rects: {metrics.dirty_rects_count}",
                f"Update Efficiency: {metrics.update_efficiency:.1f}%"
            ]
            
            # Calculate overlay size
            line_height = 25
            overlay_height = len(lines) * line_height + 10
            overlay_width = 250
            
            # Create semi-transparent overlay
            overlay = pygame.Surface((overlay_width, overlay_height))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            
            # Render text lines
            for i, line in enumerate(lines):
                text_surface = self.performance_font.render(line, True, (255, 255, 255))
                overlay.blit(text_surface, (5, 5 + i * line_height))
            
            # Blit overlay to screen (top-right corner)
            screen.blit(overlay, (screen.get_width() - overlay_width - 10, 10))
            
        except pygame.error as e:
            self.logger.error(f"Error rendering performance overlay: {e}")
    
    def log_performance_summary(self, interval_seconds: int = 30) -> None:
        """
        Log performance summary at regular intervals.
        
        Args:
            interval_seconds: Interval between log entries
        """
        if self.frame_count % (interval_seconds * 60) == 0:  # Assuming ~60 FPS
            summary = self.get_performance_summary()
            self.logger.info(
                f"Performance Summary - "
                f"FPS: {summary['avg_fps']:.1f}, "
                f"Frame Time: {summary['avg_frame_time_ms']:.1f}ms, "
                f"CPU: {summary['avg_cpu_usage']:.1f}%, "
                f"Memory: {summary['avg_memory_mb']:.1f}MB"
            )


class OptimizedFrameBuffer:
    """
    Optimized framebuffer with dirty rectangle tracking.
    
    This class extends the basic framebuffer functionality with
    performance optimizations including dirty rectangle tracking
    and efficient update mechanisms.
    """
    
    def __init__(self, pygame_surface: pygame.Surface):
        """
        Initialize the optimized framebuffer.
        
        Args:
            pygame_surface: The Pygame Surface to wrap
        """
        self.surface = pygame_surface
        self.width = pygame_surface.get_width()
        self.height = pygame_surface.get_height()
        self.dirty_tracker = DirtyRectTracker(self.width, self.height)
        self.logger = get_logger()
        
        # Track last clear state to optimize full clears
        self.last_clear_color = None
        self.needs_full_clear = True
    
    def fill(self, color: int) -> None:
        """
        Fill the framebuffer with optimized dirty rectangle tracking.
        
        Args:
            color: Color value (0 for black/background, 1 for white/foreground)
        """
        # Convert MicroPython color values (0/1) to RGB
        rgb_color = (255, 255, 255) if color else (0, 0, 0)
        
        # Always fill to ensure proper frame clearing
        # The optimization was causing frame ghosting issues
        self.surface.fill(rgb_color)
        self.last_clear_color = rgb_color
        self.needs_full_clear = False
        
        # Mark entire screen as dirty for full clear
        self.dirty_tracker.add_dirty_rect(0, 0, self.width, self.height)
    
    def pixel(self, x: int, y: int, color: Optional[int] = None) -> Optional[int]:
        """
        Set or get a pixel with dirty rectangle tracking.
        
        Args:
            x: X coordinate
            y: Y coordinate  
            color: Color value to set (0 or 1). If None, returns current pixel color.
            
        Returns:
            If color is None, returns the current pixel color (0 or 1).
            Otherwise returns None.
        """
        if color is None:
            # Get pixel color
            if 0 <= x < self.width and 0 <= y < self.height:
                rgb = self.surface.get_at((x, y))[:3]
                return 1 if sum(rgb) > 384 else 0
            return 0
        else:
            # Set pixel color with dirty tracking
            if 0 <= x < self.width and 0 <= y < self.height:
                rgb_color = (255, 255, 255) if color else (0, 0, 0)
                self.surface.set_at((x, y), rgb_color)
                self.dirty_tracker.add_dirty_rect(x, y, 1, 1)
                self.needs_full_clear = True  # Pixel changes invalidate clear optimization
    
    def get_dirty_rects(self) -> List[pygame.Rect]:
        """Get dirty rectangles for optimized updates."""
        return self.dirty_tracker.get_dirty_rects()
    
    def get_update_efficiency(self) -> float:
        """Get the current update efficiency percentage."""
        return self.dirty_tracker.get_update_efficiency()
    
    def should_use_dirty_rects(self) -> bool:
        """Determine if dirty rectangle updates should be used."""
        return self.dirty_tracker.should_use_dirty_rects()
    
    def mark_dirty_rect(self, x: int, y: int, width: int, height: int) -> None:
        """
        Manually mark a rectangular region as dirty.
        
        Args:
            x: X coordinate of the rectangle
            y: Y coordinate of the rectangle
            width: Width of the rectangle
            height: Height of the rectangle
        """
        self.dirty_tracker.add_dirty_rect(x, y, width, height)
        self.needs_full_clear = True
    
    def mark_dirty_circle(self, center_x: int, center_y: int, radius: int) -> None:
        """
        Mark a circular region as dirty.
        
        Args:
            center_x: X coordinate of circle center
            center_y: Y coordinate of circle center
            radius: Radius of the circle
        """
        self.dirty_tracker.add_dirty_circle(center_x, center_y, radius)
        self.needs_full_clear = True