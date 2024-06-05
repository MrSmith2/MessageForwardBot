import asyncio
import logging
from youtube_auth import get_authenticated_service
import config
from utils import fetch_live_chat_id, fetch_chat_messages, post_message_to_youtube

class YouTubeBot:
    def __init__(self, chat_window, twitch_bot):
        self.youtube, self.token = get_authenticated_service()
        self.chat_window = chat_window
        self.twitch_bot = twitch_bot
        self.word_filter_list = []
        logging.info(f"YouTubeBot initialized with twitch_bot: {self.twitch_bot}")

    async def listen_to_chat(self):
        live_chat_id = await fetch_live_chat_id(self.token, config.YT_CHAT_ID)
        if not live_chat_id:
            logging.error("No active chat found.")
            return

        processed_message_ids = set()
        next_page_token = None

        while True:
            try:
                messages, next_page_token = await fetch_chat_messages(self.token, live_chat_id, next_page_token)
                for message in messages:
                    message_id = message['id']
                    if message_id in processed_message_ids:
                        continue

                    processed_message_ids.add(message_id)
                    author = message['authorDetails']['displayName']
                    text = message['snippet']['textMessageDetails']['messageText']

                    if any(word in text for word in self.word_filter_list):
                        logging.info(f"Message filtered: {text}")
                        continue

                    youtube_message = f"{author}: {text}"
                    self.chat_window.add_message(youtube_message, source='YouTube')
                    logging.info('Message sent to Twitch')
                    await self.send_message_to_twitch(youtube_message)
            except Exception as e:
                logging.error(f"Error in listening to YouTube chat: {e}")

            await asyncio.sleep(2)

    async def send_message_to_youtube(self, message):
        message_with_tag = f"[TW]{message}"
        live_chat_id = await fetch_live_chat_id(self.token, config.YT_CHAT_ID)
        if live_chat_id:
            await post_message_to_youtube(self.token, live_chat_id, message_with_tag)
            logging.info(f"Message sent to YouTube: {message_with_tag}")

    async def send_message_to_twitch(self, message):
        message_with_tag = f"[YT]{message}"
        logging.info(f"Sending message to Twitch: {message_with_tag}")
        if self.twitch_bot:
            await self.twitch_bot.send_message_to_twitch(message_with_tag)
        else:
            logging.error("Twitch bot is not initialized.")

    def update_word_filter(self, word_filter_list):
        self.word_filter_list = word_filter_list
