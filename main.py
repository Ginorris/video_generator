from source.utils import *
import os
import praw
from dotenv import load_dotenv
from moviepy.config import change_settings


load_dotenv(os.path.join(os.getcwd(), 'config/.env'))
change_settings({'IMAGEMAGICK_BINARY': os.getenv('IMAGEMAGIK_PATH')})

# Constants definitios
MEDIA_PATH = os.path.join(os.getcwd(), 'media')
RAW_PATH = os.path.join(MEDIA_PATH, 'video_templates')
TEMP_PATH = os.path.join(MEDIA_PATH, 'temp')
FINAL_PATH = os.path.join(MEDIA_PATH, 'videos')
REDDIT = praw.Reddit(
    client_id=os.getenv('REDDIT_APP_ID'),
    client_secret=os.getenv('REDDIT_APP_SECRET'),
    password=os.getenv('REDDIT_PASSWORD'),
    user_agent=os.getenv('REDDIT_USER_AGENT'),
    username=os.getenv('REDDIT_USERNAME'),
)
DB_PATH = os.path.join(MEDIA_PATH, 'misc', 'db.csv')
REQUEST_LIMIT = 100

NUMBER_OF_VIDEOS = 1


def main():
    posts = get_text(REDDIT, DB_PATH, NUMBER_OF_VIDEOS, REQUEST_LIMIT)
    for idx, submission in enumerate(posts):
        # submission['comment'].body = check_text(submission['comment'].body)
        id = submission['post'].id
        screenshot_path = os.path.join(TEMP_PATH, f'{id}_screenshot.png')
        title_audio_path = os.path.join(TEMP_PATH, f'{id}_title.mp3')
        body_audio_path = os.path.join(TEMP_PATH, f'{id}_body.mp3')
        full_audio_path = os.path.join(TEMP_PATH, f'{id}_full.mp3')
        subtitle_path = os.path.join(TEMP_PATH, f'{id}_subs.srt')
        # TODO video filename = title, preprocess it before
        video_path = os.path.join(FINAL_PATH, f'{id}.mp4')

        if not get_screenshot(submission['post'].url, id, screenshot_path):
            continue

        generate_audio(submission['post'].title, title_audio_path)
        generate_audio(submission['comment'].body, body_audio_path)

        title_duration, full_audio_duration = combine_audio(
            title_audio_path, body_audio_path, full_audio_path
        )

        get_subs(full_audio_path, subtitle_path)
        edit_video(
            # TODO ensure the video has the required lenght w full_audio_duration, see pymediainfo module
            os.path.join(RAW_PATH, random.choice(os.listdir(RAW_PATH))),
            title_duration, 
            full_audio_path, 
            subtitle_path,
            screenshot_path,
            video_path
        )
        with open(os.path.join(FINAL_PATH, 'description.txt'), 'a') as file:
            file.write(f'{id} - {submission["post"].title}\n\n')

        save_id(DB_PATH, id, submission['comment'].id)
        # TODO upload_to_drive()
        # TODO remove_temp()
        for f in os.listdir(TEMP_PATH):
            os.remove(os.path.join(TEMP_PATH, f))
        print(f'---------- FINISHED {idx + 1}/{NUMBER_OF_VIDEOS} VIDEOS ----------')


if __name__ == '__main__':
    main()
