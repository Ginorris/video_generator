import os
import random
import pyttsx3
import whisper
import csv
import pandas as pd
from PIL import Image # uninstall
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
from moviepy.config import change_settings
from dotenv import load_dotenv

load_dotenv()
change_settings({"IMAGEMAGICK_BINARY": 'C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe'})
MEDIA_PATH = os.path.join(os.getcwd(), 'media')
RAW_PATH = os.path.join(MEDIA_PATH, 'video_templates')
TEMP_PATH = os.path.join(MEDIA_PATH, 'temp')
FINAL_PATH = os.path.join(MEDIA_PATH, 'videos')
NUMBER_OF_VIDEOS = 3
REQUEST_LIMIT = 100


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


def save_id(database, post_id, comment_id):
    # use pandas
    with open(database, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['post_id', 'comment_id'])
        writer.writerow({'post_id': post_id, 'comment_id': comment_id})


def create_srt(transcribe, output_path):
    for segment in transcribe['segments']:
        for idx, item in enumerate(segment['words']):
            segment_id = segment['id'] + 1 + idx
            start_delta = str(timedelta(seconds=item['start'])).replace('.', ',')[:11]
            start_time = f'0{start_delta if len(start_delta) == 11 else start_delta + ",000"}'
            end_delta = str(timedelta(seconds=item['end'])).replace('.', ',')[:11]
            end_time = f'0{end_delta if len(end_delta) == 11 else end_delta + ",000"}'
            text = item['word'].strip().upper()

            srt_section = f'{segment_id}\n{start_time} --> {end_time}\n{text}\n\n'

            # TODO opening file on each iteration
            with open(output_path, 'a', encoding='utf-8') as srtFile:
                srtFile.write(srt_section)
