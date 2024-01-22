from utils import *


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

            # minimum 180 words
            if len(comment.body.split()) > 180:
                comments_filtered.append(comment)

        if len(comments_filtered) == 0:
            continue

        # get longest comment
        # comment_final = max([c.body for c in comments_filtered], key=len)
        comment_final = sorted(comments_filtered, key=lambda c: len(c.body), reverse=True)[0]

        posts.append({'post': submission, 'comment': comment_final})

    return posts[:n_videos]


def get_screenshot(post_url, post_id, output_path):
    driver = webdriver.Firefox()
    driver.get(post_url)
    search = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, f't3_{post_id}')))
    with open(output_path, 'wb') as file:
        file.write(search.screenshot_as_png)
    # TODO close browser
    # driver.close()
    driver.quit()


def generate_audio(text, output_path):
    engine = pyttsx3.init("sapi5")
    engine.setProperty('rate', 180)
    # engine.setProperty('voice', random.choice(engine.getProperty('voices')).id)
    engine.save_to_file(text, output_path)
    engine.runAndWait()


def get_subs(audiofile_path, output_path):
    model = whisper.load_model('medium')
    transcribe = model.transcribe(audio=audiofile_path, word_timestamps=True)
    create_srt(transcribe, output_path)


def edit_video(video_path, title_duration, audio_path, sub_path, image_path, output_path):
    # TODO explore using ffmpeg to edit with gpu
    # open files
    video_clip = VideoFileClip(video_path)
    audio_clip = AudioFileClip(audio_path)
    generator = lambda txt : TextClip(txt, font='Montserrat-ExtraBold', fontsize=35, color='white', bg_color='black')
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
    # threads=4, fps=24, preset='slow' , ffmpeg_params['-crf', '24']
    # codec='mpeg4', threads=12, bitrate='8000k 
    final_video.write_videofile(output_path, codec='libx264')
    # TODO necesary ? close clips ?
    final_video.close()


def main():
    posts = get_text(
        os.path.join(MEDIA_PATH, 'misc', 'db.csv'), NUMBER_OF_VIDEOS, REQUEST_LIMIT
    )
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

        # combine audio files - should be a func
        title = AudioFileClip(title_audio_path)
        body = AudioFileClip(body_audio_path)
        audio_clip = CompositeAudioClip([title, body.set_start(title.duration)])
        audio_clip.write_audiofile(full_audio_path, fps=44100)

        get_subs(full_audio_path, subtitle_path)
        edit_video(
            os.path.join(RAW_PATH, random.choice(os.listdir(RAW_PATH))),
            title.duration, 
            full_audio_path, 
            subtitle_path,
            screenshot_path,
            video_path
        )
        save_id(os.path.join(MEDIA_PATH, 'misc', 'db.csv'), id, submission['comment'].id)
        # remove_temp()
        for f in os.listdir(TEMP_PATH):
            os.remove(os.path.join(TEMP_PATH, f))


if __name__ == '__main__':
    main()
