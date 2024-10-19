import os
import random
from source.constants import (
    # RAW_PATH can be a command line argument or just be a folder outside the project (see .env)
    # same with FINAL_PATH
    RAW_PATH, TEMP_PATH, FINAL_PATH, REDDIT, DB_PATH, REQUEST_LIMIT
)
from source.utils import (
    get_text, get_screenshot, generate_audio, 
    combine_audio, get_subs, edit_video, save_id
)
from moviepy.config import change_settings


change_settings({"IMAGEMAGICK_BINARY": "C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe"})


# TODO s
### project management ### 
# Modify the code structure to keep the main.py as consice and straightforward as possible
# move the media/misc/ folder and or files to another dir
# impprove abstraction and add docstrings to functions
# maybe add a TODO s par in the README.md

### features ###
# there is a temp faile being created in the project root
# Preproces comment text and final subtitles to escape especial chars and censor insults
# implemnt google drive uploading with upload.py

# perhaps add as a command line argument -n=1 or --n_videos=1

NUMBER_OF_VIDEOS = 1


def main():
    posts = get_text(REDDIT, DB_PATH, NUMBER_OF_VIDEOS, REQUEST_LIMIT)
    for idx, submission in enumerate(posts):
        # submission['comment'].body = check_text(submission['comment'].body)
        id = submission['post'].id
        # get_paths()?
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
        video_template_path = random.choice([f for f in os.listdir(RAW_PATH) if f != '.gitkeep'])
        edit_video(
            # TODO ensure the video has the required lenght w full_audio_duration, see pymediainfo module
            os.path.join(RAW_PATH, video_template_path),
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
