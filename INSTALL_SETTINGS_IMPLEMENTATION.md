# Install Settings Screen Implementation

## Overview
This implementation adds a new "Install Settings" screen to the SBC-Man game launcher, allowing users to configure installation-related options.

## Changes Made

### 1. New File: `sbcman/states/install_settings_state.py`
- Created a new state class `InstallSettingsState` that manages the install settings screen
- Implements adaptive layout support similar to other settings screens
- Provides the following configurable options:
  - **Install as pip package**: Boolean toggle (ON/OFF)
  - **Add Portmaster entry**: Boolean toggle (ON/OFF)
  - **Portmaster base dir**: Directory selection with browse button
  - **Portmaster image dir**: Directory selection with browse button

### 2. Modified File: `sbcman/states/settings_state.py`
- Updated `_select_option()` method to navigate to the new Install Settings screen
- Added navigation logic for "Install Settings" menu option

### 3. Modified File: `sbcman/core/state_manager.py`
- Registered the new `InstallSettingsState` in the state manager
- Added import and initialization of the new state

### 4. New Test File: `tests/unit/test_install_settings_state.py`
- Comprehensive unit tests for the new Install Settings state
- Tests cover initialization, state transitions, settings modification, and rendering

### 5. Modified Test File: `tests/unit/test_settings_state.py`
- Updated existing tests to work with the new implementation

## Implementation Details

### Data Persistence
The installation settings are persisted using the existing `ConfigManager` infrastructure:
- Settings are stored in the `config.json` file
- Uses dot notation for nested keys (e.g., `install.install_as_pip`)
- Default values are:
  - `install_as_pip`: `False`
  - `add_portmaster_entry`: `False`
  - `portmaster_base_dir`: `~/portmaster`
  - `portmaster_image_dir`: `~/portmaster/images`

### Directory Browser
The directory selection feature uses `tkinter.filedialog`:
- Temporarily hides the pygame window
- Opens a native directory browser dialog
- Validates the selected directory exists and is accessible
- Restores the pygame window after selection
- Handles errors gracefully with appropriate logging

### User Interface
The screen follows the existing design patterns:
- Adaptive layout that responds to screen size
- Scrollable list for navigation
- Clear visual indicators for toggle states (ON/OFF)
- Path truncation for long directory paths
- Consistent styling with other settings screens

### Navigation
- Access from main Settings menu by selecting "Install Settings"
- Return to main Settings menu by selecting "Back to Settings"
- Settings are automatically saved when returning to the main settings menu

### Input Handling
- **Up/Down**: Navigate through settings options
- **A/Confirm**: Toggle boolean options or browse directories
- **B/Cancel**: Return to main settings menu
- **ESC**: Return to main settings menu

## Configuration Keys

The following configuration keys are used (stored in `config.json`):

```json
{
  "install": {
    "install_as_pip": false,
    "add_portmaster_entry": false,
    "portmaster_base_dir": "/home/user/portmaster",
    "portmaster_image_dir": "/home/user/portmaster/images"
  }
}
```

## Testing

All unit tests pass successfully:
```bash
# Test the install settings state
python -m unittest tests.unit.test_install_settings_state

# Test the updated settings state
python -m unittest tests.unit.test_settings_state
```

## Code Style Compliance

The implementation follows the project's coding standards:
- Custom classes and data structures (no dictionaries for main data)
- Uses `pathlib` instead of `os.path`
- Imports modules, not classes
- Minimal methods with logical sections factored out
- Classes kept under 400 lines
- Single-line docstrings for simple methods
- Comprehensive logging for debugging

## Error Handling

The implementation includes robust error handling:
- Directory validation (existence and type checks)
- Graceful handling of tkinter errors
- Proper cleanup of pygame window state
- Logging of all errors and warnings
- Fallback to home directory if initial path doesn't exist

## Future Enhancements

Potential improvements that could be made:
- Add validation for Portmaster directory structure
- Implement custom file/directory browser in pygame
- Add tooltips or help text for each setting
- Support for keyboard input for directory paths
- Add reset to defaults option
- Implement settings presets

## Notes

- The directory browser uses `tkinter` which is included with Python by default
- The implementation preserves all commented-out elements in the original code
- All existing functionality remains intact
- The changes are backward compatible with existing configurations