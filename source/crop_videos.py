# dont run, output video freezes in the firsts frames, managed in main.py
import os
import subprocess

RAW_PATH = os.path.join(os.getcwd(), 'media', 'video_templates')


def crop(input_file, output_file):
    # Get the input video's resolution and aspect ratio
    result = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height,sample_aspect_ratio', '-of', 'csv=s=x:p=0', input_file], capture_output=True, text=True)
    width, height = map(int, result.stdout.strip().split('x')[:2])
    # height = int(result.stdout.strip().split('x')[1])
    new_width = int(height * 9/16)
    crop_params = f'crop={new_width}:{height}'
    # scale_params = f'scale={new_width}:{height},setsar=1,setdar={9/16}'

    # Run FFmpeg to change the aspect ratio
    # add '-hwaccel_output_format', 'cuda', '-c:v', 'h264_nvenc', '-preset', 'slow', if CUDA codec available
    commands = ['ffmpeg', '-hwaccel', 'cuda', '-hwaccel_output_format', 'cuda', '-i', 
                input_file, '-c:v', 'h264_nvenc', '-vf', crop_params, '-c:a', 'copy', '-preset', 'slow', output_file]
    subprocess.run(commands)


to_crop = os.listdir(RAW_PATH)
for idx, file in enumerate(to_crop):
    input = os.path.join(RAW_PATH, file)
    output = f'{idx}.mp4'
    # output = os.path.join(RAW_PATH, f'{idx}.mp4')
    crop(input, output)
    # os.remove(input)
