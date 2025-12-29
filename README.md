# SBC-Man Game Launcher

**SBC-Man** is a game manager for SBC (Single Board Computer) handheld game consoles that downloads, installs, and launches games from the Max Blocks collection of Pygame-based games.

## Overview

SBC-Man provides a simple interface for managing your game collection on handheld gaming devices. It integrates with [PortMaster](https://portmaster.games/) to launch games and can install games directly into the PortMaster directory structure.

### Key Features

- **Game Library Management**: Browse and manage your installed games
- **Download System**: Download and install games from the Max Blocks collection
- **PortMaster Integration**: Piggy-backs on PortMaster for game launching
- **Device Detection**: Automatically detects hardware and configures settings
- **Input Mapping**: Flexible input system with device-specific configurations
- **Cross-platform Support**: Works on ArkOS, JELOS, Batocera, and other Linux-based handheld gaming OSes

## Building and Testing

### Prerequisites

First, install [Bazel](https://bazel.build/install) - the build system used by this project.

### Build Commands

```bash
# Run all tests
bazel test ...

# Build the wheel package
bazel build //sbcman:sbc_man_wheel
```

### Running from Source

```bash
# Set Python path and run
export PYTHONPATH=./sbc-man
./sbcman/main.py
```

## Installation

### From Wheel Package

```bash
# After building the wheel
pip install bazel-bin/sbcman/sbc_man-*.whl
```

### From Source

```bash
# Clone the repository
git clone https://github.com/hblok/sbc-man.git
cd sbc-man

# Install dependencies
pip install -r requirements.txt

# Run directly
export PYTHONPATH=.
python sbcman/main.py
```

## Project Structure

```
sbc-man/
├── sbcman/
│   ├── core/          # Main application components
│   ├── hardware/      # Hardware detection and configuration
│   ├── models/        # Data models (Game, GameLibrary, etc.)
│   ├── services/      # Service layer (Network, Input, Process)
│   ├── states/        # Application states (Menu, GameList, Download, etc.)
│   ├── views/         # View components
│   └── config/        # Configuration files for devices and input mappings
├── tests/
│   ├── unit/          # Unit tests
│   └── integration/   # Integration tests
├── google/            # Google Protocol Buffers library
└── docs/              # Documentation files
```

## Architecture

### State Pattern

The application uses a state-based architecture for navigation:

- **MenuState**: Main menu with options to browse, download, configure, and exit
- **GameListState**: Browse installed and available games
- **DownloadState**: Download and install new games with progress tracking
- **SettingsState**: Configure application settings
- **PlayingState**: Launch and monitor running games
- **UpdateState**: Check for and install application updates

### Services Layer

- **NetworkService**: HTTP operations with timeout and retry handling
- **InputHandler**: Layered input mapping system for controllers and keyboards
- **ProcessLauncher**: Game process management and monitoring
- **FileOps**: File system operations and utilities
- **Updater**: Application update management

### Models

- **Game**: Game metadata and installation information
- **GameLibrary**: Collection of games with persistence
- **DownloadManager**: Game download management with observer pattern
- **ConfigManager**: Hierarchical configuration management

## Configuration

SBC-Man automatically detects your hardware and loads appropriate configuration files from `sbcman/config/`:

- **devices/**: Device-specific configurations (Anbernic, Miyoo, Retroid, etc.)
- **input_mappings/**: Input mapping configurations for different devices
- **os_types/**: OS-specific configurations (ArkOS, JELOS, Batocera, etc.)

Configuration is hierarchical and can be overridden at device, OS, and game levels.

## Development

### Running Tests

```bash
# Run all tests with Bazel
bazel test ...

# Run specific test suite
bazel test //tests/unit:all
bazel test //tests/integration:all

# Run with coverage (using pytest directly)
pip install coverage pytest
coverage run -m pytest tests/
coverage report
```

### Code Style

The project follows Python best practices:
- Type hints for function signatures
- Docstrings for all public methods
- PEP 8 style guidelines
- Comprehensive unit and integration tests

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Ensure all tests pass (`bazel test ...`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

### SBC-Man Code

All original SBC-Man code is licensed under the **GNU General Public License v3.0 or later (GPL-3.0-or-later)**.

```
Copyright (C) 2025 H. Blok

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
```

See the [LICENSE](LICENSE) file for the complete GPL v3 license text.

### Google Protocol Buffers

The Google Protocol Buffers library included in the `google/` directory is licensed under the BSD 3-Clause License.

```
Copyright 2008 Google Inc. All rights reserved.
```

See the license information at: https://developers.google.com/open-source/licenses/bsd

## Links

- **Project Repository**: https://github.com/hblok/sbc-man
- **PortMaster**: https://portmaster.games/
- **Max Blocks Games**: https://github.com/hblok/max_blocks
- **Bazel Build System**: https://bazel.build/

## Support

For issues, questions, or contributions, please visit the [GitHub Issues](https://github.com/hblok/sbc-man/issues) page.