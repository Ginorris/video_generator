# dont run, output video freezes in the firsts frames, managed in main.py
import os
from moviepy.editor import VideoFileClip

PATH = os.path.join(os.getcwd(), 'media\\video_templates')
VIDEOS = os.listdir(PATH)

for video in VIDEOS:
    new_filename = f'{VIDEOS.index(video)}.mp4'
    os.rename(os.path.join(PATH, video), os.path.join(PATH, new_filename))

    video_clip = VideoFileClip(os.path.join(PATH, new_filename))
    
    target_width = int(video_clip.size[1] * 9 / 16)
    x_center = (video_clip.size[0] - target_width) / 2
    video_clip = video_clip.crop(x1=x_center, x2=x_center + target_width)

    video_clip.write_videofile(os.path.join(PATH, new_filename), codec='libx264')
