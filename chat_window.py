from PyQt5.QtGui import QPixmap
import os

from PyQt5.QtWidgets import QWidget, QTextEdit, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton


class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_icons()

    def initUI(self):
        self.setGeometry(200, 200, 600, 400)
        self.setWindowTitle('Chat Window')

        self.layout = QVBoxLayout(self)

        self.chat_display = QTextEdit(self)
        self.chat_display.setReadOnly(True)
        self.layout.addWidget(self.chat_display)

        self.input_layout = QHBoxLayout()

        self.chat_input = QLineEdit(self)
        self.input_layout.addWidget(self.chat_input)

        self.send_button = QPushButton('Send', self)
        self.send_button.clicked.connect(self.send_message)
        self.input_layout.addWidget(self.send_button)

        self.layout.addLayout(self.input_layout)

    def load_icons(self):
        self.youtube_icon = QPixmap(os.path.join("Images/", "youtube_icon.png")).scaledToHeight(25)
        self.twitch_icon = QPixmap(os.path.join("Images/", "twitch_icon.png")).scaledToHeight(25)

    def send_message(self):
        message = self.chat_input.text().strip()
        if message:
            self.chat_display.append(f'You: {message}')
            self.chat_input.clear()
            # ToDo

    def add_message(self, message, source=None):
        if "[TW]" in message or "[YT]" in message:
            return

        if source:
            if source == 'YouTube':
                icon_html = '<img src="{}" height="20">'.format("Images/youtube_icon.png")
                self.chat_display.append(f'{icon_html} {message}')
            elif source == 'Twitch':
                icon_html = '<img src="{}" height="20">'.format("Images/twitch_icon.png")
                self.chat_display.append(f'{icon_html} {message}')
        else:
            self.chat_display.append(message)
