from dotenv import load_dotenv
import os
import json

load_dotenv()

# Twitch
HOST = os.getenv('HOST')
PORT = int(os.getenv('PORT'))
BOT_NICK = os.getenv('BOT_NICK')
BOT_ID = os.getenv('BOT_ID')
TOKEN = os.getenv('TOKEN')
CHAN = os.getenv('CHAN')

# YouTube
API_KEY = os.getenv('API_KEY')
YT_CHAN = os.getenv('YT_CHAN')
YT_CHAT_ID = os.getenv('YT_CHAT_ID')
AUTH_CODE = os.getenv('AUTH_CODE')
CLIENT_SECRET_JSON = json.loads(os.getenv('CLIENT_SECRET_JSON'))
