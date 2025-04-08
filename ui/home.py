import requests
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit,
    QPushButton, QListWidget, QHBoxLayout, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon


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
        title.setStyleSheet("""
            font-size: 32px; 
            font-weight: bold; 
            color: #60A5FA;
        """)
        layout.addWidget(title)

        subtitle = QLabel("Control your computer with natural language commands")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size: 14px; color: #9CA3AF;")
        layout.addWidget(subtitle)

        # Main Frame
        main_frame = QFrame()
        main_frame.setStyleSheet("background-color: #111827; border-radius: 12px; padding: 20px;")
        main_layout = QVBoxLayout(main_frame)
        main_layout.setSpacing(15)

        # Error Message Section
        self.error_label = QLabel()
        self.error_label.setStyleSheet("""
            color: #F87171; 
            padding: 10px; 
            background-color: #1F2937; 
            border-radius: 5px;
            font-weight: bold;
        """)
        self.error_label.setVisible(False)

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

        # Execute Button
        self.execute_btn = QPushButton("Execute Command")
        self.execute_btn.setIcon(QIcon("path/to/arrow_icon.png"))  # Replace with actual icon path
        self.execute_btn.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3B82F6, stop:1 #9333EA);
            color: white; 
            padding: 12px; 
            border-radius: 5px;
            font-size: 14px;
            font-weight: bold;
        """)
        main_layout.addWidget(self.execute_btn)

        # Recent Commands Section
        recent_container = QHBoxLayout()
        recent_label = QLabel("Recent commands")
        recent_label.setStyleSheet("color: #6B7280; font-size: 14px;")
        recent_container.addWidget(recent_label)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet("""
            background-color: #1F2937; 
            color: #9CA3AF; 
            padding: 5px 10px; 
            border-radius: 5px;
            font-size: 12px;
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

        # List of recent commands
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

        self.no_commands_label = QLabel("No recent commands")
        self.no_commands_label.setStyleSheet("color: #6B7280; padding: 10px; font-size: 14px;")
        self.no_commands_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.no_commands_label)

        layout.addWidget(main_frame)
        self.setLayout(layout)

        # Signal Connections
        self.command_input.returnPressed.connect(self.execute_command)
        self.execute_btn.clicked.connect(self.execute_command)
        self.recent_list.itemClicked.connect(self.reuse_command)
        self.model_combo.currentTextChanged.connect(self.validate_api_key)

        self.validate_api_key()

    def validate_api_key(self):
        model = "fast-gpt" if self.model_combo.currentText() == "GPT-4o" else "fast-gemini"
        try:
            self.set_loading_state(True)
            response = requests.post("http://127.0.0.1:8002/validate/", json={"model": model})
            if response.status_code == 404:
                self.show_error("Invalid API Key or API Key not found.")
                self.set_inputs_enabled(False)
            else:
                self.error_label.setVisible(False)
                self.set_inputs_enabled(True)
        except requests.RequestException as e:
            self.show_error(f"API validation failed: {e}")
            self.set_inputs_enabled(False)
        finally:
            self.set_loading_state(False)

    def execute_command(self):
        command = self.command_input.text().strip()
        if not command:
            return

        # Immediate visual feedback
        self.set_loading_state(True, btn_text="Processing...")

        model = "fast-gpt" if self.model_combo.currentText() == "GPT-4o" else "fast-gemini"
        
        def post_command():
            try:
                response = requests.post("http://127.0.0.1:8002/pipeline/", json={"model": model, "prompt": command})
                response.raise_for_status()

                self.recent_list.insertItem(0, command)
                self.command_input.clear()
                self.no_commands_label.setVisible(False)
            except requests.RequestException as e:
                self.show_error(f"Command execution failed: {e}")
            finally:
                self.set_loading_state(False, btn_text="Execute Command")

        # Run the network request in a separate thread to avoid UI freeze
        from threading import Thread
        Thread(target=post_command).start()


    def show_error(self, message):
        self.error_label.setText(message)
        self.error_label.setVisible(True)

    def set_inputs_enabled(self, state: bool):
        self.command_input.setEnabled(state)
        self.execute_btn.setEnabled(state)

    def set_loading_state(self, is_loading, btn_text=None):
        self.execute_btn.setEnabled(not is_loading)
        if btn_text:
            self.execute_btn.setText(btn_text)

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
