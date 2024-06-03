import asyncio
import logging
from youtube_auth import get_authenticated_service
import config
from utils import fetch_live_chat_id, fetch_chat_messages

class YouTubeBot:
    def __init__(self, chat_window, twitch_bot):
        self.youtube, self.token = get_authenticated_service()
        self.chat_window = chat_window
        self.twitch_bot = twitch_bot

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
                    youtube_message = f"{author}: {text}"
                    self.chat_window.add_message(youtube_message, source='YouTube')
                    logging.info('Message sent to Twitch')
                    await self.send_message_to_twitch(youtube_message)
            except Exception as e:
                logging.error(f"Error in listening to YouTube chat: {e}")

            await asyncio.sleep(2)

    async def send_message_to_twitch(self, message):
        message_with_tag = f"[YT]{message}"
        logging.info(f"Sending message to Twitch: {message_with_tag}")
        await self.twitch_bot.send_message_to_twitch(message_with_tag)
