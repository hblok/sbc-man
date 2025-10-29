# SBC-Man Game Launcher

SBC-Man is a cross-platform game launcher designed for handheld gaming devices running Linux-based operating systems. It provides a simple interface for browsing, downloading, and launching games with support for various input methods and device configurations.

## Features

- **Cross-platform support**: Works on standard Linux, ArkOS, JELOS, Batocera, and other Linux-based handheld gaming OSes
- **Device detection**: Automatically detects hardware and configures appropriate settings
- **Game library management**: Browse and manage installed games
- **Download system**: Download and install new games with progress tracking
- **Input mapping**: Flexible input mapping system with device-specific configurations
- **State-based architecture**: Clean separation of concerns with state pattern implementation

## Installation

```bash
# Clone the repository
git clone https://github.com/hblok/sbc-man.git
cd sbc-man

# Install dependencies
pip install -e .

# Run the application
sbc-man
```

## Development

### Project Structure

```
sbc-man/
├── src/
│   ├── core/          # Main application components
│   ├── hardware/      # Hardware detection and configuration
│   ├── models/        # Data models
│   ├── services/      # Service layer components
│   ├── states/        # Application states
│   └── views/         # View components (currently integrated with states)
├── tests/
│   ├── unit/          # Unit tests
│   └── integration/   # Integration tests
└── docs/             # Documentation files
```

### Running Tests

```bash
TODO

# Run with coverage
coverage run -m test tests/
coverage report
```

### States

The application uses a state pattern for navigation:

- **MenuState**: Main menu with options to browse games, download games, settings, and exit
- **GameListState**: Browse installed and available games
- **DownloadState**: Download and install new games
- **SettingsState**: Configure application settings
- **PlayingState**: Launch and monitor running games

### Services

- **NetworkService**: HTTP operations with timeout and retry handling
- **InputHandler**: Layered input mapping system
- **ProcessLauncher**: Game process management
- **FileOps**: File system operations

### Models

- **Game**: Game metadata and installation information
- **GameLibrary**: Collection of games with persistence
- **DownloadManager**: Game download management with observer pattern
- **ConfigManager**: Application configuration management

## Configuration

The launcher automatically detects hardware and loads appropriate configuration files from `src/config/`. Configuration can be overridden per-device and per-game.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for your changes
5. Run all tests to ensure they pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.