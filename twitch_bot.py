from twitchio.ext import commands
from youtube_auth import get_authenticated_service
from utils import fetch_live_chat_id, post_message_to_youtube
import config
import logging

class TwitchBot(commands.Bot):
    def __init__(self, chat_window, loop):
        super().__init__(token=config.TOKEN, prefix='!', initial_channels=[config.CHAN], loop=loop)
        self.youtube, self.token = None, None
        self.chat_window = chat_window

    async def event_ready(self):
        logging.info(f'Logged in as | {self.nick}')
        for channel in self.connected_channels:
            logging.info(f'Connected to channel: {channel.name}')

    async def event_message(self, message):
        if message.echo or "[YT]" in message.content:
            return

        user_message = f"{message.author.name}: {message.content}"
        self.chat_window.add_message(user_message, source='Twitch')
        logging.info(f"Received message from Twitch: {user_message}")
        await self.send_message_to_youtube(user_message)

    async def send_message_to_youtube(self, message):
        message_with_tag = f"[TW]{message}"
        logging.info(f"Sending message to YouTube: {message_with_tag}")

        if not self.youtube or not self.token:
            self.youtube, self.token = get_authenticated_service()

        live_chat_id = await fetch_live_chat_id(self.token, config.YT_CHAT_ID)
        if live_chat_id:
            await post_message_to_youtube(self.token, live_chat_id, message_with_tag)

    async def send_message_to_twitch(self, message):
        if "[TW]" in message:
            logging.info(f"Preventing loop: Not sending message to Twitch: {message}")
            return
        for channel in self.connected_channels:
            logging.info(f"Sending message to Twitch channel: {channel.name}: {message}")
            await channel.send(message)
