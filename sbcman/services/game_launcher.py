# Unfinished example code for launching a game.

# game_launcher.py
import multiprocessing
import importlib
import traceback

class GameManager:
    def __init__(self):
        self.games = {
            'snake': 'games.snake',
            'pong': 'games.pong',
            'tetris': 'games.tetris'
        }
    
    def launch_game(self, game_name):
        if game_name not in self.games:
            print(f"Game '{game_name}' not found")
            return
        
        module_name = self.games[game_name]
        
        # Create isolated process
        process = multiprocessing.Process(
            target=self._run_game,
            args=(module_name,)
        )
        
        process.start()
        process.join()  # Wait for game to finish
        
        if process.exitcode != 0:
            print(f"Game exited with code: {process.exitcode}")
    
    @staticmethod
    def _run_game(module_name):
        try:
            game = importlib.import_module(module_name)
            game.main()
        except Exception:
            traceback.print_exc()
            sys.exit(1)
