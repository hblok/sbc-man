# Path Management Refactoring Plan

## Current State Analysis
- AppPaths class exists in `src/hardware/paths.py` 
- Multiple files use hardcoded "~" paths and `paths.get()` calls
- Need to centralize all path management and use constructor injection

## Step-by-Step Implementation

### 1. Analyze Current Usage
- Find all files using "~" expansion
- Find all files using `paths.get()` 
- Identify all hardcoded paths

### 2. Update AppPaths Class
- Ensure AppPaths handles all identified paths
- Add any missing path methods
- Verify pathlib usage only

### 3. Refactor Component Classes
- Update Application class to inject AppPaths
- Update ConfigManager to accept AppPaths
- Update GameLibrary to accept AppPaths  
- Update InputHandler to accept AppPaths
- Update DownloadManager to accept AppPaths
- Update StateManager to accept and pass AppPaths

### 4. Clean Up Documentation
- Remove verbose docstrings from simple methods
- Convert to single-line docstrings where appropriate
- Keep docstrings for complex logic only

### 5. Update Tests
- Mock AppPaths in unit tests
- Update test constructors to pass AppPaths
- Ensure all tests pass

### 6. Create GitHub Pull Request
- Commit all changes
- Push branch
- Create PR with description

## Files to Modify
- `src/hardware/paths.py` - Enhance AppPaths
- `src/core/application.py` - Inject AppPaths to components
- `src/core/state_manager.py` - Accept and pass AppPaths
- `src/models/config_manager.py` - Accept AppPaths
- `src/models/game_library.py` - Accept AppPaths
- `src/services/input_handler.py` - Accept AppPaths
- `src/models/download_manager.py` - Accept AppPaths
- All test files - Update for AppPaths injection

## Success Criteria
- All hardcoded paths replaced with AppPaths
- All "~" expansion removed
- Constructor injection used everywhere
- All tests pass
- Documentation cleaned up
- Pull request created