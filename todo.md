# Test Suite Refactoring - Split Combined Test Classes

## Files to Refactor

### Unit Tests (3 files need splitting):
- [x] `tests/unit/test_models.py` - Contains: TestGame, TestGameLibrary, TestConfigManager → Split into 3 files
- [x] `tests/unit/test_hardware_detection.py` - Contains: TestHardwareDetector, TestHardwareProber → Split into 2 files
- [x] `tests/unit/test_states.py` - Contains: TestBaseState, TestMenuState, TestGameListState, TestPlayingState, TestSettingsState → Split into 5 files

### Unit Tests (already correct - 1 TestCase per file):
- [x] `tests/unit/test_config_loader.py` - TestConfigLoader only
- [x] `tests/unit/test_download_manager.py` - TestDownloadManager only (TestDownloadObserver is not a TestCase)
- [x] `tests/unit/test_download_state.py` - TestDownloadState only
- [x] `tests/unit/test_input_handler.py` - TestInputHandler only
- [x] `tests/unit/test_network_service.py` - TestNetworkService only

### Integration Tests (already correct - 1 TestCase per file):
- [x] `tests/integration/test_download_install_flow.py` - TestDownloadInstallFlow only
- [x] `tests/integration/test_game_launch_flow.py` - TestGameLaunchFlow only
- [x] `tests/integration/test_startup_flow.py` - TestStartupFlow only
- [x] `tests/integration/test_state_transition_flow.py` - TestStateTransitionFlow only

## Refactoring Tasks
- [x] Create feature branch `refactor/split-test-classes`
- [x] Split test_models.py into 3 separate files
- [x] Split test_hardware_detection.py into 2 separate files  
- [x] Split test_states.py into 5 separate files
- [x] Update BUILD files to reflect new test module structure
- [x] Run individual tests to verify functionality
- [ ] Run complete test suite with bazel test
- [ ] Commit changes after each successful split
- [ ] Create Pull Request

## Summary
- Total test files to split: 3
- New test files to create: 10 (3 + 2 + 5)
- TestCase classes to relocate: 10

## Files Created
From test_models.py:
- test_game.py (TestGame - 4 tests)
- test_game_library.py (TestGameLibrary - 6 tests)
- test_config_manager.py (TestConfigManager - 6 tests)

From test_hardware_detection.py:
- test_hardware_detector.py (TestHardwareDetector - 6 tests)
- test_hardware_prober.py (TestHardwareProber - 4 tests)

From test_states.py:
- test_base_state.py (TestBaseState - 1 test)
- test_menu_state.py (TestMenuState - 8 tests)
- test_game_list_state.py (TestGameListState - 7 tests)
- test_playing_state.py (TestPlayingState - 6 tests)
- test_settings_state.py (TestSettingsState - 6 tests)

## Current Test Structure
Before: 8 unit test files
After: 15 unit test files

Total tests preserved: 48 individual test methods