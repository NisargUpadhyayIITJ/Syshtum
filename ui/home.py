# ui/home.py
import requests
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QListWidget, QHBoxLayout, QFrame
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QIcon
from operate.config import Config
from operate.operate import main
import sys
from operate.utils.style import (
    ANSI_GREEN,
    ANSI_RESET,
    ANSI_RED,
)

class RequestException(IOError):
    def __init__(self, *args, **kwargs):
        response = kwargs.pop("response", None)
        self.response = response
        self.request = kwargs.pop("request", None)
        if response is not None and not self.request and hasattr(response, "request"):
            self.request = self.response.request
        super().__init__(*args, **kwargs)

class HTTPError(RequestException):
    pass

# Worker thread for running the main function
class MainWorker(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, model, command):
        super().__init__()
        self.model = model
        self.command = command

    def run(self):
        try:
            main(model=self.model, terminal_prompt=self.command)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

class HomeScreen(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)
        self.setMaximumWidth(800)

        title = QLabel("AgentOpera")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #60A5FA; margin-bottom: 5px;")
        layout.addWidget(title)

        subtitle = QLabel("Control your computer with natural language commands")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size: 14px; color: #9CA3AF; margin-bottom: 20px;")
        layout.addWidget(subtitle)

        main_frame = QFrame()
        main_frame.setStyleSheet("background-color: #111827; border-radius: 12px; padding: 20px;")
        main_layout = QVBoxLayout(main_frame)
        main_layout.setSpacing(15)

        self.error_label = QLabel("Invalid API Key or API Key not found")
        self.error_label.setStyleSheet("color: #F87171; padding: 10px; background-color: #1F2937; border-radius: 5px;")
        
        error_container = QHBoxLayout()
        error_container.addWidget(self.error_label, 1)
        
        enter_api_btn = QPushButton("Enter API Key")
        enter_api_btn.setStyleSheet("""
            QPushButton {
                background-color: #374151; 
                color: white; 
                padding: 8px 15px; 
                border-radius: 5px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #4B5563;
            }
        """)
        enter_api_btn.clicked.connect(lambda: self.parent.navigate_to("save_api"))
        error_container.addWidget(enter_api_btn)
        
        main_layout.addLayout(error_container)

        self.model_combo = QComboBox()
        self.model_combo.addItems(["GPT-4o", "Gemini"])
        self.model_combo.setStyleSheet("""
            QComboBox {
                background-color: #1F2937; 
                color: #D1D5DB; 
                padding: 12px;
                border-radius: 5px;
                selection-background-color: #2563EB;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(path/to/down_arrow.png);  /* Replace with actual icon if available */
            }
        """)
        main_layout.addWidget(self.model_combo)

        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Enter your command...")
        self.command_input.setStyleSheet("""
            QLineEdit {
                background-color: #1F2937; 
                color: #D1D5DB; 
                padding: 12px; 
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #3B82F6;
            }
        """)
        main_layout.addWidget(self.command_input)

        buttons_container = QHBoxLayout()
        
        self.execute_btn = QPushButton("Execute Command")
        self.execute_btn.setIcon(QIcon("path/to/arrow_icon.png"))  # Replace with actual icon
        self.execute_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3B82F6, stop:1 #9333EA);
                color: white; 
                padding: 12px; 
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4F46E5, stop:1 #A855F7);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563EB, stop:1 #7E22CE);
            }
            QPushButton:disabled {
                background: #6B7280;
                color: #9CA3AF;
            }
        """)
        buttons_container.addWidget(self.execute_btn)
        
        self.voice_btn = QPushButton("Voice Input")
        self.voice_btn.setIcon(QIcon("path/to/mic_icon.png"))  # Replace with actual icon
        self.voice_btn.setStyleSheet("""
            QPushButton {
                background-color: #1F2937;
                color: white; 
                padding: 12px; 
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #374151;
            }
            QPushButton:pressed {
                background-color: #4B5563;
            }
            QPushButton:disabled {
                background-color: #1F2937;
                color: #6B7280;
            }
        """)
        buttons_container.addWidget(self.voice_btn)
        
        main_layout.addLayout(buttons_container)

        recent_container = QHBoxLayout()
        
        recent_label = QLabel("Recent commands")
        recent_label.setStyleSheet("color: #6B7280; font-size: 14px;")
        recent_container.addWidget(recent_label)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #1F2937; 
                color: #9CA3AF; 
                padding: 5px 10px; 
                border-radius: 5px;
                font-size: 12px;
                margin-right: 8px;
            }
            QPushButton:hover {
                background-color: #374151;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_data)
        recent_container.addWidget(refresh_btn, 0, Qt.AlignmentFlag.AlignRight)
        
        history_btn = QPushButton("History")
        history_btn.setStyleSheet("""
            QPushButton {
                background-color: #1F2937; 
                color: #9CA3AF; 
                padding: 5px 10px; 
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #374151;
            }
        """)
        recent_container.addWidget(history_btn, 0, Qt.AlignmentFlag.AlignRight)
        
        main_layout.addLayout(recent_container)

        self.recent_list = QListWidget()
        self.recent_list.setStyleSheet("""
            QListWidget {
                background-color: #1F2937; 
                color: #D1D5DB; 
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
            QListWidget::item:selected {
                background-color: #2563EB;
            }
        """)
        self.recent_list.setMaximumHeight(100)
        main_layout.addWidget(self.recent_list)

        self.no_commands_label = QLabel("No recent commands")
        self.no_commands_label.setStyleSheet("color: #6B7280; padding: 10px; font-size: 14px;")
        self.no_commands_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.no_commands_label)

        layout.addWidget(main_frame)
        self.setLayout(layout)
        
        self.command_input.returnPressed.connect(self.execute_command)
        self.execute_btn.clicked.connect(self.execute_command)
        self.recent_list.itemClicked.connect(self.reuse_command)
        self.model_combo.currentTextChanged.connect(self.validate_api_key)
        self.voice_btn.clicked.connect(self.activate_voice_input)
        
        self.validate_api_key()

    def validate_api_key(self):
        model = "fast-gpt" if self.model_combo.currentText() == "GPT-4o" else "fast-gemini"
        try:
            config = Config()
            if config.validation(model, voice_mode=False):
                self.error_label.setVisible(True)
                self.execute_btn.setEnabled(False)
                self.command_input.setEnabled(False)
                self.voice_btn.setEnabled(False)
            else:
                self.error_label.setVisible(False)
                self.execute_btn.setEnabled(True)
                self.command_input.setEnabled(True)
                self.voice_btn.setEnabled(True)
        except requests.RequestException as e:
            self.error_label.setText(f"Error: {str(e)}")
            self.error_label.setVisible(True)

    def execute_command(self):
        command = self.command_input.text().strip()
        if not command:
            return

        model = "fast-gpt" if self.model_combo.currentText() == "GPT-4o" else "fast-gemini"
        try:
            config = Config()
            if config.validation(model, voice_mode=False):
                raise HTTPError("Error occurred in validating API Key.", response=self)
            
            # Navigate to processing screen
            self.parent.navigate_to("processing")
            
            # Update button states immediately
            self.execute_btn.setText("Processing...")
            self.execute_btn.setEnabled(False)
            
            # Run main in a separate thread
            self.worker = MainWorker(model, command)
            self.worker.finished.connect(self.on_main_finished)
            self.worker.error.connect(self.on_main_error)
            self.worker.start()
            
        except requests.RequestException as e:
            self.error_label.setText(f"Error: {str(e)}")
            self.error_label.setVisible(True)
            self.execute_btn.setText("Execute Command")
            self.execute_btn.setEnabled(True)

    def on_main_finished(self):
        # Return to home screen
        self.parent.navigate_to("home")
        # Update recent commands
        command = self.command_input.text().strip()
        if command:
            self.recent_list.insertItem(0, command)
            self.no_commands_label.setVisible(False)
            self.recent_list.setVisible(True)
        self.command_input.clear()
        self.execute_btn.setText("Execute Command")
        self.execute_btn.setEnabled(True)
        self.voice_btn.setText("Voice Input")
        self.voice_btn.setEnabled(True)

    def on_main_error(self, error_message):
        self.parent.navigate_to("home")
        self.error_label.setText(f"Error: {error_message}")
        self.error_label.setVisible(True)
        self.execute_btn.setText("Execute Command")
        self.execute_btn.setEnabled(True)

    def activate_voice_input(self):
        self.voice_btn.setText("Listening...")
        self.voice_btn.setEnabled(False)
        self.execute_btn.setEnabled(False)

        try:
            from whisper_mic import WhisperMic
            mic = WhisperMic()
        except ImportError:
            print("Voice mode requires the 'whisper_mic' module. Please install it using 'pip install -r requirements-audio.txt'")
            sys.exit(1)

        print(f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_RESET} Listening for your command... (speak now)")
        try:
            objective = mic.listen()
        except Exception as e:
            print(f"{ANSI_RED}Error in capturing voice input: {e}{ANSI_RESET}")
            self.restore_voice_button()
            return

        self.command_input.setText(objective)
        self.voice_btn.setText("Voice Input")
        model = "fast-gpt" if self.model_combo.currentText() == "GPT-4o" else "fast-gemini"

        try:
            config = Config()
            if config.validation(model, voice_mode=False):
                raise HTTPError("Error occurred in validating API Key.", response=self)
            
            self.parent.navigate_to("processing")
            
            # Run main in a separate thread
            self.worker = MainWorker(model, objective)
            self.worker.finished.connect(self.on_main_finished)
            self.worker.error.connect(self.on_main_error)
            self.worker.start()
            
        except requests.RequestException as e:
            self.error_label.setText(f"Error: {str(e)}")
            self.error_label.setVisible(True)
            self.restore_voice_button()

    def restore_voice_button(self):
        self.voice_btn.setText("Voice Input")
        self.voice_btn.setEnabled(True)
        self.execute_btn.setEnabled(True)

    def reuse_command(self, item):
        self.command_input.setText(item.text())
        
    def refresh_data(self):
        self.validate_api_key()
        
        refresh_btn = self.sender()
        original_text = refresh_btn.text()
        refresh_btn.setText("Refreshing...")
        refresh_btn.setEnabled(False)
        
        QTimer.singleShot(1000, lambda: self.restore_refresh_button(refresh_btn, original_text))
    
    def restore_refresh_button(self, button, text):
        button.setText(text)
        button.setEnabled(True)