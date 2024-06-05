import sys
from PyQt5.QtWidgets import QApplication
from bot_gui import BotGUI
from chat_window import ChatWindow
import asyncio
import logging
import bot_logic

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    bot_gui = BotGUI()
    bot_gui.show()

    chat_window = ChatWindow()
    bot_gui.set_chat_window(chat_window)
    chat_window.show()

    twitch_loop = asyncio.new_event_loop()
    youtube_loop = asyncio.new_event_loop()

    bot_logic_instance = bot_logic.BotLogic(chat_window, twitch_loop, youtube_loop)
    bot_gui.set_bot_logic(bot_logic_instance)

    bot_gui.set_event_loops(twitch_loop, youtube_loop)

    sys.exit(app.exec_())
