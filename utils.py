import os
import random
import pyttsx3
import whisper
import csv
import torch
import pandas as pd
from datetime import timedelta
# from pathlib import Path
# from openai import OpenAI
import praw
from praw.models import MoreComments
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeAudioClip, ImageClip
from moviepy.video.io.VideoFileClip import VideoFileClip # why 2 VideoFileClip
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.fx.all import crop


def get_text(database, n_videos, limit):
    # get posts
    reddit = praw.Reddit(
        client_id=os.getenv('REDDIT_APP_ID'),
        client_secret=os.getenv('REDDIT_APP_SECRET'),
        password=os.getenv('REDDIT_PASSWORD'),
        user_agent=os.getenv('REDDIT_USER_AGENT'),
        username=os.getenv('REDDIT_USERNAME'),
    )
    
    posts = []
    df = pd.read_csv(database)

    # see limit
    for submission in reddit.subreddit('askreddit').hot(limit=int(limit/2)):
        # skip over_18 or already in db
        if submission.over_18 or df['post_id'].eq(submission.id).any():
            continue
    
        # get comments
        comments_filtered = []
        for comment in submission.comments.list():
            # replace_more method, each replacement requires one network request
            if isinstance(comment, MoreComments):
                continue

            # min 180 words - 1 min, max 900 words - 5 mins
            if 180 < len(comment.body.split()) < 900:
                comments_filtered.append(comment)

        if len(comments_filtered) == 0:
            continue

        # get longest comment
        # comment_final = sorted(comments_filtered, key=lambda c: len(c.body), reverse=True)[0]

        # get comment with highest score (upvotes)
        comment_final = sorted(comments_filtered, key=lambda c: c.score, reverse=True)[0]

        posts.append({'post': submission, 'comment': comment_final})

    return posts[:n_videos]


def get_screenshot(post_url, post_id, output_path):
    # TODO handle timeout exception
    driver = webdriver.Firefox()
    driver.get(post_url)
    search = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, f't3_{post_id}')))
    with open(output_path, 'wb') as file:
        file.write(search.screenshot_as_png)
    # driver.close()
    driver.quit()


def generate_audio(text, output_path):
    engine = pyttsx3.init("sapi5")
    engine.setProperty('rate', 180)
    # engine.setProperty('voice', random.choice(engine.getProperty('voices')).id)
    engine.save_to_file(text, output_path)
    engine.runAndWait()


# def generate_audio(text_path, output_path):
    # openai tts - paid option
    # voices = ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']
    # let the user know it is an ai generated voice per policy
    # client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    # response = client.audio.speech.create(
    #     model='tts-1',
    #     voice='alloy',
    #     input=text_file.read()
    # )
    # response.stream_to_file(os.path.join(output_path, audiofile_name))


def get_subs(audiofile_path, output_path):
    torch.cuda.init()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = whisper.load_model('medium').to(device)
    with torch.cuda.device(device):
        transcribe = model.transcribe(audio=audiofile_path, fp16=False, word_timestamps=True)
    create_srt(transcribe, output_path)


def create_srt(transcribe, output_path):
    to_write = []
    for segment in transcribe['segments']:
        for idx, item in enumerate(segment['words']):
            segment_id = segment['id'] + 1 + idx
            start_delta = str(timedelta(seconds=item['start'])).replace('.', ',')[:11]
            start_time = f'0{start_delta if len(start_delta) == 11 else start_delta + ",000"}'
            end_delta = str(timedelta(seconds=item['end'])).replace('.', ',')[:11]
            end_time = f'0{end_delta if len(end_delta) == 11 else end_delta + ",000"}'
            text = item['word'].strip().upper()

            srt_section = f'{segment_id}\n{start_time} --> {end_time}\n{text}\n\n'
            to_write.append(srt_section)

    # should be write instead of append
    with open(output_path, 'a', encoding='utf-8') as srtFile:
        srtFile.write(''.join(to_write))


def edit_video(video_path, title_duration, audio_path, sub_path, image_path, output_path):
    # TODO explore using ffmpeg to edit with gpu
    # open files
    video_clip = VideoFileClip(video_path)
    audio_clip = AudioFileClip(audio_path)
    generator = lambda txt : TextClip(txt, font='Montserrat-ExtraBold', fontsize=75, color='white', bg_color='black')
    subtitles_clip = SubtitlesClip(sub_path, generator).set_position(('center', 'center'))
    image_clip = ImageClip(image_path, duration=title_duration).set_position(('center', 'center'))

    # edit video
    start_time = random.randint(0, int(video_clip.duration - audio_clip.duration))
    video_clip = video_clip.subclip(start_time, start_time + audio_clip.duration)

    # TODO check aspect ratio before crop
    target_width = int(video_clip.size[1] * 9 / 16)
    x_center = (video_clip.size[0] - target_width) / 2
    video_clip = video_clip.crop(x1=x_center, x2=x_center + target_width)

    image_clip = image_clip.resize(width=int(target_width * 0.9))

    # combine and write output file
    final_video = CompositeVideoClip([video_clip.set_audio(audio_clip), subtitles_clip, image_clip])
    # others configs: threads=12, temp file
    final_video.write_videofile(
        output_path, codec='mpeg4', fps=24, threads=12, preset='slow', 
        bitrate='8000k', ffmpeg_params=['-crf', '24']
    )

    # closing files, ram friendly
    video_clip.close()
    audio_clip.close()
    subtitles_clip.close()
    image_clip.close()
    final_video.close()


def save_id(database, post_id, comment_id):
    # TODO use pandas
    with open(database, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['post_id', 'comment_id'])
        writer.writerow({'post_id': post_id, 'comment_id': comment_id})
