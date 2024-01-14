import os
import random
import pyttsx3
import whisper
from PIL import Image # uninstall
from datetime import timedelta
# from pathlib import Path
# from openai import OpenAI
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip
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

def main():
    textfile_name = 'input_text.txt'
    audiofile_name = generate_audio(textfile_name, TEMP_PATH)
    subfile_name = get_subs(os.path.join(TEMP_PATH, audiofile_name), TEMP_PATH)
    videofile_name = edit_video(
        os.path.join(RAW_PATH, random.choice(os.listdir(RAW_PATH))), 
        os.path.join(TEMP_PATH, audiofile_name), 
        os.path.join(TEMP_PATH, subfile_name),
        FINAL_PATH
    )
    for f in os.listdir(TEMP_PATH):
        os.remove(os.path.join(TEMP_PATH, f))


def generate_audio(text_path, output_path):
    text_file = open(text_path, 'r')
    audiofile_name = 'audio.mp3'

    # pyttsx3
    engine = pyttsx3.init("sapi5")
    # TODO add final part 
    engine.setProperty('rate', 180)
    # engine.setProperty('voice', random.choice(engine.getProperty('voices')).id)
    engine.save_to_file(text_file.read(), os.path.join(output_path, audiofile_name))
    engine.runAndWait()

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

    return audiofile_name

def get_subs(audiofile_path, output_path):
    model = whisper.load_model('medium')
    transcribe = model.transcribe(audio=audiofile_path, word_timestamps=True)

    # create srt file
    srt_filename = 'sub.srt'

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
            with open(os.path.join(output_path, srt_filename), 'a', encoding='utf-8') as srtFile:
                srtFile.write(srt_section)

    return srt_filename

def edit_video(video_path, audio_path, sub_path, output_path):
    # open files
    video_clip = VideoFileClip(video_path)
    audio_clip = AudioFileClip(audio_path)
    generator = lambda txt : TextClip(txt, font='Montserrat-ExtraBold', fontsize=35, color='white', bg_color='black')
    subtitles_clip = SubtitlesClip(sub_path, generator).set_position(('center', 'center'))

    # edit video
    start_time = random.randint(0, int(video_clip.duration - audio_clip.duration))
    video_clip = video_clip.subclip(start_time, start_time + audio_clip.duration)

    target_width = int(video_clip.size[1] * 9 / 16)
    x_center = (video_clip.size[0] - target_width) / 2
    video_clip = video_clip.crop(x1=x_center, x2=x_center + target_width)

    # combine and write output file
    final_video = CompositeVideoClip([video_clip.set_audio(audio_clip), subtitles_clip])
    final_name = f'{len(os.listdir(output_path))}.mp4'
    final_video.write_videofile(os.path.join(output_path, final_name), codec='libx264')
    # TODO necesary ? close clips ?
    final_video.close()

    return final_name


main()
    