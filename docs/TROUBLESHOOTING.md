# RoboEyes Desktop Troubleshooting Guide

This guide helps you diagnose and resolve common issues with RoboEyes Desktop.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Application Startup Problems](#application-startup-problems)
3. [Performance Issues](#performance-issues)
4. [Display and Graphics Problems](#display-and-graphics-problems)
5. [Input and Control Issues](#input-and-control-issues)
6. [Configuration Problems](#configuration-problems)
7. [Platform-Specific Issues](#platform-specific-issues)
8. [Advanced Debugging](#advanced-debugging)

## Installation Issues

### Python Version Problems

**Problem**: Application fails to start with Python version errors.

**Symptoms**:
- `SyntaxError` related to type hints or f-strings
- `ModuleNotFoundError` for standard library modules
- Import errors for dataclasses

**Solutions**:
1. **Check Python version**:
   ```bash
   python --version
   # Should be 3.8 or higher
   ```

2. **Upgrade Python**:
   - **Windows**: Download from [python.org](https://www.python.org/downloads/)
   - **macOS**: `brew install python` or download from python.org
   - **Linux**: `sudo apt update && sudo apt install python3.8` (or higher)

3. **Use virtual environment**:
   ```bash
   python -m venv roboeyes_env
   source roboeyes_env/bin/activate  # Linux/macOS
   roboeyes_env\Scripts\activate     # Windows
   pip install -r requirements.txt
   ```

### Pygame Installation Failures

**Problem**: Pygame fails to install or import.

**Symptoms**:
- `pip install pygame` fails with compilation errors
- `ImportError: No module named 'pygame'`
- SDL-related error messages

**Solutions**:

**Windows**:
```bash
# Install Visual C++ Build Tools first
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Then install pygame
pip install pygame

# If still failing, try pre-compiled wheel
pip install --upgrade pip
pip install pygame --force-reinstall
```

**macOS**:
```bash
# Install Xcode Command Line Tools
xcode-select --install

# Install pygame
pip install pygame

# If using M1/M2 Mac and having issues
arch -arm64 pip install pygame
```

**Linux**:
```bash
# Install system dependencies first
sudo apt update
sudo apt install python3-dev libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libfreetype6-dev libportmidi-dev

# Then install pygame
pip install pygame
```

### Missing Dependencies

**Problem**: Other required packages are missing.

**Solutions**:
```bash
# Install all requirements
pip install -r requirements.txt

# Or install individually
pip install pygame dataclasses typing-extensions
```

## Application Startup Problems

### Pygame Initialization Errors

**Problem**: Application crashes on startup with Pygame errors.

**Symptoms**:
- `PygameInitializationError: Pygame failed to initialize`
- `pygame.error: No available video device`
- Black screen or immediate crash

**Solutions**:

1. **Check display environment**:
   ```bash
   # Linux: Ensure X11 or Wayland is running
   echo $DISPLAY
   echo $WAYLAND_DISPLAY
   
   # If empty, you may be in a headless environment
   ```

2. **Update graphics drivers**:
   - **Windows**: Update through Device Manager or manufacturer website
   - **macOS**: Update through System Preferences
   - **Linux**: `sudo apt update && sudo apt upgrade` or install proprietary drivers

3. **Try different video drivers**:
   ```bash
   # Set SDL video driver explicitly
   export SDL_VIDEODRIVER=x11    # Linux X11
   export SDL_VIDEODRIVER=wayland # Linux Wayland
   export SDL_VIDEODRIVER=windib  # Windows fallback
   ```

4. **Run with debug information**:
   ```bash
   python -m src.roboeyes.desktop_roboeyes --debug
   ```

### Permission Errors

**Problem**: Application fails to start due to permission issues.

**Symptoms**:
- `PermissionError` when creating config files
- Cannot write to log directories
- Access denied errors

**Solutions**:

1. **Check file permissions**:
   ```bash
   # Linux/macOS
   ls -la ~/.config/roboeyes/
   chmod 755 ~/.config/roboeyes/
   
   # Windows - Run as Administrator if needed
   ```

2. **Create directories manually**:
   ```bash
   # Linux/macOS
   mkdir -p ~/.config/roboeyes
   mkdir -p ~/.local/share/roboeyes/logs
   
   # Windows
   mkdir "%APPDATA%\RoboEyes"
   mkdir "%LOCALAPPDATA%\RoboEyes\Logs"
   ```

## Performance Issues

### Low Frame Rate

**Problem**: Animation is choppy or slow.

**Symptoms**:
- Jerky eye movements
- Delayed response to input
- Frame rate below 30 FPS

**Solutions**:

1. **Lower frame rate target**:
   ```bash
   python -m src.roboeyes.desktop_roboeyes --frame-rate 30
   ```

2. **Reduce window size**:
   ```bash
   python -m src.roboeyes.desktop_roboeyes --window-width 640 --window-height 480
   ```

3. **Disable performance-heavy features**:
   ```python
   # In your code
   config = RoboEyesConfig(
       frame_rate=30,
       window_width=640,
       window_height=480
   )
   robo = DesktopRoboEyes(config=config)
   ```

4. **Close other applications**:
   - Close web browsers with many tabs
   - Stop video streaming or games
   - Check Task Manager/Activity Monitor for CPU usage

5. **Enable hardware acceleration**:
   ```bash
   # Linux: Install hardware-accelerated drivers
   sudo apt install mesa-utils
   glxinfo | grep "direct rendering"  # Should show "Yes"
   ```

### High CPU Usage

**Problem**: Application uses excessive CPU resources.

**Solutions**:

1. **Enable dirty rectangle optimization**:
   ```python
   # This is enabled by default, but ensure it's working
   robo = DesktopRoboEyes(config=config)
   # Check logs for "Using dirty rectangle optimization"
   ```

2. **Reduce animation complexity**:
   ```python
   # Disable auto-blinker and idle mode temporarily
   robo.set_auto_blinker(OFF)
   robo.set_idle_mode(OFF)
   ```

3. **Monitor performance**:
   ```bash
   python -m src.roboeyes.desktop_roboeyes --debug
   # Check logs for performance metrics
   ```

### Memory Leaks

**Problem**: Memory usage increases over time.

**Solutions**:

1. **Monitor memory usage**:
   ```python
   # Enable performance monitoring
   robo.performance_monitor.enable_memory_tracking = True
   ```

2. **Restart periodically**:
   - For long-running applications, implement periodic restarts
   - Monitor memory usage in Task Manager/Activity Monitor

## Display and Graphics Problems

### Window Not Appearing

**Problem**: Application starts but no window is visible.

**Solutions**:

1. **Check if window is off-screen**:
   ```bash
   # Try different window position
   python -m src.roboeyes.desktop_roboeyes --window-width 800 --window-height 600
   ```

2. **Try fullscreen mode**:
   ```bash
   python -m src.roboeyes.desktop_roboeyes --fullscreen
   ```

3. **Check display configuration**:
   - Ensure monitor is connected and active
   - Try different display if using multiple monitors

### Scaling Issues

**Problem**: Eyes appear too small or too large.

**Solutions**:

1. **Adjust scale factor**:
   ```bash
   python -m src.roboeyes.desktop_roboeyes --scale-factor 2.0
   ```

2. **Modify display dimensions**:
   ```bash
   python -m src.roboeyes.desktop_roboeyes --display-width 256 --display-height 128
   ```

3. **For high-DPI displays**:
   ```python
   config = RoboEyesConfig(
       window_width=1600,
       window_height=1200,
       scale_factor=2.0
   )
   ```

### Color Problems

**Problem**: Colors appear wrong or washed out.

**Solutions**:

1. **Check color depth**:
   ```python
   # Ensure 32-bit color depth
   pygame.display.set_mode((800, 600), pygame.DOUBLEBUF, 32)
   ```

2. **Adjust color settings**:
   ```python
   config = RoboEyesConfig(
       background_color=(0, 0, 0),      # Pure black
       foreground_color=(255, 255, 255) # Pure white
   )
   ```

### Font Rendering Issues

**Problem**: Text in help overlay appears corrupted or missing.

**Solutions**:

1. **Install system fonts**:
   ```bash
   # Linux
   sudo apt install fonts-dejavu fonts-liberation
   
   # macOS - fonts should be available by default
   
   # Windows - ensure Arial is installed
   ```

2. **Check font loading**:
   ```python
   # In debug mode, check logs for font loading messages
   python -m src.roboeyes.desktop_roboeyes --debug
   ```

## Input and Control Issues

### Keyboard Not Responding

**Problem**: Keyboard controls don't work.

**Solutions**:

1. **Ensure window has focus**:
   - Click on the RoboEyes window
   - Check if window is minimized or behind other windows

2. **Check keyboard layout**:
   - US keyboard layout is recommended
   - Some keys may be mapped differently on international layouts

3. **Test with mouse controls**:
   - If mouse works but keyboard doesn't, it's likely a focus issue
   - Try Alt+Tab to ensure window focus

4. **Disable conflicting software**:
   - Gaming software that captures keyboard input
   - Screen readers or accessibility software
   - Virtual keyboard software

### Mouse Controls Not Working

**Problem**: Mouse clicks don't trigger actions.

**Solutions**:

1. **Check click area**:
   - Ensure you're clicking within the eye display area
   - Try clicking in the center of the window

2. **Test different mouse buttons**:
   - Left click should make eyes look at position
   - Right click should trigger blink

3. **Check mouse sensitivity**:
   ```python
   # Mouse coordinates are automatically scaled
   # No manual adjustment should be needed
   ```

### Help Overlay Not Showing

**Problem**: Pressing H or F1 doesn't show help.

**Solutions**:

1. **Try both keys**:
   - Press H key
   - Press F1 key
   - Ensure Caps Lock is off

2. **Check if help is already visible**:
   - Help overlay toggles on/off
   - Look for semi-transparent text overlay

3. **Window focus issue**:
   - Click on window first, then press H

## Configuration Problems

### Configuration File Errors

**Problem**: Application fails to load or save configuration.

**Symptoms**:
- `ConfigurationError` on startup
- Settings not persisting between sessions
- JSON parsing errors

**Solutions**:

1. **Check configuration file location**:
   ```bash
   # Linux
   ls -la ~/.config/roboeyes/roboeyes_config.json
   
   # macOS
   ls -la ~/Library/Application\ Support/RoboEyes/roboeyes_config.json
   
   # Windows
   dir "%APPDATA%\RoboEyes\roboeyes_config.json"
   ```

2. **Validate JSON syntax**:
   ```bash
   # Use online JSON validator or
   python -m json.tool ~/.config/roboeyes/roboeyes_config.json
   ```

3. **Reset configuration**:
   ```bash
   # Delete corrupted config file
   rm ~/.config/roboeyes/roboeyes_config.json  # Linux/macOS
   del "%APPDATA%\RoboEyes\roboeyes_config.json"  # Windows
   
   # Application will create new default config
   ```

4. **Create minimal config**:
   ```json
   {
     "window_width": 800,
     "window_height": 600,
     "frame_rate": 60,
     "debug": false
   }
   ```

### Command Line Argument Errors

**Problem**: Command line arguments not working or causing errors.

**Solutions**:

1. **Check argument syntax**:
   ```bash
   # Correct
   python -m src.roboeyes.desktop_roboeyes --window-width 1024
   
   # Incorrect
   python -m src.roboeyes.desktop_roboeyes --window-width=1024
   ```

2. **Use help to see available options**:
   ```bash
   python -m src.roboeyes.desktop_roboeyes --help
   ```

3. **Quote arguments with spaces**:
   ```bash
   python -m src.roboeyes.desktop_roboeyes --config "my config.json"
   ```

## Platform-Specific Issues

### Windows Issues

**DirectX vs OpenGL**:
```bash
# Force OpenGL if DirectX causes issues
set SDL_VIDEODRIVER=opengl
python -m src.roboeyes.desktop_roboeyes
```

**Windows Defender**:
- Add exception for RoboEyes directory
- Temporarily disable real-time protection for testing

**High DPI Scaling**:
```python
# Add to your script before importing pygame
import os
os.environ['SDL_VIDEO_WINDOW_POS'] = 'centered'
os.environ['SDL_VIDEO_CENTERED'] = '1'
```

### macOS Issues

**Gatekeeper**:
```bash
# If blocked by Gatekeeper
sudo spctl --master-disable  # Temporarily disable
# Or add specific exception in System Preferences > Security
```

**Retina Display**:
```python
# Retina displays are handled automatically
# If issues occur, try:
config = RoboEyesConfig(scale_factor=0.5)  # Half scale for Retina
```

**Permission Dialogs**:
- Grant accessibility permissions if requested
- Allow input monitoring in System Preferences > Security & Privacy

### Linux Issues

**Wayland vs X11**:
```bash
# Force X11 if Wayland has issues
export GDK_BACKEND=x11
export QT_QPA_PLATFORM=xcb
python -m src.roboeyes.desktop_roboeyes
```

**Audio Group**:
```bash
# Add user to audio group (may be required for some systems)
sudo usermod -a -G audio $USER
# Log out and back in
```

**Missing Libraries**:
```bash
# Install additional libraries if needed
sudo apt install libgl1-mesa-glx libglib2.0-0 libxrandr2 libxss1 libxcursor1 libxcomposite1 libasound2 libxi6 libxtst6
```

## Advanced Debugging

### Enable Debug Logging

```bash
# Run with debug mode
python -m src.roboeyes.desktop_roboeyes --debug
```

### Check Log Files

**Linux**:
```bash
tail -f ~/.local/share/roboeyes/logs/roboeyes.log
```

**macOS**:
```bash
tail -f ~/Library/Logs/RoboEyes/roboeyes.log
```

**Windows**:
```cmd
type "%LOCALAPPDATA%\RoboEyes\Logs\roboeyes.log"
```

### Performance Profiling

```python
import cProfile
import pstats

# Profile the application
cProfile.run('robo.run()', 'roboeyes_profile.prof')

# Analyze results
stats = pstats.Stats('roboeyes_profile.prof')
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 functions
```

### Memory Profiling

```bash
# Install memory profiler
pip install memory-profiler psutil

# Run with memory profiling
python -m memory_profiler examples/desktop_basic.py
```

### Network Debugging (if applicable)

```bash
# Check for network-related issues
netstat -an | grep :8080  # If using network features
```

### System Information

```python
# Get system information for bug reports
import platform
import pygame
import sys

print(f"Python: {sys.version}")
print(f"Platform: {platform.platform()}")
print(f"Pygame: {pygame.version.ver}")
print(f"SDL: {pygame.version.SDL}")

# Graphics information
pygame.init()
info = pygame.display.Info()
print(f"Display: {info.bitsize}-bit, {info.fmt}")
```

## Getting Help

### Before Reporting Issues

1. **Check this troubleshooting guide**
2. **Search existing issues** on the project repository
3. **Try with minimal configuration**:
   ```bash
   python -m src.roboeyes.desktop_roboeyes --debug
   ```
4. **Test with examples**:
   ```bash
   python examples/desktop_basic.py
   ```

### Information to Include in Bug Reports

1. **System Information**:
   - Operating system and version
   - Python version
   - Pygame version
   - Graphics card and drivers

2. **Error Messages**:
   - Complete error traceback
   - Log file contents (with --debug)
   - Screenshots if applicable

3. **Reproduction Steps**:
   - Exact commands used
   - Configuration files
   - Minimal code example

4. **Expected vs Actual Behavior**:
   - What you expected to happen
   - What actually happened
   - Any workarounds you've tried

### Community Resources

- **Documentation**: Check the `docs/` directory
- **Examples**: Run examples in `examples/` directory
- **API Reference**: See `docs/API_DOCUMENTATION.md`
- **Installation Guide**: See `INSTALL.md`

Remember: Most issues are related to environment setup, graphics drivers, or configuration problems. Following this guide systematically should resolve the majority of common issues.