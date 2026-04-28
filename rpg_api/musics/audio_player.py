
from pathlib import Path
from just_playback import Playback

BASE_DIR = Path(__file__).resolve().parent

path_musics = Path( BASE_DIR,  'Animals_House_Of_The_Rising_Sun1.wav')
music = Playback()

music.load_file(str(path_musics))