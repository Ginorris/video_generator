# only downloads 720p, may throw connection error
import os
from dotenv import load_dotenv
from pytube import Playlist

load_dotenv()

SAVE_PATH = os.path.join(os.getcwd(), 'media\\video_templates')
# TODO url enconding in .env
LINK=os.getenv('PLAYLIST_LINK')

yt = Playlist(LINK)
for video in yt.videos:
    video.streams.\
        filter(type='video', progressive=True, file_extension='mp4').\
        order_by('resolution').\
        desc().\
        first().\
        download(SAVE_PATH)

# TODO rename files