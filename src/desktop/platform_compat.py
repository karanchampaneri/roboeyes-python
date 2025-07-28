"""
Cross-platform compatibility utilities for RoboEyes Desktop.

This module provides platform detection, path handling, and platform-specific
configurations to ensure consistent behavior across Windows, macOS, and Linux.
"""

import os
import sys
import platform
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from enum import Enum

from .logging import get_logger


class Platform(Enum):
    """Supported platforms."""
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"
    UNKNOWN = "unknown"


class PlatformCompat:
    """Cross-platform compatibility utilities."""
    
    def __init__(self):
        """Initialize platform compatibility utilities."""
        self.logger = get_logger()
        self._platform = self._detect_platform()
        self._platform_info = self._get_platform_info()
        
        self.logger.debug(f"Detected platform: {self._platform.value}")
        self.logger.debug(f"Platform info: {self._platform_info}")
    
    def _detect_platform(self) -> Platform:
        """
        Detect the current platform.
        
        Returns:
            Platform enum value
        """
        system = platform.system().lower()
        
        if system == "windows":
            return Platform.WINDOWS
        elif system == "darwin":
            return Platform.MACOS
        elif system == "linux":
            return Platform.LINUX
        else:
            self.logger.warning(f"Unknown platform: {system}")
            return Platform.UNKNOWN
    
    def _get_platform_info(self) -> Dict[str, Any]:
        """
        Get detailed platform information.
        
        Returns:
            Dictionary with platform details
        """
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
        }
    
    @property
    def platform(self) -> Platform:
        """Get the current platform."""
        return self._platform
    
    @property
    def platform_info(self) -> Dict[str, Any]:
        """Get platform information."""
        return self._platform_info.copy()
    
    def is_windows(self) -> bool:
        """Check if running on Windows."""
        return self._platform == Platform.WINDOWS
    
    def is_macos(self) -> bool:
        """Check if running on macOS."""
        return self._platform == Platform.MACOS
    
    def is_linux(self) -> bool:
        """Check if running on Linux."""
        return self._platform == Platform.LINUX
    
    def get_config_dir(self) -> Path:
        """
        Get the platform-appropriate configuration directory.
        
        Returns:
            Path to configuration directory
        """
        if self.is_windows():
            # Use APPDATA on Windows
            appdata = os.environ.get("APPDATA")
            if appdata:
                return Path(appdata) / "RoboEyes"
            else:
                return Path.home() / "AppData" / "Roaming" / "RoboEyes"
        elif self.is_macos():
            # Use Application Support on macOS
            return Path.home() / "Library" / "Application Support" / "RoboEyes"
        else:
            # Use XDG config directory on Linux and others
            xdg_config = os.environ.get("XDG_CONFIG_HOME")
            if xdg_config:
                return Path(xdg_config) / "roboeyes"
            else:
                return Path.home() / ".config" / "roboeyes"
    
    def get_data_dir(self) -> Path:
        """
        Get the platform-appropriate data directory.
        
        Returns:
            Path to data directory
        """
        if self.is_windows():
            # Use LOCALAPPDATA on Windows
            localappdata = os.environ.get("LOCALAPPDATA")
            if localappdata:
                return Path(localappdata) / "RoboEyes"
            else:
                return Path.home() / "AppData" / "Local" / "RoboEyes"
        elif self.is_macos():
            # Use Application Support on macOS
            return Path.home() / "Library" / "Application Support" / "RoboEyes"
        else:
            # Use XDG data directory on Linux and others
            xdg_data = os.environ.get("XDG_DATA_HOME")
            if xdg_data:
                return Path(xdg_data) / "roboeyes"
            else:
                return Path.home() / ".local" / "share" / "roboeyes"
    
    def get_cache_dir(self) -> Path:
        """
        Get the platform-appropriate cache directory.
        
        Returns:
            Path to cache directory
        """
        if self.is_windows():
            # Use TEMP on Windows
            temp_dir = os.environ.get("TEMP", os.environ.get("TMP"))
            if temp_dir:
                return Path(temp_dir) / "RoboEyes"
            else:
                return Path.home() / "AppData" / "Local" / "Temp" / "RoboEyes"
        elif self.is_macos():
            # Use Caches on macOS
            return Path.home() / "Library" / "Caches" / "RoboEyes"
        else:
            # Use XDG cache directory on Linux and others
            xdg_cache = os.environ.get("XDG_CACHE_HOME")
            if xdg_cache:
                return Path(xdg_cache) / "roboeyes"
            else:
                return Path.home() / ".cache" / "roboeyes"
    
    def get_log_dir(self) -> Path:
        """
        Get the platform-appropriate log directory.
        
        Returns:
            Path to log directory
        """
        if self.is_windows():
            # Use LOCALAPPDATA/Logs on Windows
            localappdata = os.environ.get("LOCALAPPDATA")
            if localappdata:
                return Path(localappdata) / "RoboEyes" / "Logs"
            else:
                return Path.home() / "AppData" / "Local" / "RoboEyes" / "Logs"
        elif self.is_macos():
            # Use Logs on macOS
            return Path.home() / "Library" / "Logs" / "RoboEyes"
        else:
            # Use XDG data directory for logs on Linux
            xdg_data = os.environ.get("XDG_DATA_HOME")
            if xdg_data:
                return Path(xdg_data) / "roboeyes" / "logs"
            else:
                return Path.home() / ".local" / "share" / "roboeyes" / "logs"
    
    def ensure_directories(self) -> None:
        """Create all necessary directories if they don't exist."""
        directories = [
            self.get_config_dir(),
            self.get_data_dir(),
            self.get_cache_dir(),
            self.get_log_dir(),
        ]
        
        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                self.logger.debug(f"Ensured directory exists: {directory}")
            except OSError as e:
                self.logger.error(f"Failed to create directory {directory}: {e}")
    
    def get_font_paths(self) -> list[Path]:
        """
        Get platform-specific font search paths.
        
        Returns:
            List of paths to search for fonts
        """
        font_paths = []
        
        if self.is_windows():
            # Windows font directories
            windows_dir = os.environ.get("WINDIR", "C:\\Windows")
            font_paths.extend([
                Path(windows_dir) / "Fonts",
                Path.home() / "AppData" / "Local" / "Microsoft" / "Windows" / "Fonts",
            ])
        elif self.is_macos():
            # macOS font directories
            font_paths.extend([
                Path("/System/Library/Fonts"),
                Path("/Library/Fonts"),
                Path.home() / "Library" / "Fonts",
            ])
        else:
            # Linux font directories
            font_paths.extend([
                Path("/usr/share/fonts"),
                Path("/usr/local/share/fonts"),
                Path.home() / ".fonts",
                Path.home() / ".local" / "share" / "fonts",
            ])
        
        # Filter to only existing directories
        existing_paths = [path for path in font_paths if path.exists()]
        self.logger.debug(f"Font search paths: {existing_paths}")
        
        return existing_paths
    
    def get_default_font(self) -> Optional[str]:
        """
        Get the default system font for the platform.
        
        Returns:
            Font name or None if not found
        """
        if self.is_windows():
            return "Arial"
        elif self.is_macos():
            return "Helvetica"
        else:
            # Try common Linux fonts
            common_fonts = ["DejaVu Sans", "Liberation Sans", "Ubuntu", "Arial"]
            # For now, return the first one - in a real implementation,
            # we'd check which fonts are actually available
            return common_fonts[0]
    
    def get_display_scaling(self) -> float:
        """
        Get the system display scaling factor.
        
        Returns:
            Display scaling factor (1.0 = 100%)
        """
        try:
            if self.is_windows():
                # Try to get Windows DPI scaling
                import ctypes
                try:
                    # Get DPI awareness
                    ctypes.windll.shcore.SetProcessDpiAwareness(1)
                    # Get DPI for the primary monitor
                    hdc = ctypes.windll.user32.GetDC(0)
                    dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)  # LOGPIXELSX
                    ctypes.windll.user32.ReleaseDC(0, hdc)
                    return dpi / 96.0  # 96 DPI is 100% scaling
                except Exception:
                    return 1.0
            elif self.is_macos():
                # macOS handles scaling automatically through Pygame
                return 1.0
            else:
                # Linux - try to detect from environment variables
                scale = os.environ.get("GDK_SCALE", "1.0")
                try:
                    return float(scale)
                except ValueError:
                    return 1.0
        except Exception as e:
            self.logger.warning(f"Failed to detect display scaling: {e}")
            return 1.0
    
    def get_window_manager_info(self) -> Dict[str, Any]:
        """
        Get information about the window manager (Linux only).
        
        Returns:
            Dictionary with window manager information
        """
        if not self.is_linux():
            return {}
        
        info = {}
        
        # Try to detect desktop environment
        desktop_env = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
        if desktop_env:
            info["desktop_environment"] = desktop_env
        
        # Try to detect window manager
        wm_name = os.environ.get("WINDOW_MANAGER", "").lower()
        if wm_name:
            info["window_manager"] = wm_name
        
        # Check for Wayland vs X11
        if os.environ.get("WAYLAND_DISPLAY"):
            info["display_server"] = "wayland"
        elif os.environ.get("DISPLAY"):
            info["display_server"] = "x11"
        
        return info
    
    def get_pygame_driver_hints(self) -> Dict[str, str]:
        """
        Get platform-specific Pygame driver hints.
        
        Returns:
            Dictionary of SDL environment variables to set
        """
        hints = {}
        
        if self.is_windows():
            # Use DirectX on Windows for better performance
            hints["SDL_VIDEODRIVER"] = "directx"
        elif self.is_macos():
            # Use Cocoa on macOS
            hints["SDL_VIDEODRIVER"] = "cocoa"
        else:
            # Linux - try to use the best available driver
            wm_info = self.get_window_manager_info()
            if wm_info.get("display_server") == "wayland":
                hints["SDL_VIDEODRIVER"] = "wayland"
            else:
                hints["SDL_VIDEODRIVER"] = "x11"
        
        return hints
    
    def apply_pygame_hints(self) -> None:
        """Apply platform-specific Pygame/SDL hints."""
        hints = self.get_pygame_driver_hints()
        
        for key, value in hints.items():
            os.environ[key] = value
            self.logger.debug(f"Set {key}={value}")
    
    def get_performance_settings(self) -> Dict[str, Any]:
        """
        Get platform-specific performance settings.
        
        Returns:
            Dictionary with recommended performance settings
        """
        settings = {
            "vsync": True,
            "hardware_acceleration": True,
            "double_buffering": True,
        }
        
        if self.is_windows():
            # Windows-specific optimizations
            settings.update({
                "preferred_fps": 60,
                "use_dirty_rects": True,
            })
        elif self.is_macos():
            # macOS-specific optimizations
            settings.update({
                "preferred_fps": 60,
                "use_dirty_rects": False,  # macOS handles this well
            })
        else:
            # Linux-specific optimizations
            settings.update({
                "preferred_fps": 60,
                "use_dirty_rects": True,
            })
        
        return settings


# Global instance
_platform_compat = None


def get_platform_compat() -> PlatformCompat:
    """
    Get the global platform compatibility instance.
    
    Returns:
        PlatformCompat instance
    """
    global _platform_compat
    if _platform_compat is None:
        _platform_compat = PlatformCompat()
    return _platform_compat


def get_platform() -> Platform:
    """
    Get the current platform.
    
    Returns:
        Platform enum value
    """
    return get_platform_compat().platform


def is_windows() -> bool:
    """Check if running on Windows."""
    return get_platform_compat().is_windows()


def is_macos() -> bool:
    """Check if running on macOS."""
    return get_platform_compat().is_macos()


def is_linux() -> bool:
    """Check if running on Linux."""
    return get_platform_compat().is_linux()