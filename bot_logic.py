import asyncio
import threading
import logging
from youtube_auth import get_authenticated_service, get_auth_url
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError
import youtube_bot
import twitch_bot
import config
from utils import extract_video_id

class BotLogic:
    def __init__(self, chat_window, twitch_loop, youtube_loop):
        self.running = False
        self.auth_thread = None
        self.on_authenticated = None
        self.on_auth_failed = None
        self.on_bots_started = None
        self.on_start_bots_failed = None
        self.chat_window = chat_window
        self.twitch_loop = twitch_loop
        self.youtube_loop = youtube_loop
        self.twitch_bot = None
        self.youtube_bot = None
        self.word_filter_list = []

    def authenticate(self, auth_code):
        config.AUTH_CODE = auth_code
        self.auth_thread = threading.Thread(target=self._authenticate_service)
        self.auth_thread.start()

    def _authenticate_service(self):
        try:
            get_authenticated_service()
            if self.on_authenticated:
                self.on_authenticated()
        except InvalidGrantError:
            if self.on_auth_failed:
                self.on_auth_failed("Invalid authorization code. Please try again.")
        except Exception as e:
            if self.on_auth_failed:
                self.on_auth_failed(f"Authentication failed: {str(e)}")

    def set_on_authenticated_callback(self, callback):
        self.on_authenticated = callback

    def set_on_auth_failed_callback(self, callback):
        self.on_auth_failed = callback

    def start_bots(self, youtube_input):
        config.YT_CHAT_ID = extract_video_id(youtube_input)
        self.auth_thread = threading.Thread(target=self._validate_youtube_id_and_start_bots)
        self.auth_thread.start()

    def _validate_youtube_id_and_start_bots(self):
        try:
            youtube, token = get_authenticated_service()
            live_chat_id = asyncio.run(youtube_bot.fetch_live_chat_id(token, config.YT_CHAT_ID))
            if not live_chat_id:
                raise ValueError("Invalid YouTube Live Chat ID")
            self.running = True
            self._start_bots_threads()
            if self.on_bots_started:
                self.on_bots_started()
            self.set_chat_window_bots()  # Added here
        except Exception as e:
            logging.error(f"Error starting bots: {e}")
            if self.on_start_bots_failed:
                self.on_start_bots_failed(f"Error starting bots: {str(e)}")

    def set_on_bots_started_callback(self, callback):
        self.on_bots_started = callback

    def set_on_start_bots_failed_callback(self, callback):
        self.on_start_bots_failed = callback

    def _start_bots_threads(self):
        self.twitch_thread = threading.Thread(target=self._run_twitch_bot)
        self.youtube_thread = threading.Thread(target=self._run_youtube_bot)
        self.twitch_thread.start()
        self.youtube_thread.start()

    def _run_twitch_bot(self):
        asyncio.set_event_loop(self.twitch_loop)
        self.twitch_bot = twitch_bot.TwitchBot(self.chat_window, self.twitch_loop)
        self.twitch_bot.update_word_filter(self.word_filter_list)
        self.twitch_loop.run_until_complete(self.twitch_bot.start())
        logging.info("TwitchBot started")

    def _run_youtube_bot(self):
        asyncio.set_event_loop(self.youtube_loop)
        self.youtube_bot = youtube_bot.YouTubeBot(self.chat_window, self.twitch_bot)
        self.youtube_bot.update_word_filter(self.word_filter_list)
        self.youtube_loop.run_until_complete(self.youtube_bot.listen_to_chat())
        logging.info("YouTubeBot started")

    def stop_bots(self):
        self.running = False
        if self.twitch_bot:
            self.twitch_bot.close()
        if self.youtube_bot:
            self.youtube_bot.stop()

    def set_chat_window_bots(self):
        self.chat_window.set_bots(self.youtube_bot, self.twitch_bot)

    def update_word_filter(self, word_filter_list):
        self.word_filter_list = word_filter_list
        if self.twitch_bot:
            self.twitch_bot.update_word_filter(word_filter_list)
        if self.youtube_bot:
            self.youtube_bot.update_word_filter(word_filter_list)
