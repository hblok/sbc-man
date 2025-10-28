# Phase 1: Approach and Implementation Plan

## Documentation-to-Code Mapping

### Core Architecture Approach
Based on the documentation analysis, the system follows a 6-layer architecture with clear separation of concerns:

1. **Hardware Layer** - Device detection and abstraction
2. **Core Layer** - Application orchestration and state management  
3. **Service Layer** - Shared services (input, file ops, network)
4. **Model Layer** - Data models and business logic
5. **State Layer** - Application states and transitions
6. **View Layer** - UI rendering and user interaction

### Documentation Mapping Table

#### Core System Files
| Documentation File | Target Implementation | Key Requirements |
|-------------------|----------------------|------------------|
| `docs/code/package_main.txt` | `main.py` | Zero-logic entry point, imports compat_sdl and application |
| `docs/core_arch.txt` | Overall architecture | 6-layer separation, pygame-ce, Linux-first |
| `docs/other/sequence_startup.txt` | `src/core/application.py` | Hardware detection → config loading → pygame init → component init |
| `docs/code/package_core.txt` | Core package structure | Application orchestrator, state manager, game loop |

#### Hardware Layer Mapping
| Documentation File | Target Implementation | Key Features |
|-------------------|----------------------|-------------|
| `class_hardware_detector.txt` | `src/hardware/detector.py` | Static methods, device/OS detection, fallbacks |
| `class_hardware_prober.txt` | `src/hardware/prober.py` | Display/input/storage/CPU probing, no hard-coded values |
| `class_hardware_config_loader.txt` | `src/hardware/config_loader.py` | 4-layer config merge, path expansion |
| Hardware docs | `src/hardware/compat_sdl.py` | SDL compatibility for main.py import |

#### Model Layer Mapping
| Documentation File | Target Implementation | Key Features |
|-------------------|----------------------|-------------|
| `class_models_game.txt` | `src/models/game.py` | Game data model, serialization |
| `class_models_game_library.txt` | `src/models/game_library.py` | CRUD operations, library management |
| `class_models_config_manager.txt` | `src/models/config_manager.py` | Runtime configuration management |
| `class_models_download_manager.txt` | `src/models/download_manager.py` | Observer pattern, threading, progress tracking |

#### Service Layer Mapping
| Documentation File | Target Implementation | Key Features |
|-------------------|----------------------|-------------|
| `class_services_input_handler.txt` | `src/services/input_handler.py` | Layered mappings, per-game overrides |
| `class_services_file_ops.txt` | `src/services/file_ops.py` | pathlib-based file operations |
| `class_services_network.txt` | `src/services/network.py` | HTTPS requests, timeout handling |
| `class_services_process_launcher.txt` | `src/services/process_launcher.py` | Game launching, pre/post commands |

#### State Layer Mapping
| Documentation File | Target Implementation | Key Features |
|-------------------|----------------------|-------------|
| `class_states_base_state.txt` | `src/states/base_state.py` | Base state interface, lifecycle methods |
| `class_states_menu_state.txt` | `src/states/menu_state.py` | Main menu state implementation |
| `class_states_game_list_state.txt` | `src/states/game_list_state.py` | Game browsing functionality |
| `class_states_download_state.txt` | `src/states/download_state.py` | Download management UI |
| `class_states_settings_state.txt` | `src/states/settings_state.py` | Settings configuration |
| `class_states_playing_state.txt` | `src/states/playing_state.py` | Game playing state |
| `class_state_manager.txt` | `src/core/state_manager.py` | State machine, transitions |

#### View Layer Mapping
| Documentation File | Target Implementation | Key Features |
|-------------------|----------------------|-------------|
| `class_views_base_view.txt` | `src/views/base_view.py` | Base view interface |
| View class files | `src/views/` individual views | Menu, game list, download, settings views |
| Widget class files | `src/views/widgets/` | Button, list, scrollbar, progress bar, grid, game card |

#### Configuration System Mapping
| Documentation File | Target Implementation | Key Features |
|-------------------|----------------------|-------------|
| `config_hierarchy.txt` | Config loading logic | 4-layer merge hierarchy |
| `config_devices.txt` | `src/config/devices/` | Device-specific JSON configs |
| `config_os_types.txt` | `src/config/os_types/` | OS-specific JSON configs |
| `config_input_mappings.txt` | `src/config/input_mappings/` | Input mapping JSON files |

### Final Project Directory Structure

```
sbc-man/
├── main.py                         # Entry point: compat_sdl + application import
├── README.md
├── LICENSE
├── pyproject.toml                   # Project configuration and dependencies
├── src/                            # Python package root
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── application.py          # Startup lifecycle orchestrator
│   │   ├── state_manager.py        # State machine implementation
│   │   └── game_loop.py            # Main loop wrapper
│   ├── hardware/
│   │   ├── __init__.py
│   │   ├── detector.py             # Device/OS detection
│   │   ├── prober.py               # Hardware capability probing
│   │   ├── config_loader.py        # Configuration merging
│   │   └── compat_sdl.py           # SDL compatibility (imported by main.py)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── game.py                 # Game data model
│   │   ├── game_library.py         # Game library management
│   │   ├── config_manager.py       # Runtime configuration
│   │   └── download_manager.py     # Download with observer pattern
│   ├── services/
│   │   ├── __init__.py
│   │   ├── input_handler.py        # Layered input mapping
│   │   ├── file_ops.py             # File operations
│   │   ├── process_launcher.py     # Game launching
│   │   └── network.py              # Network operations
│   ├── states/
│   │   ├── __init__.py
│   │   ├── base_state.py           # Base state interface
│   │   ├── menu_state.py           # Main menu
│   │   ├── game_list_state.py      # Game library browsing
│   │   ├── download_state.py       # Download management
│   │   ├── settings_state.py       # Settings configuration
│   │   └── playing_state.py        # Game playing
│   ├── views/
│   │   ├── __init__.py
│   │   ├── base_view.py            # Base view interface
│   │   ├── menu_view.py            # Menu UI
│   │   ├── game_list_view.py       # Game list UI
│   │   ├── download_view.py        # Download progress UI
│   │   ├── settings_view.py        # Settings UI
│   │   └── widgets/
│   │       ├── __init__.py
│   │       ├── button.py           # Button widget
│   │       ├── list.py             # List widget
│   │       ├── scrollbar.py        # Scrollbar widget
│   │       ├── progress_bar.py     # Progress indication
│   │       ├── grid.py             # Grid layout
│   │       └── game_card.py        # Game information card
│   ├── config/                     # Seed configuration
│   │   ├── devices/
│   │   │   ├── default.json
│   │   │   ├── anbernic.json
│   │   │   ├── miyoo.json
│   │   │   └── retroid.json
│   │   ├── os_types/
│   │   │   ├── arkos.json
│   │   │   ├── jelos.json
│   │   │   ├── batocera.json
│   │   │   ├── android.json
│   │   │   └── standard_linux.json
│   │   └── input_mappings/
│   │       ├── default.json
│   │       ├── anbernic.json
│   │       ├── miyoo.json
│   │       └── retroid.json
│   └── assets/
│       ├── fonts/
│       ├── icons/
│       └── themes/
├── tests/
│   ├── conftest.py                 # Test configuration and fixtures
│   ├── unit/
│   │   ├── test_models.py          # Model layer tests
│   │   ├── test_hardware_detection.py # Hardware detection tests
│   │   ├── test_config_loader.py   # Configuration loading tests
│   │   ├── test_input_handler.py   # Input mapping tests
│   │   ├── test_file_ops.py        # File operations tests
│   │   ├── test_game_library.py    # Game library tests
│   │   └── test_download_manager.py # Download manager tests
│   └── integration/
│       ├── test_state_transitions.py # State transition tests
│       ├── test_download_flow.py   # Download flow tests
│       └── test_game_launch.py     # Game launch tests
└── .github/
    └── workflows/
        └── ci.yml                  # CI pipeline
```

### Implementation Strategy Notes

#### Key Architecture Decisions
1. **Zero-Logic Entry Point**: main.py only imports compat_sdl and application, following docs exactly
2. **Hardware-First Approach**: Hardware detection and configuration loading happens before pygame init
3. **Layered Configuration**: 4-layer merge hierarchy (default → device → OS → user)
4. **Observer Pattern**: DownloadManager uses observer pattern for non-blocking UI updates
5. **State Pattern**: Clean state transitions with lifecycle management
6. **Pathlib Usage**: All file operations use pathlib.Path, no os.path

#### Critical Implementation Requirements
- **pygame-ce**: Use pygame-ce library, not standard pygame
- **Linux-First**: Target Linux handhelds and Android-based Linux
- **Headless Testing**: SDL_VIDEODRIVER=dummy for test environment
- **Input Mapping Hierarchy**: default → device → user → per-game overrides
- **Error Handling**: Graceful degradation, never crash
- **Thread Safety**: DownloadManager with threading, UI stays responsive

#### Testing Strategy
- **unittest Framework**: Use python unittest with fixtures and mocks
- **85% Coverage Target**: 100% on models and config loader
- **Headless Testing**: Mock pygame, use SDL_VIDEODRIVER=dummy
- **Integration Tests**: Startup flow, download flow, game launch flow

## Ready for Phase 2: Scaffolding

The documentation is complete and comprehensive. All 66 files are present and provide detailed specifications for every component. The mapping above shows exactly how each documentation file maps to the implementation.

Next phase: Generate package scaffolding with empty modules and docstrings.