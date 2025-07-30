"""
Configuration management system for RoboEyes Desktop.

This module provides configuration loading, saving, validation, and command-line
argument parsing for the RoboEyes desktop application.
"""

import argparse
import json
import os
from dataclasses import dataclass, asdict, fields
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, Union

from .exceptions import ConfigurationError
from .logging import get_logger
from .platform_compat import get_platform_compat


@dataclass
class RoboEyesConfig:
    """Configuration settings for the desktop RoboEyes application."""
    # Window settings
    window_width: int = 800
    window_height: int = 600
    scale_factor: float = 1.0
    frame_rate: int = 60
    fullscreen: bool = False
    resizable: bool = True
    
    # Eye display settings
    eye_width: int = 36
    eye_height: int = 36
    display_width: int = 128
    display_height: int = 64
    
    # Color settings
    background_color: Tuple[int, int, int] = (0, 0, 0)
    foreground_color: Tuple[int, int, int] = (255, 255, 255)
    
    # Animation settings
    auto_blinker: bool = False
    blink_interval: float = 1.0
    blink_variation: int = 4
    idle_mode: bool = False
    idle_interval: float = 1.0
    idle_variation: int = 3
    
    # Application settings
    config_file: Optional[str] = None
    debug: bool = False
    suppress_graphics_warnings: bool = True


class ConfigManager:
    """Manages configuration loading, saving, and validation."""
    
    DEFAULT_CONFIG_FILENAME = "roboeyes_config.json"
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_file: Optional path to configuration file
        """
        self.config_file = config_file or self._get_default_config_path()
        self._config = RoboEyesConfig()
    
    def _get_default_config_path(self) -> str:
        """Get the default configuration file path."""
        # Use platform-appropriate config directory
        platform_compat = get_platform_compat()
        config_dir = platform_compat.get_config_dir()
        config_dir.mkdir(parents=True, exist_ok=True)
        return str(config_dir / self.DEFAULT_CONFIG_FILENAME)
    
    def load_config(self, config_file: Optional[str] = None) -> RoboEyesConfig:
        """
        Load configuration from file.
        
        Args:
            config_file: Optional path to configuration file
            
        Returns:
            RoboEyesConfig instance
            
        Raises:
            ConfigurationError: If configuration file is invalid
        """
        logger = get_logger()
        file_path = config_file or self.config_file
        
        if not os.path.exists(file_path):
            logger.info(f"Configuration file not found: {file_path}, using defaults")
            return RoboEyesConfig()
        
        try:
            logger.debug(f"Loading configuration from: {file_path}")
            with open(file_path, 'r') as f:
                config_data = json.load(f)
            
            # Validate and create config object
            validated_data = self._validate_config_data(config_data)
            self._config = RoboEyesConfig(**validated_data)
            
            logger.info(f"Configuration loaded successfully from: {file_path}")
            return self._config
            
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in configuration file {file_path}: {e}"
            logger.error(error_msg)
            raise ConfigurationError(error_msg)
        except IOError as e:
            error_msg = f"Failed to read configuration file {file_path}: {e}"
            logger.error(error_msg)
            raise ConfigurationError(error_msg)
        except TypeError as e:
            error_msg = f"Invalid configuration data structure in {file_path}: {e}"
            logger.error(error_msg)
            raise ConfigurationError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error loading configuration from {file_path}: {e}"
            logger.exception(error_msg)
            raise ConfigurationError(error_msg)
    
    def save_config(self, config: RoboEyesConfig, config_file: Optional[str] = None) -> None:
        """
        Save configuration to file.
        
        Args:
            config: RoboEyesConfig instance to save
            config_file: Optional path to configuration file
            
        Raises:
            ConfigurationError: If configuration cannot be saved
        """
        logger = get_logger()
        file_path = config_file or self.config_file
        
        try:
            logger.debug(f"Saving configuration to: {file_path}")
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Convert config to dictionary and save
            config_dict = asdict(config)
            
            with open(file_path, 'w') as f:
                json.dump(config_dict, f, indent=2)
            
            logger.info(f"Configuration saved successfully to: {file_path}")
                
        except (IOError, OSError) as e:
            error_msg = f"Failed to save configuration to {file_path}: {e}"
            logger.error(error_msg)
            raise ConfigurationError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error saving configuration to {file_path}: {e}"
            logger.exception(error_msg)
            raise ConfigurationError(error_msg)
    
    def _validate_config_data(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate configuration data and apply defaults for missing values.
        
        Args:
            config_data: Raw configuration data from file
            
        Returns:
            Validated configuration data
            
        Raises:
            ConfigurationError: If validation fails
        """
        validated_data = {}
        config_fields = {field.name: field for field in fields(RoboEyesConfig)}
        
        for field_name, field_info in config_fields.items():
            if field_name in config_data:
                value = config_data[field_name]
                
                # Type validation
                if not self._validate_field_type(value, field_info.type):
                    raise ConfigurationError(
                        f"Invalid type for field '{field_name}': expected {field_info.type}, got {type(value)}"
                    )
                
                # Range validation
                validated_value = self._validate_field_range(field_name, value)
                validated_data[field_name] = validated_value
            else:
                # Use default value if field is missing
                validated_data[field_name] = field_info.default
        
        return validated_data
    
    def _validate_field_type(self, value: Any, expected_type: type) -> bool:
        """
        Validate that a value matches the expected type.
        
        Args:
            value: Value to validate
            expected_type: Expected type
            
        Returns:
            True if type is valid, False otherwise
        """
        # Handle special cases for typing annotations
        if hasattr(expected_type, '__origin__'):
            if expected_type.__origin__ is Union:
                # Handle Optional types (Union[T, None])
                if value is None:
                    return type(None) in expected_type.__args__
                return any(isinstance(value, arg) for arg in expected_type.__args__ if arg is not type(None))
            elif expected_type.__origin__ is tuple:
                # Handle Tuple types
                return isinstance(value, (tuple, list))
        
        # Handle Optional types in Python 3.10+ style
        if str(expected_type).startswith('typing.Union') or str(expected_type).startswith('typing.Optional'):
            if value is None:
                return 'NoneType' in str(expected_type) or 'None' in str(expected_type)
            # Extract the non-None type from Optional[T]
            if hasattr(expected_type, '__args__'):
                non_none_types = [arg for arg in expected_type.__args__ if arg is not type(None)]
                if non_none_types:
                    return isinstance(value, non_none_types[0])
        
        return isinstance(value, expected_type)
    
    def _validate_field_range(self, field_name: str, value: Any) -> Any:
        """
        Validate field value ranges and apply constraints.
        
        Args:
            field_name: Name of the field
            value: Value to validate
            
        Returns:
            Validated (and possibly constrained) value
            
        Raises:
            ConfigurationError: If value is out of valid range
        """
        # Window dimensions
        if field_name in ('window_width', 'window_height'):
            if not (100 <= value <= 4000):
                raise ConfigurationError(f"{field_name} must be between 100 and 4000 pixels")
        
        # Display dimensions
        elif field_name in ('display_width', 'display_height'):
            if not (32 <= value <= 1024):
                raise ConfigurationError(f"{field_name} must be between 32 and 1024 pixels")
        
        # Eye dimensions
        elif field_name in ('eye_width', 'eye_height'):
            if not (8 <= value <= 128):
                raise ConfigurationError(f"{field_name} must be between 8 and 128 pixels")
        
        # Frame rate
        elif field_name == 'frame_rate':
            if not (1 <= value <= 120):
                raise ConfigurationError("frame_rate must be between 1 and 120 FPS")
        
        # Scale factor
        elif field_name == 'scale_factor':
            if not (0.1 <= value <= 10.0):
                raise ConfigurationError("scale_factor must be between 0.1 and 10.0")
        
        # Color values
        elif field_name in ('background_color', 'foreground_color'):
            if isinstance(value, (list, tuple)) and len(value) == 3:
                # Validate RGB values
                for i, component in enumerate(value):
                    if not (0 <= component <= 255):
                        raise ConfigurationError(f"{field_name}[{i}] must be between 0 and 255")
                # Convert to tuple if it's a list
                value = tuple(value)
            else:
                raise ConfigurationError(f"{field_name} must be a 3-element RGB tuple/list")
        
        # Timing intervals
        elif field_name in ('blink_interval', 'idle_interval'):
            if not (0.1 <= value <= 60.0):
                raise ConfigurationError(f"{field_name} must be between 0.1 and 60.0 seconds")
        
        # Timing variations
        elif field_name in ('blink_variation', 'idle_variation'):
            if not (0 <= value <= 30):
                raise ConfigurationError(f"{field_name} must be between 0 and 30 seconds")
        
        return value
    
    def parse_command_line(self, args: Optional[list] = None) -> RoboEyesConfig:
        """
        Parse command-line arguments and create configuration.
        
        Args:
            args: Optional list of arguments (uses sys.argv if None)
            
        Returns:
            RoboEyesConfig instance with command-line overrides
        """
        parser = argparse.ArgumentParser(
            description="RoboEyes Desktop - Animated robot eyes for your desktop",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        
        # Window settings
        window_group = parser.add_argument_group('Window Settings')
        window_group.add_argument(
            '--window-width', type=int, default=800,
            help='Window width in pixels (100-4000)'
        )
        window_group.add_argument(
            '--window-height', type=int, default=600,
            help='Window height in pixels (100-4000)'
        )
        window_group.add_argument(
            '--fullscreen', action='store_true',
            help='Start in fullscreen mode'
        )
        window_group.add_argument(
            '--no-resize', action='store_true',
            help='Disable window resizing'
        )
        
        # Display settings
        display_group = parser.add_argument_group('Display Settings')
        display_group.add_argument(
            '--display-width', type=int, default=128,
            help='Eye display width in pixels (32-1024)'
        )
        display_group.add_argument(
            '--display-height', type=int, default=64,
            help='Eye display height in pixels (32-1024)'
        )
        display_group.add_argument(
            '--eye-width', type=int, default=36,
            help='Individual eye width in pixels (8-128)'
        )
        display_group.add_argument(
            '--eye-height', type=int, default=36,
            help='Individual eye height in pixels (8-128)'
        )
        display_group.add_argument(
            '--scale-factor', type=float, default=1.0,
            help='Display scaling factor (0.1-10.0)'
        )
        
        # Animation settings
        animation_group = parser.add_argument_group('Animation Settings')
        animation_group.add_argument(
            '--frame-rate', type=int, default=60,
            help='Target frame rate in FPS (1-120)'
        )
        animation_group.add_argument(
            '--auto-blinker', action='store_true',
            help='Enable automatic blinking'
        )
        animation_group.add_argument(
            '--blink-interval', type=float, default=1.0,
            help='Blink interval in seconds (0.1-60.0)'
        )
        animation_group.add_argument(
            '--blink-variation', type=int, default=4,
            help='Blink timing variation in seconds (0-30)'
        )
        animation_group.add_argument(
            '--idle-mode', action='store_true',
            help='Enable idle eye movement'
        )
        animation_group.add_argument(
            '--idle-interval', type=float, default=1.0,
            help='Idle movement interval in seconds (0.1-60.0)'
        )
        animation_group.add_argument(
            '--idle-variation', type=int, default=3,
            help='Idle timing variation in seconds (0-30)'
        )
        
        # Configuration file
        config_group = parser.add_argument_group('Configuration')
        config_group.add_argument(
            '--config', type=str,
            help='Path to configuration file'
        )
        config_group.add_argument(
            '--save-config', action='store_true',
            help='Save current settings to configuration file'
        )
        config_group.add_argument(
            '--debug', action='store_true',
            help='Enable debug mode'
        )
        
        # Parse arguments
        parsed_args = parser.parse_args(args)
        
        # Load base configuration from file if specified
        if parsed_args.config:
            try:
                # Create a temporary manager for the specified config file
                temp_manager = ConfigManager(parsed_args.config)
                base_config = temp_manager.load_config()
            except ConfigurationError as e:
                print(f"Warning: {e}")
                base_config = RoboEyesConfig()
        else:
            base_config = RoboEyesConfig()
        
        # Override with command-line arguments
        config_dict = asdict(base_config)
        
        # Map command-line arguments to config fields (only override if explicitly set)
        # We need to check if the argument was actually provided vs using the default
        
        # Get the default values from the parser
        defaults = {
            'window_width': 800,
            'window_height': 600,
            'fullscreen': False,
            'no_resize': False,
            'display_width': 128,
            'display_height': 64,
            'eye_width': 36,
            'eye_height': 36,
            'scale_factor': 1.0,
            'frame_rate': 60,
            'auto_blinker': False,
            'blink_interval': 1.0,
            'blink_variation': 4,
            'idle_mode': False,
            'idle_interval': 1.0,
            'idle_variation': 3,
            'debug': False,
        }
        
        # Only override config values if they were explicitly provided on command line
        # (i.e., different from defaults or boolean flags that were set)
        if parsed_args.window_width != defaults['window_width']:
            config_dict['window_width'] = parsed_args.window_width
        if parsed_args.window_height != defaults['window_height']:
            config_dict['window_height'] = parsed_args.window_height
        if parsed_args.fullscreen:  # Boolean flag, only set if True
            config_dict['fullscreen'] = True
        if parsed_args.no_resize:  # Boolean flag, only set if True
            config_dict['resizable'] = False
        if parsed_args.display_width != defaults['display_width']:
            config_dict['display_width'] = parsed_args.display_width
        if parsed_args.display_height != defaults['display_height']:
            config_dict['display_height'] = parsed_args.display_height
        if parsed_args.eye_width != defaults['eye_width']:
            config_dict['eye_width'] = parsed_args.eye_width
        if parsed_args.eye_height != defaults['eye_height']:
            config_dict['eye_height'] = parsed_args.eye_height
        if parsed_args.scale_factor != defaults['scale_factor']:
            config_dict['scale_factor'] = parsed_args.scale_factor
        if parsed_args.frame_rate != defaults['frame_rate']:
            config_dict['frame_rate'] = parsed_args.frame_rate
        if parsed_args.auto_blinker:  # Boolean flag, only set if True
            config_dict['auto_blinker'] = True
        if parsed_args.blink_interval != defaults['blink_interval']:
            config_dict['blink_interval'] = parsed_args.blink_interval
        if parsed_args.blink_variation != defaults['blink_variation']:
            config_dict['blink_variation'] = parsed_args.blink_variation
        if parsed_args.idle_mode:  # Boolean flag, only set if True
            config_dict['idle_mode'] = True
        if parsed_args.idle_interval != defaults['idle_interval']:
            config_dict['idle_interval'] = parsed_args.idle_interval
        if parsed_args.idle_variation != defaults['idle_variation']:
            config_dict['idle_variation'] = parsed_args.idle_variation
        if parsed_args.debug:  # Boolean flag, only set if True
            config_dict['debug'] = True
        
        # Always set config_file if provided
        if parsed_args.config:
            config_dict['config_file'] = parsed_args.config
        
        # Validate the final configuration
        try:
            validated_config = self._validate_config_data(config_dict)
            final_config = RoboEyesConfig(**validated_config)
        except ConfigurationError as e:
            parser.error(f"Configuration validation failed: {e}")
        
        # Save configuration if requested
        if parsed_args.save_config:
            try:
                config_file = parsed_args.config or self.config_file
                self.save_config(final_config, config_file)
                print(f"Configuration saved to {config_file}")
            except ConfigurationError as e:
                print(f"Warning: Failed to save configuration: {e}")
        
        return final_config
    
    def get_config(self) -> RoboEyesConfig:
        """Get the current configuration."""
        return self._config
    
    def update_config(self, **kwargs) -> None:
        """
        Update configuration with new values.
        
        Args:
            **kwargs: Configuration fields to update
            
        Raises:
            ConfigurationError: If validation fails
        """
        config_dict = asdict(self._config)
        config_dict.update(kwargs)
        
        validated_data = self._validate_config_data(config_dict)
        self._config = RoboEyesConfig(**validated_data)


def create_default_config() -> RoboEyesConfig:
    """Create a default configuration instance."""
    return RoboEyesConfig()


def load_config_from_file(config_file: str) -> RoboEyesConfig:
    """
    Load configuration from a specific file.
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        RoboEyesConfig instance
        
    Raises:
        ConfigurationError: If configuration cannot be loaded
    """
    manager = ConfigManager(config_file)
    return manager.load_config()


def save_config_to_file(config: RoboEyesConfig, config_file: str) -> None:
    """
    Save configuration to a specific file.
    
    Args:
        config: Configuration to save
        config_file: Path to configuration file
        
    Raises:
        ConfigurationError: If configuration cannot be saved
    """
    manager = ConfigManager(config_file)
    manager.save_config(config, config_file)