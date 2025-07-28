"""
Timing utilities for desktop RoboEyes implementation.

This module provides timing functions that replace MicroPython's time.ticks_ms(),
time.ticks_diff(), and time.ticks_add() functions using standard Python time functions.
"""

import time
from typing import Union


def ticks_ms() -> int:
    """
    Get current time in milliseconds.
    
    Replacement for MicroPython's time.ticks_ms().
    
    Returns:
        Current time in milliseconds as an integer
    """
    return int(time.time() * 1000)


def ticks_diff(ticks1: int, ticks2: int) -> int:
    """
    Calculate the difference between two tick values.
    
    Replacement for MicroPython's time.ticks_diff().
    
    Args:
        ticks1: First tick value (typically current time)
        ticks2: Second tick value (typically start time)
        
    Returns:
        Difference in milliseconds (ticks1 - ticks2)
    """
    return ticks1 - ticks2


def ticks_add(ticks: int, delta: int) -> int:
    """
    Add a delta to a tick value.
    
    Replacement for MicroPython's time.ticks_add().
    
    Args:
        ticks: Base tick value
        delta: Delta to add in milliseconds
        
    Returns:
        New tick value (ticks + delta)
    """
    return ticks + delta


class FrameRateLimiter:
    """
    Frame rate limiting utility for smooth animation.
    
    This class helps maintain consistent frame rates by tracking timing
    and providing methods to limit update frequency.
    """
    
    def __init__(self, target_fps: int = 60):
        """
        Initialize the frame rate limiter.
        
        Args:
            target_fps: Target frames per second
        """
        self.target_fps = target_fps
        self.frame_interval = 1000 // target_fps  # milliseconds per frame
        self.last_frame_time = 0  # Initialize to 0 so first call returns True
    
    def set_fps(self, fps: int) -> None:
        """
        Set the target frame rate.
        
        Args:
            fps: Target frames per second
        """
        self.target_fps = fps
        self.frame_interval = 1000 // fps
    
    def should_update(self) -> bool:
        """
        Check if enough time has passed for the next frame.
        
        Returns:
            True if it's time for the next frame, False otherwise
        """
        current_time = ticks_ms()
        if ticks_diff(current_time, self.last_frame_time) >= self.frame_interval:
            self.last_frame_time = current_time
            return True
        return False
    
    def wait_for_next_frame(self) -> None:
        """
        Sleep until it's time for the next frame.
        
        This method can be used to actively wait for the next frame
        instead of just checking with should_update().
        """
        current_time = ticks_ms()
        elapsed = ticks_diff(current_time, self.last_frame_time)
        
        if elapsed < self.frame_interval:
            sleep_time = (self.frame_interval - elapsed) / 1000.0
            time.sleep(sleep_time)
        
        self.last_frame_time = ticks_ms()
    
    def get_fps(self) -> int:
        """
        Get the current target FPS.
        
        Returns:
            Current target frames per second
        """
        return self.target_fps
    
    def get_frame_interval(self) -> int:
        """
        Get the current frame interval in milliseconds.
        
        Returns:
            Frame interval in milliseconds
        """
        return self.frame_interval