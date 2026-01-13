# Refactoring Analysis

## Current State Analysis

### updater.py - install_update() method
The `install_update()` method in `updater.py` contains:
1. **Pip installation logic** (`_install_with_pip()` method):
   - Finds pip command (pip or pip3)
   - Checks pip version for --break-system-packages support
   - Builds pip install command with appropriate flags
   - Executes pip install with timeout and error handling
   
2. **Manual extraction fallback** (`_install_with_extraction()` method):
   - Extracts wheel as zip file to site-packages
   - Handles permission errors
   - Gets site-packages path dynamically

### download_manager.py - _extract_archive() method
The `_extract_archive()` method currently handles:
- `.zip` files using zipfile module
- `.tar` files (including .tar.gz, .tar.bz2) using tarfile module
- Security validation for both formats
- Does NOT handle `.whl` files

## Refactoring Plan

### 1. Create wheel_installer.py module
Location: `sbcman/services/wheel_installer.py`

This module will contain:
- `WheelInstaller` class with methods:
  - `install_wheel(wheel_path: Path) -> Tuple[bool, str]` - Main entry point
  - `_install_with_pip(wheel_path: Path) -> Tuple[bool, str]` - Pip installation
  - `_install_with_extraction(wheel_path: Path) -> Tuple[bool, str]` - Manual extraction fallback
  - `_find_pip_command() -> Optional[str]` - Find pip executable
  - `_check_pip_break_system_packages_support(pip_command: str) -> bool` - Check pip version
  - `_get_site_packages_path() -> Optional[Path]` - Get site-packages directory

### 2. Modify updater.py
Changes:
- Import the new `WheelInstaller` class
- Replace `install_update()` implementation to use `WheelInstaller`
- Remove `_install_with_pip()` and `_install_with_extraction()` methods
- Keep `_find_pip_command()`, `_check_pip_break_system_packages_support()`, and `_get_site_packages_path()` as they may be used elsewhere

Actually, after reviewing the code more carefully:
- Move ALL pip-related methods to `WheelInstaller`
- `install_update()` will instantiate `WheelInstaller` and call its methods

### 3. Enhance download_manager.py
Changes to `_extract_archive()` method:
- Add file extension detection at the beginning
- Route `.whl` files to `WheelInstaller`
- Keep existing `.zip` and `.tar` handling
- Add error handling for unsupported formats

## Implementation Details

### File Extension Routing Logic
```python
def _extract_archive(self, archive_path: Path, game: game_pb2.Game) -> Path:
    # Determine file type
    suffix = archive_path.suffix.lower()
    
    if suffix == '.whl':
        # Use wheel installer
        from sbcman.services.wheel_installer import WheelInstaller
        installer = WheelInstaller()
        success, message = installer.install_wheel(archive_path)
        if not success:
            raise Exception(f"Wheel installation failed: {message}")
        # Return appropriate path
        return self._get_wheel_install_path(archive_path)
    elif suffix == '.zip':
        # Existing zip handling
        ...
    elif suffix in ['.tar', '.gz', '.bz2', '.xz']:
        # Existing tar handling
        ...
    else:
        raise Exception(f"Unsupported archive format: {suffix}")
```

### Backward Compatibility
- `updater.py` will maintain the same public interface
- `install_update()` will continue to work as before
- Internal implementation changes are transparent to callers