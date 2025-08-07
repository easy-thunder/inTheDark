# run_game.py
import os, sys
from pathlib import Path

def set_cwd_for_pyinstaller():
    """
    Make sure cwd is the folder that *actually contains* 'assets/'.
    Works for:
      - dev runs
      - PyInstaller onedir (dist/run_game)
      - weird macOS onedir cases where cwd starts in _internal
      - onefile fallback to _MEIPASS
    """
    candidates = []

    # 1) Folder next to the executable (typical onedir)
    exe_dir = Path(getattr(sys, "executable", ".")).resolve().parent
    candidates.append(exe_dir)

    # 2) Parent of that (covers when the real work dir is _internal)
    candidates.append(exe_dir.parent)

    # 3) _MEIPASS (onefile extraction dir)
    if hasattr(sys, "_MEIPASS"):
        candidates.append(Path(sys._MEIPASS).resolve())

    # 4) Current dir (dev)
    candidates.append(Path.cwd())

    for c in candidates:
        if (c / "assets").exists():
            os.chdir(c)
            # Optional: print for sanity
            print("[cwd fix] using:", c)
            return

    # If we get here, we didn't find assets anywhere obvious.
    # Leave cwd as-is, but warn.
    print("[cwd fix] WARNING: couldn't find 'assets/' in any candidate:", candidates)

def main():
    set_cwd_for_pyinstaller()
    print("[run_game] cwd:", os.getcwd())
    print("[run_game] assets exists?:", Path("assets").exists())

    from game.main import main as game_main
    game_main()

if __name__ == "__main__":
    print("[run_game] starting…")
    main()
