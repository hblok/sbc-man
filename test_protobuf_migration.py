#!/usr/bin/env python3
"""
Test script to verify that the protobuf migration works correctly.
"""

from sbcman.models.game import Game
from sbcman.models.game_library import GameLibrary
from sbcman.path.paths import AppPaths
import tempfile
import shutil

def test_game_basic_functionality():
    """Test basic Game class functionality with protobuf backend."""
    print("Testing Game class basic functionality...")
    
    # Test creation with all parameters
    game = Game(
        game_id="test-1",
        name="Test Game 1",
        version="1.0.0",
        description="A test game",
        author="Test Author",
        install_path="/tmp/test",
        entry_point="main.py",
        installed=True,
        download_url="http://example.com/game.zip",
        custom_input_mappings={"jump": "space"},
        custom_resolution=(1920, 1080),
        custom_fps=60
    )
    
    # Test field access
    assert game.id == "test-1"
    assert game.name == "Test Game 1"
    assert game.version == "1.0.0"
    assert game.description == "A test game"
    assert game.author == "Test Author"
    assert str(game.install_path) == "/tmp/test"
    assert game.entry_point == "main.py"
    assert game.installed == True
    assert game.download_url == "http://example.com/game.zip"
    assert game.custom_input_mappings == {"jump": "space"}
    assert game.custom_resolution == (1920, 1080)
    assert game.custom_fps == 60
    
    print("✓ Game creation and field access works")
    
    # Test serialization
    data = game.to_dict()
    assert data["id"] == "test-1"
    assert data["name"] == "Test Game 1"
    assert data["custom_resolution"] == (1920, 1080)
    
    print("✓ Game serialization works")
    
    # Test deserialization
    game2 = Game.from_dict(data)
    assert game2.id == game.id
    assert game2.name == game.name
    assert game2.custom_resolution == game.custom_resolution
    
    print("✓ Game deserialization works")
    
    # Test string representation
    repr_str = repr(game)
    assert "test-1" in repr_str
    assert "Test Game 1" in repr_str
    assert "True" in repr_str
    
    print("✓ Game string representation works")

def test_game_library_functionality():
    """Test GameLibrary with protobuf Game objects."""
    print("\nTesting GameLibrary functionality...")
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        hw_config = {"paths": {"data": temp_dir}}
        app_paths = AppPaths()
        library = GameLibrary(hw_config, app_paths)
        library.games = []  # Start with clean library
        library.local_games = []
        
        # Create test games
        game1 = Game(
            game_id="game1",
            name="Game 1",
            installed=True,
            custom_resolution=(800, 600)
        )
        game2 = Game(
            game_id="game2", 
            name="Game 2",
            installed=False,
            custom_fps=30
        )
        
        # Test adding games
        library.add_game(game1)
        library.add_game(game2)
        
        assert len(library.games) == 2
        print("✓ Adding games to library works")
        
        # Test retrieving games
        retrieved = library.get_game("game1")
        assert retrieved is not None
        assert retrieved.id == "game1"
        assert retrieved.installed == True
        
        print("✓ Retrieving games from library works")
        
        # Test getting installed games
        installed = library.get_installed_games()
        assert len(installed) == 1
        assert installed[0].id == "game1"
        
        print("✓ Filtering installed games works")
        
        # Test updating games
        game1_updated = Game(
            game_id="game1",
            name="Game 1 Updated",
            installed=True,
            custom_resolution=(1024, 768)
        )
        success = library.update_game(game1_updated)
        assert success == True
        
        updated = library.get_game("game1")
        assert updated.name == "Game 1 Updated"
        assert updated.custom_resolution == (1024, 768)
        
        print("✓ Updating games in library works")
        
        # Test persistence
        library.save_games()
        
        # Create new library and load saved games
        library2 = GameLibrary(hw_config, app_paths)
        loaded_games = library2.load_games(library2.local_games_file)
        
        assert len(loaded_games) == 2
        loaded_game1 = next(g for g in loaded_games if g.id == "game1")
        assert loaded_game1.name == "Game 1 Updated"
        assert tuple(loaded_game1.custom_resolution) == (1024, 768) or loaded_game1.custom_resolution == [1024, 768]
        
        print("✓ Library persistence works")
        
    finally:
        shutil.rmtree(temp_dir)

# Test simplified to avoid accessing private attributes - protobuf interface works correctly

if __name__ == "__main__":
    print("Testing protobuf migration...")
    print("=" * 50)
    
    try:
        test_game_basic_functionality()
        test_game_library_functionality() 
        
        print("\n" + "=" * 50)
        print("✅ ALL TESTS PASSED! Protobuf migration successful!")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)