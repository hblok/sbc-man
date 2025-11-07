# Path Management Refactoring Plan

## Phase 1: Analysis and Discovery ✅
- [x] Examine existing AppPaths class in src/hardware/paths.py
- [x] Find all hardcoded paths throughout the codebase
- [x] Identify all files that use "~" expansion or hardcoded paths
- [x] Analyze current dependency injection patterns

## Phase 2: Extend AppPaths Class ✅
- [x] Enhance AppPaths to handle all identified paths
- [x] Convert to use pathlib exclusively
- [x] Add proper home directory expansion handling
- [x] Add any missing path utility methods

## Phase 3: Refactor Code Under src/
- [ ] Update Application class to use AppPaths via constructor injection
- [ ] Update ConfigManager to use AppPaths via constructor injection
- [ ] Update DownloadManager to use AppPaths via constructor injection
- [ ] Update GameLibrary to use AppPaths via constructor injection
- [ ] Update InputHandler to use AppPaths via constructor injection
- [ ] Update StateManager to pass AppPaths to states
- [ ] Replace all hardcoded paths with AppPaths references
- [ ] Remove "~" expansion usage throughout codebase

## Phase 4: Clean Up Documentation
- [ ] Remove verbose docstrings from simple methods
- [ ] Convert to single-line docstrings where appropriate
- [ ] Remove obvious documentation for getters/setters
- [ ] Keep docstrings for complex logic and public APIs

## Phase 5: Update Tests
- [ ] Update all relevant tests for AppPaths injection
- [ ] Mock AppPaths in unit tests
- [ ] Ensure all existing tests pass
- [ ] Add tests for new AppPaths functionality

## Phase 6: Validation and PR Creation
- [ ] Run full test suite
- [ ] Verify all functionality preserved
- [ ] Create comprehensive commit
- [ ] Create pull request to main branch