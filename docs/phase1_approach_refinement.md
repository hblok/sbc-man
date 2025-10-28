# Phase 1: Approach Refinement and Detailed Implementation Strategy

## Implementation Approach Overview

Based on comprehensive documentation analysis, the implementation will follow a **bottom-up, layer-by-layer** approach:

1. **Foundation Layer First**: Hardware detection and configuration
2. **Data Layer Second**: Models and data structures
3. **Service Layer Third**: Shared services
4. **Application Layer Fourth**: Core orchestration
5. **State Layer Fifth**: Application states
6. **View Layer Last**: UI components

This approach ensures each layer has its dependencies available before implementation.

## Key Architecture Decisions

### 1. Entry Point Design
**Requirement**: Zero-logic main.py
```python
# main.py - Absolute minimal entry point
from src.hardware.compat_sdl import setup_sdl_environment
from src.core.application import Application

if __name__ == "__main__":
    setup_sdl_environment()
    Application().run()
```

### 2. Hardware Detection Strategy
**Approach**: File-based detection with safe fallbacks
- Read `/sys/firmware/devicetree/base/model` for ARM devices
- Parse `/etc/os-release` for OS distribution
- Check device-specific mount points
- Environment variable overrides for testing
- Always fallback to 'desktop' and 'standard_linux'

### 3. Configuration Hierarchy Implementation
**4-Layer Merge Strategy**:
1. **Base**: `config/devices/default.json`
2. **Device**: `config/devices/{device_type}.json`
3. **OS**: `config/os_types/{os_type}.json`
4. **User**: `data/user_config.json`
5. **Per-Game** (input only): `data/input_overrides/games/{game_id}.json`

**Deep Merge Algorithm**:
- Recursively merge nested dictionaries
- Lists are replaced, not merged
- Later layers override earlier layers
- Preserve type consistency

### 4. Input Mapping Resolution
**Layered Resolution Order**:
1. Check per-game mapping (if game context set)
2. Check user device override
3. Check device-specific mapping
4. Check default mapping
5. Return None if action not found

**Action-Based Abstraction**:
- Physical inputs (keys, buttons) → Actions (confirm, cancel, menu)
- States handle actions, not raw inputs
- Supports multiple inputs per action
- Semantic button naming (BUTTON_A, BUTTON_SOUTH)

### 5. State Management Pattern
**State Lifecycle**:
```
on_enter(previous_state) → update(dt) loop → handle_events(events) → render(surface) → on_exit()
```

**State Transitions**:
- Clean exit from current state
- Initialize new state with context
- Support state stack for overlays
- Error handling prevents state corruption

### 6. Download Manager with Observer Pattern
**Threading Strategy**:
- Download runs in separate thread
- Progress updates via observer callbacks
- Thread-safe progress tracking
- UI remains responsive during downloads

**Observer Interface**:
```python
def on_progress(downloaded, total):
    # Update UI progress bar
    
def on_complete(success, message):
    # Handle completion
    
def on_error(error_message):
    # Handle errors
```

### 7. Testing Strategy
**Headless Testing Setup**:
```python
# In conftest.py
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
```

**Mock Strategy**:
- Mock pygame.display for headless tests
- Mock pygame.joystick for input tests
- Mock requests for network tests
- Mock subprocess for game launch tests
- Use tmp_path for filesystem isolation

**Coverage Targets**:
- Models: 100%
- Hardware: 95%
- Services: 90%
- States: 85%
- Views: 80%
- Overall: 85%+

## Module Implementation Details

### Hardware Layer

#### detector.py
- **Static methods only** (no class instantiation)
- `get_config()`: Main entry point, orchestrates detection
- `_detect_device()`: File-based device detection
- `_detect_os()`: OS distribution detection
- `_expand_paths()`: Environment variable expansion

#### prober.py
- **Static methods only**
- `probe_all()`: Orchestrates all probing
- `probe_display()`: pygame.display.Info() for resolution
- `probe_input()`: Enumerate joysticks
- `probe_storage()`: Check mount points with shutil.disk_usage()
- `probe_cpu()`: Parse /proc/cpuinfo

#### config_loader.py
- **Instance-based** (needs state for merge)
- `__init__(device_type, os_type, probed_hw)`: Store detection results
- `load_config()`: Execute 4-layer merge
- `_load_json(path)`: Safe JSON loading
- `_deep_merge(base, override)`: Recursive merge algorithm

#### compat_sdl.py
- `setup_sdl_environment()`: Set SDL environment variables
- Called before pygame import in main.py
- Sets video driver, audio driver, joystick settings

### Model Layer

#### game.py
- **Data class** with serialization
- Attributes: id, name, version, description, author, install_path, etc.
- `to_dict()`: Serialize to JSON-compatible dict
- `from_dict()`: Deserialize from dict
- Type hints on all attributes

#### game_library.py
- **Manages game collection**
- `load_games()`: Load from data/games.json
- `save_games()`: Persist to data/games.json
- `add_game()`, `remove_game()`, `get_game()`: CRUD operations
- `get_installed_games()`, `get_available_games()`: Filtering

#### config_manager.py
- **Runtime configuration management**
- `get(key, default)`: Get config value with dot notation
- `set(key, value)`: Set config value
- `save()`: Persist to data/config.json
- Wraps hardware config with runtime overrides

#### download_manager.py
- **Observer pattern implementation**
- `download_game(game, observer)`: Start download in thread
- `_download_thread()`: Worker thread function
- `_extract_archive()`: Extract zip/tar files
- Thread-safe progress updates

### Service Layer

#### input_handler.py
- **Layered input mapping**
- `__init__(hw_config)`: Load mapping hierarchy
- `set_game_context(game_id)`: Enable per-game mappings
- `is_action_pressed(action, events)`: Check if action triggered
- `save_mapping(action, keys, scope)`: Persist custom mappings

#### file_ops.py
- **pathlib-based file operations**
- `ensure_directory(path)`: Create directory if not exists
- `copy_file(src, dst)`: Safe file copying
- `move_file(src, dst)`: Safe file moving
- `delete_file(path)`: Safe file deletion
- All operations use pathlib.Path

#### process_launcher.py
- **Game launching**
- `launch_game(game, hw_config)`: Launch game process
- `_run_pre_commands()`: Execute pre-launch commands
- `_run_post_commands()`: Execute post-launch commands
- `_build_environment()`: Build environment variables

#### network.py
- **HTTP operations**
- `download_file(url, dest, progress_callback)`: Download with progress
- `check_url(url)`: Verify URL accessibility
- `get_file_size(url)`: Get remote file size
- Timeout and retry handling

### Core Layer

#### application.py
- **Main orchestrator**
- `__init__()`: Initialize all components
- `run()`: Main application loop
- `_initialize_pygame()`: Setup pygame
- `_initialize_components()`: Create managers
- `_shutdown()`: Cleanup on exit

#### state_manager.py
- **State machine**
- `change_state(name)`: Transition to new state
- `push_state(name)`: Push overlay state
- `pop_state()`: Return to previous state
- `update(dt)`, `handle_events()`, `render()`: Delegate to current state

#### game_loop.py
- **Main loop wrapper**
- `run(state_manager, clock, target_fps)`: Execute game loop
- Handle events, update, render, flip
- FPS limiting and delta time calculation

### State Layer

#### base_state.py
- **Abstract base class**
- `on_enter(previous_state)`: State initialization
- `on_exit()`: State cleanup
- `update(dt)`: Logic update
- `handle_events(events)`: Event processing
- `render(surface)`: Rendering

#### Concrete States
- **menu_state.py**: Main menu navigation
- **game_list_state.py**: Browse game library
- **download_state.py**: Download management
- **settings_state.py**: Configuration UI
- **playing_state.py**: Game execution wrapper

### View Layer

#### base_view.py
- **Abstract view base**
- `render(surface)`: Main render method
- `_load_theme()`: Load theme colors/fonts
- Helper methods for common rendering

#### Concrete Views
- **menu_view.py**: Main menu UI
- **game_list_view.py**: Game grid/list display
- **download_view.py**: Download progress UI
- **settings_view.py**: Settings interface

#### Widgets
- **button.py**: Clickable button
- **list.py**: Scrollable list
- **scrollbar.py**: Scrollbar indicator
- **progress_bar.py**: Progress indication
- **grid.py**: Grid layout
- **game_card.py**: Game information card

## Configuration File Structure

### Device Configurations
```json
{
  "device_type": "anbernic",
  "display": {
    "resolution": "auto",
    "fullscreen": true,
    "fps_target": 60
  },
  "input": {
    "hide_cursor": true
  },
  "paths": {
    "games": "/roms/ports",
    "data": "~/.local/share/sbc-man"
  }
}
```

### Input Mappings
```json
{
  "confirm": ["BUTTON_A", "BUTTON_SOUTH", "RETURN"],
  "cancel": ["BUTTON_B", "BUTTON_EAST", "ESCAPE"],
  "menu": ["BUTTON_START", "ESCAPE"],
  "up": ["DPAD_UP", "UP"],
  "down": ["DPAD_DOWN", "DOWN"],
  "left": ["DPAD_LEFT", "LEFT"],
  "right": ["DPAD_RIGHT", "RIGHT"]
}
```

## Error Handling Strategy

### Principles
1. **Never crash**: Always provide fallback
2. **Log everything**: Use logging module
3. **Inform user**: Show error messages in UI when appropriate
4. **Degrade gracefully**: Reduce functionality rather than fail
5. **Maintain data integrity**: Never corrupt save files

### Error Categories
- **Hardware Detection Failures**: Fallback to desktop/standard_linux
- **Configuration Errors**: Use default values
- **Network Errors**: Show retry option
- **File System Errors**: Check permissions, show error
- **Game Launch Errors**: Log and return to menu

## Testing Implementation Plan

### Unit Tests Structure
```
tests/unit/
├── test_hardware_detection.py    # Device/OS detection
├── test_config_loader.py          # Config merging
├── test_models.py                 # Game, GameLibrary
├── test_input_handler.py          # Input mapping resolution
├── test_file_ops.py               # File operations
├── test_game_library.py           # Library management
└── test_download_manager.py       # Download logic
```

### Integration Tests Structure
```
tests/integration/
├── test_state_transitions.py     # State machine flow
├── test_download_flow.py          # End-to-end download
└── test_game_launch.py            # Game launching
```

### Test Fixtures (conftest.py)
- `mock_hw_config`: Minimal hardware configuration
- `mock_game_library`: Sample games
- `tmp_config_dir`: Temporary config directory
- `tmp_data_dir`: Temporary data directory
- `headless_pygame`: Pygame with dummy driver

## Dependencies and Tools

### Runtime Dependencies
- **pygame-ce >= 2.1.0**: UI framework (NOT standard pygame)
- **requests >= 2.28.0**: HTTP client
- **Pillow >= 9.0.0**: Image processing (optional)

### Development Dependencies
- **coverage >= 7.0.0**: Coverage reporting
- **black >= 22.0.0**: Code formatter
- **flake8 >= 4.0.0**: Linter
- **mypy >= 0.950**: Type checker

### Build Tools
- **pyproject.toml**: Modern Python packaging
- **setuptools**: Package building
- **wheel**: Binary distribution

## Implementation Phases Summary

### Phase 2: Scaffolding (Next)
- Create directory structure
- Generate empty modules with docstrings
- Create __init__.py files
- Setup pyproject.toml
- Create basic README

### Phase 3: Core Implementation
- Hardware layer (detector, prober, config_loader)
- Core layer (application, state_manager, game_loop)
- Models (game, game_library, config_manager)
- Unit tests for each

### Phase 4: Services and Views
- Services (input_handler, file_ops, network, process_launcher)
- Views and widgets
- States (base + concrete)
- Unit and integration tests

### Phase 5: Download and Install
- DownloadManager with observer pattern
- Archive extraction
- Installation flow
- Integration tests

### Phase 6: Polish and Documentation
- README with usage examples
- Configuration examples
- Testing documentation
- Linting and type checking

### Phase 7: Final Report
- Implementation summary
- Test coverage report
- Known limitations
- Future enhancements

### Phase 8: Pull Request
- Create feature branch
- Commit all changes
- Push to repository
- Create pull request

## Ready for Phase 2: Scaffolding

All architectural decisions are documented. The implementation approach is clear and follows the documentation specifications exactly. Ready to generate the complete package scaffolding.