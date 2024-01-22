# downloads max 1080p
import os
from dotenv import load_dotenv
from pytube import Playlist

load_dotenv()

# SAVE_PATH = os.path.join(os.getcwd(), 'media\\video_templates')
SAVE_PATH = 'C:/Users/rizzu/Downloads/test'

# TODO url enconding in .env
LINK=os.getenv('PLAYLIST_LINK')

try:
    yt = Playlist(LINK)
except:
    raise Exception('Problem collectiing the playlist')

failed_videos = []

# ['FsiTKTQ8P3A', 'MVWyEcaJwQY', 'mARyMmqfrBk', 'ptpdxSJ8kkU', 'p4gMf_GldOI', 'SHwEuDLIv1s', 'urcNj-cB5W0', 'nbLIXUEbULY', 'ysTSCfX4w58', 'ALu-y-8BuTc', 'fV2NrHOgGZg', 'OoP7csWPmWo', 'GXnC1kTgJlY', 'hZyjsJJ51kQ', '8yL4OhRCBnI', 'UrBngKN-1m0', 'OEDkzvLnPgY', 'iTs4YaWVfuc', 'DWS_WaB9bFU', '1_jgsUzOVMI', 'KI5pW5qgnD8', 'FRbjsytMZqk', '9yq_geptRfU', 'BYeBJHki1oI', 'GVWVfFfvEL8', 'whKKC47cCTw', 'VS3D8bgYhf4', 'gwwXdCWAZ9I', '-OeSQhnSwl4', 'fAJVaKj0ROY', 'ec-XjVGascc', 'gwc9czYyt6E', 'P2rEJGU2MBo', 'fVP7iLCJ3RQ', 'I648KQpt3k8', 'YZv_mWIezYQ', 'U_rhAsMQvTE', 'm3_PH3tBAnA', 'leJ4yOTAki0', '4ohB5xMGgvI', '56f_AOjOI60', '_XGl6I30c4g', 'PK7EuFCMn5I', 'ZkNIJJZcRkY']

for video in yt.videos:
    filename = f'{len(os.listdir(SAVE_PATH))}.mp4'
    
    # 720p
    # video.streams.get_highest_resolution().download(SAVE_PATH, filename=filename)

    try:
        video.streams.\
            filter(type='video', progressive=False, file_extension='mp4').\
            order_by('resolution').\
            desc().\
            first().\
            download(SAVE_PATH, filename=filename)
    except:
        failed_videos.append(video.video_id)
        print('Error downloading the file')

print(failed_videos)
