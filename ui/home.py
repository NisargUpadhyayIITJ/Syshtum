import requests
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, 
                            QListWidget, QHBoxLayout, QFrame, QMessageBox, QApplication)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QFont

class HomeScreen(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        self.setMaximumWidth(800)

        # Title
        title = QLabel("Self Operating Computer")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 34px; font-weight: bold; color: #60A5FA; margin-bottom: 5px;")
        layout.addWidget(title)

        subtitle = QLabel("Control your computer with natural language commands")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size: 15px; color: #9CA3AF; margin-bottom: 25px;")
        layout.addWidget(subtitle)

        # Main Content Frame
        main_frame = QFrame()
        main_frame.setStyleSheet("""
            background-color: #111827; 
            border-radius: 12px; 
            padding: 25px;
            border: 1px solid #1F2937;
        """)
        main_layout = QVBoxLayout(main_frame)
        main_layout.setSpacing(18)

        # API Error Message
        self.error_frame = QFrame()
        self.error_frame.setStyleSheet("""
            background-color: #331C1E; 
            border-radius: 8px; 
            border: 1px solid #EF4444;
            padding: 2px;
        """)
        error_layout = QHBoxLayout(self.error_frame)
        
        self.error_label = QLabel("API Key not found or invalid")
        self.error_label.setStyleSheet("color: #F87171; font-size: 13px;")
        error_layout.addWidget(self.error_label, 1)
        
        enter_api_btn = QPushButton("Enter API Key")
        enter_api_btn.setStyleSheet("""
            background-color: #374151; 
            color: white; 
            padding: 8px 15px; 
            border-radius: 6px;
            font-size: 13px;
            font-weight: 500;
        """)
        enter_api_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        enter_api_btn.clicked.connect(lambda: self.parent.navigate_to("save_api"))
        error_layout.addWidget(enter_api_btn)
        
        main_layout.addWidget(self.error_frame)

        # Model Dropdown with Label
        model_container = QHBoxLayout()
        model_label = QLabel("Model:")
        model_label.setStyleSheet("color: #D1D5DB; font-size: 14px; font-weight: 500;")
        model_container.addWidget(model_label)
        
        self.model_combo = QComboBox()
        self.model_combo.addItems(["GPT-4o", "Gemini"])
        self.model_combo.setStyleSheet("""
            background-color: #1F2937; 
            color: #D1D5DB; 
            padding: 12px;
            border-radius: 6px;
            selection-background-color: #2563EB;
            border: 1px solid #374151;
            min-height: 20px;
        """)
        self.model_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        model_container.addWidget(self.model_combo, 1)
        main_layout.addLayout(model_container)

        # Command Input
        command_label = QLabel("Command:")
        command_label.setStyleSheet("color: #D1D5DB; font-size: 14px; font-weight: 500;")
        main_layout.addWidget(command_label)
        
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Enter your command here...")
        self.command_input.setStyleSheet("""
            background-color: #1F2937; 
            color: #D1D5DB; 
            padding: 14px; 
            border-radius: 6px;
            font-size: 14px;
            border: 1px solid #374151;
            selection-background-color: #3B82F6;
        """)
        main_layout.addWidget(self.command_input)

        # Execute Button
        self.execute_btn = QPushButton("Execute Command")
        self.execute_btn.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3B82F6, stop:1 #9333EA);
            color: white; 
            padding: 14px; 
            border-radius: 6px;
            font-size: 15px;
            font-weight: bold;
        """)
        self.execute_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        main_layout.addWidget(self.execute_btn)

        # Recent Commands Section with Refresh Button
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #1F2937; margin-top: 10px; margin-bottom: 10px;")
        main_layout.addWidget(separator)
        
        recent_container = QHBoxLayout()
        
        recent_label = QLabel("Recent Commands")
        recent_label.setStyleSheet("color: #D1D5DB; font-size: 15px; font-weight: 500;")
        recent_container.addWidget(recent_label)
        
        # Add history and refresh buttons
        history_btn = QPushButton("History")
        history_btn.setStyleSheet("""
            background-color: #1F2937; 
            color: #D1D5DB; 
            padding: 6px 12px; 
            border-radius: 5px;
            font-size: 12px;
            border: 1px solid #374151;
        """)
        history_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        recent_container.addWidget(history_btn, 0, Qt.AlignmentFlag.AlignRight)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet("""
            background-color: #1F2937; 
            color: #D1D5DB; 
            padding: 6px 12px; 
            border-radius: 5px;
            font-size: 12px;
            border: 1px solid #374151;
            margin-left: 8px;
        """)
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.clicked.connect(self.refresh_data)
        recent_container.addWidget(refresh_btn, 0, Qt.AlignmentFlag.AlignRight)
        
        main_layout.addLayout(recent_container)

        self.recent_list = QListWidget()
        self.recent_list.setStyleSheet("""
            background-color: #1F2937; 
            color: #D1D5DB; 
            border-radius: 6px;
            padding: 8px;
            font-size: 14px;
            border: 1px solid #374151;
        """)
        self.recent_list.setMinimumHeight(120)
        self.recent_list.setMaximumHeight(150)
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
        self.load_recent_commands()

    def validate_api_key(self):
        model = "fast-gpt" if self.model_combo.currentText() == "GPT-4o" else "fast-gemini"
        try:
            response = requests.post("http://127.0.0.1:8002/validate/", json={"model": model}, timeout=5)
            if response.status_code == 200:
                self.error_frame.setVisible(False)
                self.execute_btn.setEnabled(True)
                self.command_input.setEnabled(True)
            else:
                self.error_label.setText(f"API Key not found or invalid for {self.model_combo.currentText()}")
                self.error_frame.setVisible(True)
                self.execute_btn.setEnabled(False)
                self.command_input.setEnabled(False)
        except requests.RequestException as e:
            self.error_label.setText(f"Connection error: {str(e)}")
            self.error_frame.setVisible(True)
            self.execute_btn.setEnabled(False)
            self.command_input.setEnabled(False)

    def execute_command(self):
        command = self.command_input.text().strip()
        if not command:
            return

        model = "fast-gpt" if self.model_combo.currentText() == "GPT-4o" else "fast-gemini"
        try:
            self.execute_btn.setText("Processing...")
            self.execute_btn.setEnabled(False)
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            
            response = requests.post(
                "http://127.0.0.1:8002/pipeline/", 
                json={"model": model, "prompt": command},
                timeout=60  # Longer timeout for command execution
            )
            
            if response.status_code == 200:
                self.add_to_recent_commands(command)
                self.command_input.clear()
                
                # Hide the "No recent commands" label when we have commands
                self.no_commands_label.setVisible(False)
                self.recent_list.setVisible(True)
            else:
                error_msg = f"Server error: {response.status_code}"
                try:
                    error_data = response.json()
                    if "detail" in error_data:
                        error_msg = error_data["detail"]
                except:
                    pass
                QMessageBox.critical(self, "Error", error_msg)
                
        except requests.RequestException as e:
            QMessageBox.critical(self, "Connection Error", f"Failed to execute command: {str(e)}")
        finally:
            self.execute_btn.setText("Execute Command")
            self.execute_btn.setEnabled(True)
            QApplication.restoreOverrideCursor()

    def reuse_command(self, item):
        self.command_input.setText(item.text())
        self.command_input.setFocus()
        
    def refresh_data(self):
        # Refresh API validation status
        self.validate_api_key()
        
        # Visual feedback for refresh action
        refresh_btn = self.sender()
        original_text = refresh_btn.text()
        refresh_btn.setText("Refreshing...")
        refresh_btn.setEnabled(False)
        
        # Use QTimer to restore the button after a short delay
        QTimer.singleShot(1000, lambda: self.restore_refresh_button(refresh_btn, original_text))
        
        # Reload recent commands
        self.load_recent_commands()
    
    def restore_refresh_button(self, button, text):
        button.setText(text)
        button.setEnabled(True)
        
    def add_to_recent_commands(self, command):
        # Add to UI list
        self.recent_list.insertItem(0, command)
        
        # Also save to backend
        try:
            requests.post(
                "http://127.0.0.1:8002/save_command/", 
                json={"command": command},
                timeout=5
            )
        except requests.RequestException:
            # Silently fail - not critical
            pass
            
    def load_recent_commands(self):
        try:
            response = requests.get("http://127.0.0.1:8002/recent_commands/", timeout=5)
            if response.status_code == 200:
                commands = response.json().get("commands", [])
                self.recent_list.clear()
                
                if commands:
                    for cmd in commands:
                        self.recent_list.addItem(cmd)
                    self.no_commands_label.setVisible(False)
                    self.recent_list.setVisible(True)
                else:
                    self.no_commands_label.setVisible(True)
                    self.recent_list.setVisible(False)
        except requests.RequestException:
            # Not critical, just show empty list
            self.no_commands_label.setVisible(True)
            self.recent_list.setVisible(False)