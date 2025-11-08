import pathlib


class AppPaths:
    
    def __init__(self, base_dir: pathlib.Path | None = None):
        if base_dir is None:
            base_dir = pathlib.Path.home() / ".game_manager"
        
        self._base_dir = base_dir
        self._temp_dir = pathlib.Path("/tmp") / "game_manager"
    
    @property
    def home(self) -> pathlib.Path:
        return pathlib.Path.home()
    
    @property
    def temp_dir(self) -> pathlib.Path:
        return self._temp_dir
    
    @property
    def config_dir(self) -> pathlib.Path:
        return self._base_dir / "config"
    
    @property
    def config_devices(self) -> pathlib.Path:
        return self.config_dir / "devices"
    
    @property
    def config_os(self) -> pathlib.Path:
        return self.config_dir / "os"
    
    @property
    def config_input_mappings(self) -> pathlib.Path:
        return self.config_dir / "input_mappings"
    
    @property
    def data_dir(self) -> pathlib.Path:
        return self._base_dir / "data"
    
    @property
    def data_games_dir(self) -> pathlib.Path:
        return self.data_dir / "games"
    
    @property
    def games_installed(self) -> pathlib.Path:
        return self.data_games_dir / "installed.json"
    
    @property
    def games_available(self) -> pathlib.Path:
        return self.data_games_dir / "available.json"
    
    @property
    def games_file(self) -> pathlib.Path:
        """Main games database file"""
        return self.data_games_dir / "games.json"
    
    @property
    def config_file(self) -> pathlib.Path:
        return self.data_dir / "config.json"
    
    @property
    def input_mappings(self) -> pathlib.Path:
        """Alias for config_input_mappings for backward compatibility"""
        return self.config_input_mappings
    
    @property
    def input_overrides(self) -> pathlib.Path:
        """Directory for user input override configurations"""
        return self.data_dir / "input_overrides"
    
    @property
    def src_config_dir(self) -> pathlib.Path:
        """Source configuration directory (relative to source code)"""
        return pathlib.Path(__file__).parent.parent / "config"
    
    @property
    def games_dir(self) -> pathlib.Path:
        """Directory for installed games"""
        return self.home / "games"
    
    @property
    def downloads_dir(self) -> pathlib.Path:
        """Directory for game downloads"""
        return self.games_dir / "downloads"
