# RoboEyes Desktop Installation Guide

This guide provides platform-specific installation instructions for RoboEyes Desktop.

## System Requirements

- Python 3.8 or higher
- Pygame 2.5.0 or higher
- At least 100MB of free disk space
- Graphics card with OpenGL support (recommended)

## Platform-Specific Installation

### Windows

#### Prerequisites
1. **Python Installation**
   - Download Python from [python.org](https://www.python.org/downloads/windows/)
   - During installation, check "Add Python to PATH"
   - Verify installation: `python --version`

2. **Visual C++ Redistributable** (if not already installed)
   - Download from [Microsoft](https://aka.ms/vs/17/release/vc_redist.x64.exe)
   - Required for Pygame compilation

#### Installation Steps
```cmd
# Clone or download the repository
git clone https://github.com/roboeyes/roboeyes-desktop.git
cd roboeyes-desktop

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install RoboEyes Desktop
pip install -e .

# Run the application
python -m src.roboeyes.desktop_roboeyes
```

#### Windows-Specific Notes
- Configuration files are stored in `%APPDATA%\RoboEyes\`
- Log files are stored in `%LOCALAPPDATA%\RoboEyes\Logs\`
- The application uses DirectX for optimal performance
- Windows Defender may flag the executable - add an exception if needed

#### Troubleshooting Windows
- **Pygame installation fails**: Install Microsoft Visual C++ Build Tools
- **Display issues**: Update graphics drivers
- **Permission errors**: Run Command Prompt as Administrator
- **Font rendering issues**: Install Arial font if missing

### macOS

#### Prerequisites
1. **Python Installation**
   - Install via Homebrew (recommended): `brew install python`
   - Or download from [python.org](https://www.python.org/downloads/macos/)
   - Verify installation: `python3 --version`

2. **Xcode Command Line Tools**
   ```bash
   xcode-select --install
   ```

#### Installation Steps
```bash
# Clone or download the repository
git clone https://github.com/roboeyes/roboeyes-desktop.git
cd roboeyes-desktop

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install RoboEyes Desktop
pip install -e .

# Run the application
python -m src.roboeyes.desktop_roboeyes
```

#### macOS-Specific Notes
- Configuration files are stored in `~/Library/Application Support/RoboEyes/`
- Log files are stored in `~/Library/Logs/RoboEyes/`
- The application uses Cocoa for native window management
- Retina displays are automatically handled

#### Troubleshooting macOS
- **Permission denied**: Use `sudo` for system-wide installation
- **Pygame installation fails**: Install Xcode Command Line Tools
- **Display scaling issues**: The app automatically detects Retina displays
- **Font issues**: System fonts are automatically detected

### Linux

#### Prerequisites
1. **Python Installation**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3 python3-pip python3-venv

   # Fedora/RHEL
   sudo dnf install python3 python3-pip python3-venv

   # Arch Linux
   sudo pacman -S python python-pip
   ```

2. **System Dependencies**
   ```bash
   # Ubuntu/Debian
   sudo apt install python3-dev libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libfreetype6-dev libportmidi-dev

   # Fedora/RHEL
   sudo dnf install python3-devel SDL2-devel SDL2_image-devel SDL2_mixer-devel SDL2_ttf-devel freetype-devel portmidi-devel

   # Arch Linux
   sudo pacman -S python-devel sdl2 sdl2_image sdl2_mixer sdl2_ttf freetype2 portmidi
   ```

#### Installation Steps
```bash
# Clone or download the repository
git clone https://github.com/roboeyes/roboeyes-desktop.git
cd roboeyes-desktop

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install RoboEyes Desktop
pip install -e .

# Run the application
python -m src.roboeyes.desktop_roboeyes
```

#### Linux-Specific Notes
- Configuration files are stored in `~/.config/roboeyes/` (or `$XDG_CONFIG_HOME/roboeyes/`)
- Log files are stored in `~/.local/share/roboeyes/logs/` (or `$XDG_DATA_HOME/roboeyes/logs/`)
- The application automatically detects X11 vs Wayland
- Works with most desktop environments (GNOME, KDE, XFCE, etc.)

#### Desktop Environment Specific Notes

**GNOME/Wayland:**
- Uses Wayland backend automatically
- May require `export GDK_BACKEND=wayland` for optimal performance

**KDE Plasma:**
- Works with both X11 and Wayland
- Window decorations follow system theme

**XFCE/X11:**
- Uses X11 backend
- Lightweight and responsive

#### Troubleshooting Linux
- **Pygame installation fails**: Install development packages listed above
- **Display server issues**: Set `SDL_VIDEODRIVER=x11` or `SDL_VIDEODRIVER=wayland`
- **Font issues**: Install `fonts-dejavu` or `liberation-fonts`
- **Permission issues**: Ensure user is in `audio` and `video` groups
- **Wayland issues**: Try running with `--no-wayland` flag or set `GDK_BACKEND=x11`

## Development Installation

For development, install additional dependencies:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run cross-platform tests
pytest tests/test_cross_platform.py

# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## Configuration

### Command Line Options
```bash
# Basic usage
python -m src.roboeyes.desktop_roboeyes

# Custom window size
python -m src.roboeyes.desktop_roboeyes --window-width 1024 --window-height 768

# Fullscreen mode
python -m src.roboeyes.desktop_roboeyes --fullscreen

# Custom frame rate
python -m src.roboeyes.desktop_roboeyes --frame-rate 30

# Enable debug mode
python -m src.roboeyes.desktop_roboeyes --debug

# Use custom config file
python -m src.roboeyes.desktop_roboeyes --config /path/to/config.json

# Save current settings
python -m src.roboeyes.desktop_roboeyes --save-config
```

### Configuration Files

Configuration files are automatically created in platform-appropriate locations:

- **Windows**: `%APPDATA%\RoboEyes\roboeyes_config.json`
- **macOS**: `~/Library/Application Support/RoboEyes/roboeyes_config.json`
- **Linux**: `~/.config/roboeyes/roboeyes_config.json`

Example configuration:
```json
{
  "window_width": 800,
  "window_height": 600,
  "fullscreen": false,
  "frame_rate": 60,
  "auto_blinker": true,
  "blink_interval": 2.0,
  "idle_mode": true,
  "debug": false
}
```

## Performance Optimization

### Windows
- Ensure graphics drivers are up to date
- Use DirectX backend (automatic)
- Enable hardware acceleration in graphics settings
- Close unnecessary background applications

### macOS
- The application automatically uses Metal acceleration
- Retina displays are handled automatically
- Close other graphics-intensive applications for best performance

### Linux
- Install proprietary graphics drivers if available (NVIDIA/AMD)
- Use Wayland for better performance on supported systems
- Adjust compositor settings for gaming/performance mode
- Consider disabling desktop effects during use

## Uninstallation

### Remove Application
```bash
pip uninstall roboeyes-desktop
```

### Remove Configuration Files

**Windows:**
```cmd
rmdir /s "%APPDATA%\RoboEyes"
rmdir /s "%LOCALAPPDATA%\RoboEyes"
```

**macOS:**
```bash
rm -rf ~/Library/Application\ Support/RoboEyes
rm -rf ~/Library/Logs/RoboEyes
rm -rf ~/Library/Caches/RoboEyes
```

**Linux:**
```bash
rm -rf ~/.config/roboeyes
rm -rf ~/.local/share/roboeyes
rm -rf ~/.cache/roboeyes
```

## Getting Help

- **Documentation**: Check the `docs/` directory
- **Issues**: Report bugs on GitHub Issues
- **Discussions**: Join GitHub Discussions for questions
- **Logs**: Check log files in platform-specific locations for debugging

## Platform Testing

The application has been tested on:

- **Windows**: 10, 11 (x64)
- **macOS**: 10.15+, 11.0+, 12.0+ (Intel and Apple Silicon)
- **Linux**: Ubuntu 20.04+, Fedora 35+, Arch Linux, Debian 11+

If you encounter issues on other platforms, please report them with your system information.