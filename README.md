# SBC-Man Game Launcher

A cross-platform Python game launcher designed for handheld gaming devices with adaptive hardware detection, customizable UI, and game management.

## Features

- **Multi-Device Support**: Automatic detection for Anbernic, Miyoo, Retroid, and desktop devices
- **Hardware Detection**: Auto-probes display resolution, input devices, storage, and CPU
- **Hierarchical Configuration**: 4-layer configuration system (default → device → OS → user)
- **Layered Input Mapping**: Flexible input system with per-game overrides
- **Game Management**: Browse, download, install, and launch games
- **Customizable**: Extensible architecture for new devices and features

## Requirements

- Python 3.11+
- pygame-ce >= 2.1.0
- requests >= 2.28.0
- Linux-based OS (primary target)

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/hblok/sbc-man.git
cd sbc-man

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -e .

# Or install with development tools
pip install -e ".[dev]"
```

### System Dependencies (Linux)

```bash
# Ubuntu/Debian
sudo apt-get install python3-dev python3-pip
sudo apt-get install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev

# Arch Linux
sudo pacman -S python python-pip
sudo pacman -S sdl2 sdl2_image sdl2_mixer sdl2_ttf
```

## Usage

### Running the Launcher

```bash
# From source
python main.py

# Or if installed as package
sbc-man
```

### Navigation

- **Arrow Keys / D-Pad**: Navigate menus
- **Enter / A Button**: Confirm selection
- **ESC / B Button**: Cancel / Go back
- **Start / Menu Button**: Open menu

### Configuration

Configuration files are stored in:
- **System Config**: `src/config/` (shipped with application)
- **User Config**: `~/.local/share/sbc-man/` (runtime data)

#### Configuration Hierarchy

1. `config/devices/default.json` - Base configuration
2. `config/devices/{device}.json` - Device-specific overrides
3. `config/os_types/{os}.json` - OS-specific overrides
4. `data/user_config.json` - User overrides

#### Adding Custom Input Mappings

Edit `~/.local/share/sbc-man/input_overrides/device.json`:

```json
{
  "confirm": ["BUTTON_A", "RETURN"],
  "cancel": ["BUTTON_B", "ESCAPE"],
  "menu": ["BUTTON_START"]
}
```

For per-game mappings, create:
`~/.local/share/sbc-man/input_overrides/games/{game_id}.json`

### Adding Games

Games are stored in `~/.local/share/sbc-man/games.json`. You can:

1. **Download via UI**: Use the "Download Games" menu
2. **Manual Installation**: Add game metadata to `games.json`

Example game entry:

```json
{
  "id": "my-game",
  "name": "My Game",
  "version": "1.0.0",
  "description": "A fun game",
  "author": "Game Developer",
  "install_path": "/path/to/game",
  "entry_point": "main.py",
  "installed": true,
  "download_url": "https://example.com/game.zip"
}
```

## Development

### Running Tests

```bash
# Run all tests
python -m unittest discover tests

# Run with coverage
coverage run -m unittest discover tests
coverage report
coverage html  # Generate HTML report

# Run specific test file
python -m unittest tests/unit/test_hardware_detection.py
```

### Headless Testing

Tests run in headless mode by default using SDL dummy drivers:

```bash
# Set environment variables for headless testing
export SDL_VIDEODRIVER=dummy
export SDL_AUDIODRIVER=dummy

python -m unittest discover tests
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

### Project Structure

```
sbc-man/
├── main.py                 # Entry point
├── src/
│   ├── core/              # Application core
│   ├── hardware/          # Hardware detection
│   ├── models/            # Data models
│   ├── services/          # Shared services
│   ├── states/            # Application states
│   ├── views/             # UI components
│   └── config/            # Default configurations
├── tests/
│   ├── unit/              # Unit tests
│   └── integration/       # Integration tests
└── docs/                  # Documentation
```

## Architecture

### Core Components

1. **Hardware Layer**: Device detection, capability probing, configuration loading
2. **Core Layer**: Application orchestration, state management, game loop
3. **Service Layer**: Input handling, file operations, network, process launching
4. **Model Layer**: Game data, library management, configuration, downloads
5. **State Layer**: Application states (menu, game list, download, settings, playing)
6. **View Layer**: UI rendering (integrated into states)

### State Machine

```
Menu → Game List → Playing
  ↓         ↓
Download  Settings
```

### Configuration System

- **Auto-Detection**: Device type and OS automatically detected
- **Hardware Probing**: Display resolution, input devices, storage, CPU
- **Deep Merge**: Configurations merged with proper precedence
- **Path Expansion**: Environment variables and ~ expanded automatically

### Input System

- **Action-Based**: Physical inputs mapped to logical actions
- **Layered Resolution**: default → device → user → per-game
- **Semantic Naming**: BUTTON_A, BUTTON_SOUTH, etc.

## Device Support

### Supported Devices

- **Anbernic**: RG series handhelds
- **Miyoo**: Miyoo Mini and similar
- **Retroid**: Retroid Pocket series
- **Desktop**: Linux desktop/laptop

### Adding New Devices

1. Create device config: `src/config/devices/mydevice.json`
2. Add detection logic in `src/hardware/detector.py`
3. Create input mapping: `src/config/input_mappings/mydevice.json`

## Troubleshooting

### Display Issues

- Check `~/.local/share/sbc-man/user_config.json`
- Set resolution manually: `{"display": {"resolution": [1280, 720]}}`

### Input Not Working

- Check joystick detection: Look for "Initialized joystick" in logs
- Verify input mappings in config files
- Test with keyboard first (always works)

### Games Not Launching

- Verify game installation path exists
- Check entry point file exists and is executable
- Review logs in console output

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Ensure tests pass and code is formatted
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Credits

- **pygame-ce**: Community Edition of pygame
- **requests**: HTTP library for Python
- **Contributors**: See GitHub contributors page

## Links

- **Repository**: https://github.com/hblok/sbc-man
- **Issues**: https://github.com/hblok/sbc-man/issues
- **Documentation**: See `docs/` directory

## Changelog

### Version 1.0.0 (Initial Release)

- Hardware detection for multiple devices
- Configuration hierarchy system
- Layered input mapping
- Game library management
- Download and installation
- State-based navigation
- Comprehensive test suite