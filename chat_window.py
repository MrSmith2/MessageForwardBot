import asyncio

from PyQt5.QtGui import QPixmap
import os
from PyQt5.QtWidgets import QWidget, QTextEdit, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton
from PyQt5.QtCore import QThread


class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_icons()
        self.youtube_bot = None
        self.twitch_bot = None

    def initUI(self):
        self.setGeometry(200, 200, 600, 400)
        self.setWindowTitle('Chat Window')

        self.layout = QVBoxLayout(self)

        self.chat_display = QTextEdit(self)
        self.chat_display.setReadOnly(True)
        self.layout.addWidget(self.chat_display)

        self.input_layout = QHBoxLayout()

        self.chat_input = QLineEdit(self)
        self.chat_input.setFixedHeight(40)
        self.input_layout.addWidget(self.chat_input)

        self.send_button = QPushButton('Send', self)
        self.send_button.setFixedSize(100, 40)
        self.send_button.clicked.connect(self.send_message)
        self.input_layout.addWidget(self.send_button)

        self.layout.addLayout(self.input_layout)
        self.chat_input.setVisible(False)
        self.send_button.setVisible(False)

    def load_icons(self):
        self.youtube_icon = QPixmap(os.path.join("Images/", "youtube_icon.png")).scaledToHeight(25)
        self.twitch_icon = QPixmap(os.path.join("Images/", "twitch_icon.png")).scaledToHeight(25)

    def set_bots(self, youtube_bot, twitch_bot):
        self.youtube_bot = youtube_bot
        self.twitch_bot = twitch_bot
        self.chat_input.setVisible(True)
        self.send_button.setVisible(True)

    def send_message(self):
        message = self.chat_input.text().strip()
        if message:
            self.chat_display.append(f'You: {message}')
            self.chat_input.clear()
            self.send_message_to_youtube_and_twitch(message)

    def send_message_to_youtube_and_twitch(self, message):
        if self.youtube_bot:
            self.youtube_thread = SendMessageThread(self.youtube_bot.send_message_to_youtube, message)
            self.youtube_thread.start()
        else:
            self.chat_display.append("Error: YouTube bot is not set.")

        if self.twitch_bot:
            self.twitch_thread = SendMessageThread(self.twitch_bot.send_message_to_twitch, message)
            self.twitch_thread.start()
        else:
            self.chat_display.append("Error: Twitch bot is not set.")

    def add_message(self, message, source=None):
        if "[TW]" in message or "[YT]" in message:
            return

        parts = message.split(":", 1)
        if len(parts) != 2:
            self.chat_display.append(message)
            return

        author, text = parts
        formatted_message = f'<span style="color: purple;">{author}:</span>{text}'

        if source:
            if source == 'YouTube':
                icon_html = '<img src="{}" height="20">'.format("Images/youtube_icon.png")
                self.chat_display.append(f'{icon_html} {formatted_message}')
            elif source == 'Twitch':
                icon_html = '<img src="{}" height="20">'.format("Images/twitch_icon.png")
                self.chat_display.append(f'{icon_html} {formatted_message}')
        else:
            self.chat_display.append(formatted_message)

class SendMessageThread(QThread):
    def __init__(self, func, *args, **kwargs):
        QThread.__init__(self)
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        asyncio.run(self.func(*self.args, **self.kwargs))
