from utils import *
from dotenv import load_dotenv
from moviepy.config import change_settings

load_dotenv()
change_settings({'IMAGEMAGICK_BINARY': 'C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe'})
MEDIA_PATH = os.path.join(os.getcwd(), 'media')
RAW_PATH = os.path.join(MEDIA_PATH, 'video_templates')
TEMP_PATH = os.path.join(MEDIA_PATH, 'temp')
FINAL_PATH = os.path.join(MEDIA_PATH, 'videos')
DB_PATH = os.path.join(MEDIA_PATH, 'misc', 'db.csv')
NUMBER_OF_VIDEOS = 3
REQUEST_LIMIT = 100


def main():
    posts = get_text(DB_PATH, NUMBER_OF_VIDEOS, REQUEST_LIMIT)
    for submission in posts:
        # TODO preprocess txt
        # TODO save txt to files
        id = submission['post'].id
        screenshot_path = os.path.join(TEMP_PATH, f'{id}_screenshot.png')
        title_audio_path = os.path.join(TEMP_PATH, f'{id}_title.mp3')
        body_audio_path = os.path.join(TEMP_PATH, f'{id}_body.mp3')
        full_audio_path = os.path.join(TEMP_PATH, f'{id}_full.mp3')
        subtitle_path = os.path.join(TEMP_PATH, f'{id}_subs.srt')
        video_path = os.path.join(FINAL_PATH, f'{id}.mp4')

        get_screenshot(submission['post'].url, id, screenshot_path)
        generate_audio(submission['post'].title, title_audio_path)
        generate_audio(submission['comment'].body, body_audio_path)

        # combine audio files - should be a func, edit_video param title.duration
        title = AudioFileClip(title_audio_path)
        body = AudioFileClip(body_audio_path)
        audio_clip = CompositeAudioClip([title, body.set_start(title.duration)])
        audio_clip.write_audiofile(full_audio_path, fps=44100)

        get_subs(full_audio_path, subtitle_path)
        edit_video(
            # TODO ensure the video has the required lenght
            os.path.join(RAW_PATH, random.choice(os.listdir(RAW_PATH))),
            title.duration, 
            full_audio_path, 
            subtitle_path,
            screenshot_path,
            video_path
        )
        # save titles in file with id
        print(submission['post'].title)
        save_id(DB_PATH, id, submission['comment'].id)
        # remove_temp()
        for f in os.listdir(TEMP_PATH):
            os.remove(os.path.join(TEMP_PATH, f))


if __name__ == '__main__':
    main()
