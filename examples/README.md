# RoboEyes Desktop Examples

This directory contains example applications demonstrating various features of the RoboEyes Desktop library, perfect for AI assistant integration and interactive applications.

### `desktop_basic.py`
**Basic desktop functionality demonstration**
- Shows how to initialize RoboEyes for desktop use
- Demonstrates basic eye animations and automated behaviors
- Good starting point for new users
- Includes auto-blinker and idle mode setup

**Usage:**
```bash
python examples/desktop_basic.py
```

### `desktop_interactive.py`
**Interactive demonstration with full keyboard/mouse controls**
- Comprehensive showcase of all RoboEyes features
- Interactive control using keyboard and mouse
- Includes automatic demonstration mode
- Shows real-time status updates

**Key Features:**
- Full keyboard control mapping
- Mouse interaction (click to look, right-click to blink)
- Auto-demo mode (press 'D')
- Status display system

**Usage:**
```bash
python examples/desktop_interactive.py
```

### `desktop_animation_sequence.py`
**Animation sequence system demonstration**
- Shows how to create complex, timed animation sequences
- Demonstrates the sequence-based animation system
- Multiple pre-built sequences showcasing different features
- Sequence control and management

**Key Features:**
- 6 different animation sequences
- Sequence control (start, stop, restart)
- Automatic sequence progression
- Demonstrates timing-based animations without delays

**Usage:**
```bash
python examples/desktop_animation_sequence.py
```

### `desktop_config_demo.py`
**Configuration and customization demonstration**
- Shows different eye shapes and configurations
- Demonstrates behavior presets
- Eye shape customization options
- Auto-cycling through configurations

**Key Features:**
- 8 eye shape presets (round, wide, narrow, etc.)
- 7 behavior presets (calm, alert, sleepy, etc.)
- Auto-cycle mode
- Real-time configuration changes

**Usage:**
```bash
python examples/desktop_config_demo.py
```

### `ollama_integration_example.py`
**Complete Ollama LLM integration example**
- Shows how to connect RoboEyes with Ollama for AI assistant visual feedback
- Eyes react to different conversation states (idle, thinking, responding, error)
- Interactive chat interface with visual cues
- Demonstrates mood changes based on AI processing states

**Key Features:**
- Real-time visual feedback during AI conversations
- Different eye expressions for different AI states
- Conversation history management
- Error handling with visual indicators

**Requirements:**
```bash
pip install requests
# Ollama must be running: ollama serve
```

**Usage:**
```bash
python examples/ollama_integration_example.py
```

## AI Integration Examples

These examples show how to integrate RoboEyes with AI systems:

### For Ollama Integration
- **`desktop_basic.py`** - Simple setup perfect for AI assistant backends
- **`desktop_interactive.py`** - Interactive demo showing all available expressions
- **`desktop_animation_sequence.py`** - Timed sequences for conversation flow

### For Chatbot Integration
- Use mood changes to reflect conversation context (happy, curious, tired)
- Animation sequences for thinking, responding, and idle states
- Interactive controls for real-time expression changes during conversations

### Integration Tips
- Use `CURIOUS` mood when the AI is processing a question
- Use `HAPPY` mood for positive responses
- Use `TIRED` mood for long processing tasks
- Use animation sequences to show conversation flow states

## Getting Started

1. **For desktop use**, start with `desktop_basic.py` to understand the basics
2. **For interactive exploration**, try `desktop_interactive.py`
3. **For animation sequences**, explore `desktop_animation_sequence.py`
4. **For customization**, check out `desktop_config_demo.py`

## Requirements

Desktop examples require:
- Python 3.7+
- Pygame
- The RoboEyes desktop library (in `src/` directory)

Install requirements:
```bash
pip install pygame
```

## Controls

All desktop examples support these common controls:
- **H** or **F1**: Show/hide help overlay
- **ESC**: Exit (or exit fullscreen)
- **F11**: Toggle fullscreen
- **Number keys 1-7**: Change moods
- **Arrow keys**: Move eyes
- **Space**: Blink
- **Mouse**: Click to look at position, right-click to blink

See individual example documentation or press H in any example for specific controls.