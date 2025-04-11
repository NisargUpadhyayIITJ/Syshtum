import requests
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QListWidget, QHBoxLayout, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from operate.config import Config
from operate.operate import main

class RequestException(IOError):
    """There was an ambiguous exception that occurred while handling your
    request.
    """

    def __init__(self, *args, **kwargs):
        """Initialize RequestException with `request` and `response` objects."""
        response = kwargs.pop("response", None)
        self.response = response
        self.request = kwargs.pop("request", None)
        if response is not None and not self.request and hasattr(response, "request"):
            self.request = self.response.request
        super().__init__(*args, **kwargs)

class HTTPError(RequestException):
    """An HTTP error occurred."""

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

        # Title
        title = QLabel("Self Operating Computer")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #60A5FA; margin-bottom: 5px;")
        layout.addWidget(title)

        subtitle = QLabel("Control your computer with natural language commands")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size: 14px; color: #9CA3AF; margin-bottom: 20px;")
        layout.addWidget(subtitle)

        # Main Content Frame
        main_frame = QFrame()
        main_frame.setStyleSheet("background-color: #111827; border-radius: 12px; padding: 20px;")
        main_layout = QVBoxLayout(main_frame)
        main_layout.setSpacing(15)

        # API Error Message
        self.error_label = QLabel("Invalid API Key or API Key not found")
        self.error_label.setStyleSheet("color: #F87171; padding: 10px; background-color: #1F2937; border-radius: 5px;")
        
        # Error message container with button
        error_container = QHBoxLayout()
        error_container.addWidget(self.error_label, 1)
        
        enter_api_btn = QPushButton("Enter API Key")
        enter_api_btn.setStyleSheet("""
            background-color: #374151; 
            color: white; 
            padding: 8px 15px; 
            border-radius: 5px;
            font-size: 13px;
        """)
        enter_api_btn.clicked.connect(lambda: self.parent.navigate_to("save_api"))
        error_container.addWidget(enter_api_btn)
        
        main_layout.addLayout(error_container)

        # Model Dropdown
        self.model_combo = QComboBox()
        self.model_combo.addItems(["GPT-4o", "Gemini"])
        self.model_combo.setStyleSheet("""
            background-color: #1F2937; 
            color: #D1D5DB; 
            padding: 12px;
            border-radius: 5px;
            selection-background-color: #2563EB;
        """)
        main_layout.addWidget(self.model_combo)

        # Command Input
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Enter your command...")
        self.command_input.setStyleSheet("""
            background-color: #1F2937; 
            color: #D1D5DB; 
            padding: 12px; 
            border-radius: 5px;
            font-size: 14px;
        """)
        main_layout.addWidget(self.command_input)

        # Buttons Container - Execute and Voice Input
        buttons_container = QHBoxLayout()
        
        # Execute Button
        self.execute_btn = QPushButton("Execute Command")
        self.execute_btn.setIcon(QIcon("path/to/arrow_icon.png"))  # Add a placeholder for the arrow icon
        self.execute_btn.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3B82F6, stop:1 #9333EA);
            color: white; 
            padding: 12px; 
            border-radius: 5px;
            font-size: 14px;
            font-weight: bold;
        """)
        buttons_container.addWidget(self.execute_btn)
        
        # Voice Input Button
        self.voice_btn = QPushButton("Voice Input")
        self.voice_btn.setIcon(QIcon("path/to/mic_icon.png"))  # Add a placeholder for the mic icon
        self.voice_btn.setStyleSheet("""
            background-color: #1F2937;
            color: white; 
            padding: 12px; 
            border-radius: 5px;
            font-size: 14px;
            font-weight: bold;
        """)
        self.voice_btn.clicked.connect(self.activate_voice_input)
        buttons_container.addWidget(self.voice_btn)
        
        main_layout.addLayout(buttons_container)

        # Recent Commands Section with Refresh Button
        recent_container = QHBoxLayout()
        
        recent_label = QLabel("Recent commands")
        recent_label.setStyleSheet("color: #6B7280; font-size: 14px;")
        recent_container.addWidget(recent_label)
        
        # Add refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet("""
            background-color: #1F2937; 
            color: #9CA3AF; 
            padding: 5px 10px; 
            border-radius: 5px;
            font-size: 12px;
            margin-right: 8px;
        """)
        refresh_btn.clicked.connect(self.refresh_data)
        recent_container.addWidget(refresh_btn, 0, Qt.AlignmentFlag.AlignRight)
        
        history_btn = QPushButton("History")
        history_btn.setStyleSheet("""
            background-color: #1F2937; 
            color: #9CA3AF; 
            padding: 5px 10px; 
            border-radius: 5px;
            font-size: 12px;
        """)
        recent_container.addWidget(history_btn, 0, Qt.AlignmentFlag.AlignRight)
        
        main_layout.addLayout(recent_container)

        self.recent_list = QListWidget()
        self.recent_list.setStyleSheet("""
            background-color: #1F2937; 
            color: #D1D5DB; 
            border-radius: 5px;
            padding: 5px;
            font-size: 14px;
        """)
        self.recent_list.setMaximumHeight(100)
        main_layout.addWidget(self.recent_list)

        # Add empty placeholder if no recent commands
        self.no_commands_label = QLabel("No recent commands")
        self.no_commands_label.setStyleSheet("color: #6B7280; padding: 10px; font-size: 14px;")
        self.no_commands_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.no_commands_label)

        layout.addWidget(main_frame)
        self.setLayout(layout)
        
        # Connect signals
        self.command_input.returnPressed.connect(self.execute_command)
        self.execute_btn.clicked.connect(self.execute_command)
        self.recent_list.itemClicked.connect(self.reuse_command)
        self.model_combo.currentTextChanged.connect(self.validate_api_key)
        
        # Initial setup
        self.validate_api_key()

    def validate_api_key(self):
        model = "fast-gpt" if self.model_combo.currentText() == "GPT-4o" else "fast-gemini"
        try:
            
            # response = requests.post("http://127.0.0.1:8002/validate/", json={"model": model})
            # if response.status_code == 404:
            config = Config()
            if(config.validation(model, voice_mode=False)):
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
            self.execute_btn.setText("Processing...")
            self.execute_btn.setEnabled(False)
            # response = requests.post("http://127.0.0.1:8002/pipeline/", json={"model": model, "prompt": command})
            # response.raise_for_status()
            config = Config()
            if(config.validation(model, voice_mode=False)):
                raise HTTPError("Error occured in validating API Key.", response=self)
            main(
                model = model,
                terminal_prompt = command
            )
            
            self.recent_list.insertItem(0, command)
            self.command_input.clear()
            
            # Hide the "No recent commands" label when we have commands
            self.no_commands_label.setVisible(False)
            self.recent_list.setVisible(True)
        except requests.RequestException as e:
            self.error_label.setText(f"Error: {str(e)}")
            self.error_label.setVisible(True)
        finally:
            self.execute_btn.setText("Execute Command")
            self.execute_btn.setEnabled(True)

    def activate_voice_input(self):
        # Placeholder for voice input functionality
        self.voice_btn.setText("Listening...")
        self.voice_btn.setEnabled(False)

        model = "fast-gpt" if self.model_combo.currentText() == "GPT-4o" else "fast-gemini"

        self.execute_btn.setText("Processing...")
        self.execute_btn.setEnabled(False)
        # response = requests.post("http://127.0.0.1:8002/pipeline/", json={"model": model, "prompt": command})
        # response.raise_for_status()
        config = Config()
        if(config.validation(model, voice_mode=False)):
            raise HTTPError("Error occured in validating API Key.", response=self)
        main(
            model = model,
            voice_mode=True
        )
        
        # Here you would implement actual voice recognition
        # For now, just simulate processing
        
    def finish_voice_input(self):
        # Reset button state
        self.voice_btn.setText("Voice Input")
        self.voice_btn.setEnabled(True)
        
        # In a real implementation, you would set the recognized text to the command input
        # self.command_input.setText(recognized_text)

    def reuse_command(self, item):
        self.command_input.setText(item.text())
        
    def refresh_data(self):
        # Refresh API validation status
        self.validate_api_key()
        
        # You could also implement fetching recent commands from storage/database here
        # For now, it just refreshes the validation status
        
        # Visual feedback for refresh action
        refresh_btn = self.sender()
        original_text = refresh_btn.text()
        refresh_btn.setText("Refreshing...")
        refresh_btn.setEnabled(False)
        
        # Use QTimer to restore the button after a short delay
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(1000, lambda: self.restore_refresh_button(refresh_btn, original_text))
    
    def restore_refresh_button(self, button, text):
        button.setText(text)
        button.setEnabled(True)