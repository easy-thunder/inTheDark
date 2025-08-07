# game/utils.py
import os, sys

def get_assets_dir() -> str:
    """
    Returns absolute path to the 'assets' folder in both dev and PyInstaller builds.
    """
    # PyInstaller: _MEIPASS points to the extracted onedir/_internal dir
    if hasattr(sys, "_MEIPASS") and sys._MEIPASS:
        # We copy assets to: dist/run_game/_internal/assets  (PyInstaller already does with --add-data)
        return os.path.join(sys._MEIPASS, "assets")

    # Dev: repo_root/assets  (this file is repo_root/game/utils.py)
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(repo_root, "assets")

ASSETS_DIR = get_assets_dir()

def asset_path(*parts: str) -> str:
    """Convenience helper: asset_path('creatures', 'zombie', 'walk.png')"""
    return os.path.join(ASSETS_DIR, *parts)
