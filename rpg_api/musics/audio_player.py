
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
path_musics = Path(BASE_DIR, 'Animals_House_Of_The_Rising_Sun1.wav')

class DummyPlayback:
    def __init__(self):
        self.active = False
        self.volume = 1.0

    def play(self):
        self.active = True

    def stop(self):
        self.active = False

    def pause(self):
        self.active = False

    def resume(self):
        self.active = True

    def load_file(self, path):
        pass

# Check if we should use dummy player (tests, headless, or audio disabled)
if os.environ.get("TEST_VERSION") == "True" or os.environ.get("DISABLE_AUDIO") == "1" or "pytest" in sys.modules or "PYTEST_CURRENT_TEST" in os.environ:
    music = DummyPlayback()
else:
    try:
        from just_playback import Playback
        music = Playback()
        if path_musics.exists():
            music.load_file(str(path_musics))
    except Exception:
        music = DummyPlayback()