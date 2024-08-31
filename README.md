VIDEO GENERATOR

Setup

run:

    pip install -r requirements.txt

Install ImageMagik:

    https://imagemagick.org/script/download.php

Change main.py if ImageMagik not installed in default directory:

    line 18: change_settings({"IMAGEMAGICK_BINARY": <PATH_TO_IMAGEMAGIK>})

add custom font in media/misc/ to ImageMagik type-ghostscript.xml:
    
  <type name="Montserrat-ExtraBold" format="ttf" glyphs=<PATH_TO_FONT>/> 
  Note: name can be anything as long as it referenced in main.py edit_video()

Change pytube innertube.py file to fix age restriction error in get_videos.py:

    line 223: 'ANDROID_MUSIC' to 'ANDROID'

Create .env file and set the variables listed in .env.example 

yt-dlp ussage:

    yt-dlp --yes-playlist -o "PATH/TO/SAVE_FOLDER/%(title)s.%(ext)s" "YOUTUBE_PLAYLIST_URL"
