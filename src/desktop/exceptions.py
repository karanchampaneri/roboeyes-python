"""
Custom exception classes for RoboEyes Desktop application.

This module defines custom exception classes for better error handling
and categorization throughout the RoboEyes desktop application.
"""


class RoboEyesError(Exception):
    """Base exception class for RoboEyes Desktop errors."""
    pass


class PygameInitializationError(RoboEyesError):
    """Raised when Pygame initialization fails."""
    pass


class DisplayError(RoboEyesError):
    """Raised when display operations fail."""
    pass


class ConfigurationError(RoboEyesError):
    """Raised when configuration validation fails."""
    pass


class InputError(RoboEyesError):
    """Raised when input processing fails."""
    pass


class AnimationError(RoboEyesError):
    """Raised when animation system encounters errors."""
    pass


class GraphicsError(RoboEyesError):
    """Raised when graphics operations fail."""
    pass


class TimingError(RoboEyesError):
    """Raised when timing system encounters errors."""
    pass


class WindowError(RoboEyesError):
    """Raised when window management operations fail."""
    pass