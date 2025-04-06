import requests
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, 
                            QFrame, QHBoxLayout, QApplication, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon

class SaveApiScreen(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        self.setMaximumWidth(800)

        # Header with Back Button
        header_layout = QHBoxLayout()
        
        back_btn = QPushButton("< Back")
        back_btn.setStyleSheet("""
            background-color: transparent; 
            color: #60A5FA; 
            font-size: 14px;
            font-weight: 500;
            border: none;
            padding: 5px;
            text-align: left;
        """)
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(lambda: self.parent.navigate_to("home"))
        header_layout.addWidget(back_btn, 0, Qt.AlignmentFlag.AlignLeft)
        
        # Title - centered in the remaining space
        title = QLabel("Enter your API Key")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 34px; font-weight: bold; color: #60A5FA; margin-bottom: 5px;")
        header_layout.addWidget(title, 1)
        
        # Add spacer to balance the back button
        spacer = QLabel("")
        spacer.setFixedWidth(back_btn.sizeHint().width())
        header_layout.addWidget(spacer, 0)
        
        layout.addLayout(header_layout)
        
        # Subtitle
        subtitle = QLabel("Your API key will be saved securely on your device")
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

        # Error Message (initially hidden)
        self.error_frame = QFrame()
        self.error_frame.setStyleSheet("""
            background-color: #331C1E; 
            border-radius: 8px; 
            border: 1px solid #EF4444;
            padding: 12px;
        """)
        error_layout = QVBoxLayout(self.error_frame)
        
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #F87171; font-size: 13px;")
        self.error_label.setWordWrap(True)
        error_layout.addWidget(self.error_label)
        
        main_layout.addWidget(self.error_frame)
        self.error_frame.setVisible(False)  # Initially hidden

        # Model Dropdown with Label
        model_label = QLabel("Choose Model:")
        model_label.setStyleSheet("color: #D1D5DB; font-size: 14px; font-weight: 500;")
        main_layout.addWidget(model_label)
        
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
        main_layout.addWidget(self.model_combo)
        
        # API Key Input with Label
        api_label = QLabel("API Key:")
        api_label.setStyleSheet("color: #D1D5DB; font-size: 14px; font-weight: 500; margin-top: 10px;")
        main_layout.addWidget(api_label)
        
        self.api_input = QLineEdit()
        self.api_input.setPlaceholderText("Enter your API key here...")
        self.api_input.setStyleSheet("""
            background-color: #1F2937; 
            color: #D1D5DB; 
            padding: 14px; 
            border-radius: 6px;
            font-size: 14px;
            border: 1px solid #374151;
            selection-background-color: #3B82F6;
        """)
        main_layout.addWidget(self.api_input)

        # Help Text
        help_text = QLabel("Your API key will only be stored locally and never shared.")
        help_text.setStyleSheet("color: #9CA3AF; font-size: 12px; margin-top: 4px;")
        main_layout.addWidget(help_text)

        # Save Button
        self.save_btn = QPushButton("Save API Key")
        self.save_btn.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3B82F6, stop:1 #9333EA);
            color: white; 
            padding: 14px; 
            border-radius: 6px;
            font-size: 15px;
            font-weight: bold;
            margin-top: 15px;
        """)
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        main_layout.addWidget(self.save_btn)

        layout.addWidget(main_frame)
        self.setLayout(layout)
        
        # Connect signals
        self.api_input.returnPressed.connect(self.save_api_key)
        self.save_btn.clicked.connect(self.save_api_key)

    def save_api_key(self):
        api_key = self.api_input.text().strip()
        if not api_key:
            self.show_error("API Key cannot be empty")
            return

        model = "fast-gpt" if self.model_combo.currentText() == "GPT-4o" else "fast-gemini"
        try:
            self.save_btn.setText("Saving...")
            self.save_btn.setEnabled(False)
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            
            response = requests.post(
                "http://127.0.0.1:8002/enter_api", 
                json={"model": model, "api_key": api_key},
                timeout=10
            )
            
            if response.status_code == 200:
                self.api_input.clear()
                self.error_frame.setVisible(False)
                QMessageBox.information(self, "Success", f"{self.model_combo.currentText()} API key saved successfully!")
                self.parent.navigate_to("home")
            else:
                error_msg = f"Server error: {response.status_code}"
                try:
                    error_data = response.json()
                    if "detail" in error_data:
                        error_msg = error_data["detail"]
                except:
                    pass
                self.show_error(error_msg)
                
        except requests.RequestException as e:
            self.show_error(f"Connection error: {str(e)}")
        finally:
            self.save_btn.setText("Save API Key")
            self.save_btn.setEnabled(True)
            QApplication.restoreOverrideCursor()
    
    def show_error(self, message):
        self.error_label.setText(message)
        self.error_frame.setVisible(True)