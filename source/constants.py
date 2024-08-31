"""This module contains constant values and config settings."""

import os
import praw
from dotenv import load_dotenv
from moviepy.config import change_settings

# Load environment variables
load_dotenv(os.path.join(os.getcwd(), 'config/.env'))

# Configure the path to the ImageMagick binary
change_settings({'IMAGEMAGICK_BINARY': os.getenv('IMAGEMAGIK_PATH')})

# Define paths for media files
MEDIA_PATH = os.path.join(os.getcwd(), 'media')
RAW_PATH = os.path.join(MEDIA_PATH, 'video_templates')
TEMP_PATH = os.path.join(MEDIA_PATH, 'temp')
FINAL_PATH = os.path.join(MEDIA_PATH, 'videos')

# Reddit API configuration
REDDIT = praw.Reddit(
    client_id=os.getenv('REDDIT_APP_ID'),
    client_secret=os.getenv('REDDIT_APP_SECRET'),
    password=os.getenv('REDDIT_PASSWORD'),
    user_agent=os.getenv('REDDIT_USER_AGENT'),
    username=os.getenv('REDDIT_USERNAME'),
)

# Path to the database file
DB_PATH = os.path.join(MEDIA_PATH, 'misc', 'db.csv')

# Other configuration constants
REQUEST_LIMIT = 100
