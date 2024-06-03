from PyQt5.QtWidgets import (QWidget, QPushButton, QLabel, QLineEdit,
                             QVBoxLayout, QHBoxLayout, QMessageBox, QSizePolicy, QTabWidget, QFrame)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import bot_logic

class AuthThread(QThread):
    authenticated = pyqtSignal()
    auth_failed = pyqtSignal(str)

    def run(self):
        try:
            bot_logic.get_authenticated_service()
            self.authenticated.emit()
        except Exception as e:
            self.auth_failed.emit(str(e))

class BotThread(QThread):
    bots_started = pyqtSignal()
    start_bots_failed = pyqtSignal(str)

    def __init__(self, youtube_input, chat_window, twitch_loop, youtube_loop):
        super().__init__()
        self.youtube_input = youtube_input
        self.chat_window = chat_window
        self.twitch_loop = twitch_loop
        self.youtube_loop = youtube_loop

    def run(self):
        try:
            bot_logic.config.YT_CHAT_ID = bot_logic.extract_video_id(self.youtube_input)
            bot_logic_instance = bot_logic.BotLogic(chat_window=self.chat_window,
                                                    twitch_loop=self.twitch_loop,
                                                    youtube_loop=self.youtube_loop)
            bot_logic_instance.set_on_bots_started_callback(self.bots_started.emit)
            bot_logic_instance.set_on_start_bots_failed_callback(self.start_bots_failed.emit)
            bot_logic_instance.start_bots(self.youtube_input)
        except Exception as e:
            self.start_bots_failed.emit(str(e))

class BotGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.chat_window = None
        self.twitch_loop = None
        self.youtube_loop = None
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Forward Message Bot')

        self.tabs = QTabWidget()
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.tabs)

        # Create tabs
        self.auth_tab = QWidget()
        self.general_tab = QWidget()
        self.logs_tab = QWidget()

        self.tabs.addTab(self.auth_tab, "Authorization")
        self.tabs.addTab(self.general_tab, "General")
        self.tabs.addTab(self.logs_tab, "Logs")

        self.auth_tab_layout = QVBoxLayout()
        self.auth_tab.setLayout(self.auth_tab_layout)

        # Twitch
        twitch_section = QHBoxLayout()

        self.twitch_status_label = QLabel('Twitch\nStatus: Connected', self)
        self.twitch_status_label.setStyleSheet("font-size: 18px; color: green;")
        self.twitch_status_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        twitch_section.addWidget(self.twitch_status_label)

        self.twitch_reconnect_button = QPushButton('Reconnect', self)
        self.twitch_reconnect_button.setFixedSize(150, 50)
        self.twitch_reconnect_button.setStyleSheet("font-size: 18px;")
        self.twitch_reconnect_button.clicked.connect(self.reconnect_twitch)
        twitch_section.addWidget(self.twitch_reconnect_button)

        self.auth_tab_layout.addLayout(twitch_section)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.auth_tab_layout.addWidget(line)

        # YouTube
        youtube_section = QHBoxLayout()

        self.youtube_status_label = QLabel('YouTube\nStatus: Not connected', self)
        self.youtube_status_label.setStyleSheet("font-size: 18px; color: red;")
        self.youtube_status_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        youtube_section.addWidget(self.youtube_status_label)

        self.youtube_connect_button = QPushButton('Connect', self)
        self.youtube_connect_button.setFixedSize(150, 50)
        self.youtube_connect_button.setStyleSheet("font-size: 18px;")
        self.youtube_connect_button.clicked.connect(self.authenticate)
        youtube_section.addWidget(self.youtube_connect_button)

        self.auth_tab_layout.addLayout(youtube_section)

        self.auth_url_label = None
        self.auth_code_label = None
        self.auth_code_entry = None
        self.submit_auth_button = None
        self.youtube_label = None
        self.youtube_entry = None
        self.start_button = None
        self.status_label = None

    def set_chat_window(self, chat_window):
        self.chat_window = chat_window

    def set_event_loops(self, twitch_loop, youtube_loop):
        self.twitch_loop = twitch_loop
        self.youtube_loop = youtube_loop

    def reconnect_twitch(self):
        # ToDo
        pass

    def authenticate(self):
        auth_url = bot_logic.get_auth_url()
        self.show_auth_url(auth_url)

    def show_auth_url(self, auth_url):
        self.clear_auth_widgets()

        self.auth_url_label = QLabel("Please authorize using this link:", self)
        self.auth_url_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.auth_url_label.setOpenExternalLinks(True)
        self.auth_url_label.setText(f'<a href="{auth_url}">Please authorize using this link</a>')
        self.auth_url_label.setStyleSheet("font-size: 16px;")
        self.auth_tab_layout.addWidget(self.auth_url_label, alignment=Qt.AlignLeft)

        self.auth_code_label = QLabel("Enter the authorization code:", self)
        self.auth_code_label.setStyleSheet("font-size: 16px;")
        self.auth_tab_layout.addWidget(self.auth_code_label, alignment=Qt.AlignLeft)

        self.auth_code_entry = QLineEdit(self)
        self.auth_code_entry.setFixedSize(500, 50)  # Увеличенный размер
        self.auth_code_entry.setStyleSheet("font-size: 16px;")
        self.auth_tab_layout.addWidget(self.auth_code_entry, alignment=Qt.AlignLeft)

        self.submit_auth_button = QPushButton('Submit Authorization Code', self)
        self.submit_auth_button.clicked.connect(self.submit_auth_code)
        self.submit_auth_button.setFixedSize(250, 50)
        self.submit_auth_button.setStyleSheet("font-size: 16px;")
        self.auth_tab_layout.addWidget(self.submit_auth_button, alignment=Qt.AlignLeft)

    def clear_auth_widgets(self):
        if self.auth_url_label:
            self.auth_tab_layout.removeWidget(self.auth_url_label)
            self.auth_url_label.deleteLater()
            self.auth_url_label = None
        if self.auth_code_label:
            self.auth_tab_layout.removeWidget(self.auth_code_label)
            self.auth_code_label.deleteLater()
            self.auth_code_label = None
        if self.auth_code_entry:
            self.auth_tab_layout.removeWidget(self.auth_code_entry)
            self.auth_code_entry.deleteLater()
            self.auth_code_entry = None
        if self.submit_auth_button:
            self.auth_tab_layout.removeWidget(self.submit_auth_button)
            self.submit_auth_button.deleteLater()
            self.submit_auth_button = None

    def submit_auth_code(self):
        auth_code = self.auth_code_entry.text().strip()
        if not auth_code:
            QMessageBox.critical(self, "Error", "Authorization code cannot be empty. Please enter a valid code.")
            return

        bot_logic.config.AUTH_CODE = auth_code
        self.auth_thread = AuthThread()
        self.auth_thread.authenticated.connect(self.show_video_id_field)
        self.auth_thread.auth_failed.connect(self.show_auth_error)
        self.auth_thread.start()

    def show_auth_error(self, error_message):
        QMessageBox.critical(self, "Error", error_message)
        auth_url = bot_logic.get_auth_url()
        self.show_auth_url(auth_url)

    def show_video_id_field(self):
        self.clear_auth_widgets()
        self.clear_video_widgets()

        self.youtube_label = QLabel("YouTube Video ID or URL:", self)
        self.youtube_label.setStyleSheet("font-size: 16px;")
        self.auth_tab_layout.addWidget(self.youtube_label, alignment=Qt.AlignLeft)

        self.youtube_entry = QLineEdit(self)
        self.youtube_entry.setFixedSize(500, 50)
        self.youtube_entry.setStyleSheet("font-size: 16px;")
        self.auth_tab_layout.addWidget(self.youtube_entry, alignment=Qt.AlignLeft)

        self.start_button = QPushButton('Start Bot', self)
        self.start_button.clicked.connect(self.start_bots)
        self.start_button.setFixedSize(250, 50)
        self.start_button.setStyleSheet("font-size: 16px;")
        self.auth_tab_layout.addWidget(self.start_button, alignment=Qt.AlignLeft)

    def start_bots(self):
        youtube_input = self.youtube_entry.text().strip()
        if not youtube_input:
            QMessageBox.critical(self, "Error",
                                 "YouTube Video ID or URL cannot be empty. Please enter a valid ID или URL.")
            return

        self.bot_thread = BotThread(youtube_input, self.chat_window, self.twitch_loop, self.youtube_loop)
        self.bot_thread.bots_started.connect(self.show_status_running)
        self.bot_thread.start_bots_failed.connect(self.show_error_message)
        self.bot_thread.start()

    def show_status_running(self):
        self.clear_video_widgets()
        self.youtube_status_label.setText('YouTube\nStatus: Connected')
        self.youtube_status_label.setStyleSheet("font-size: 18px; color: green;")
        self.youtube_connect_button.setText('Reconnect')
        self.status_label = QLabel("Bot is running", self)
        self.status_label.setStyleSheet('color: green; font-size: 16px;')
        self.auth_tab_layout.addWidget(self.status_label, alignment=Qt.AlignLeft)

    def show_error_message(self, error):
        QMessageBox.critical(self, "Error", f"Error starting bots: {error}")
        self.show_video_id_field()

    def clear_video_widgets(self):
        if self.youtube_label:
            self.auth_tab_layout.removeWidget(self.youtube_label)
            self.youtube_label.deleteLater()
            self.youtube_label = None
        if self.youtube_entry:
            self.auth_tab_layout.removeWidget(self.youtube_entry)
            self.youtube_entry.deleteLater()
            self.youtube_entry = None
        if self.start_button:
            self.auth_tab_layout.removeWidget(self.start_button)
            self.start_button.deleteLater()
            self.start_button = None
