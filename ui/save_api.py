import requests
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QFrame, QHBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtCore import QCoreApplication

class SaveApiScreen(QWidget):
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
        title = QLabel("Enter your API Key")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #60A5FA; margin-bottom: 40px;")
        layout.addWidget(title)

        # Main Content Frame
        main_frame = QFrame()
        main_frame.setStyleSheet("background-color: #111827; border-radius: 12px; padding: 20px;")
        main_layout = QVBoxLayout(main_frame)
        main_layout.setSpacing(15)

        # Top row with back button
        top_row = QHBoxLayout()
        self.back_btn = QPushButton("← Back")
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #1F2937; 
                color: #93C5FD;
                padding: 8px 12px;
                border: 1px solid #3B82F6;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #374151;
            }
        """)
        self.back_btn.clicked.connect(lambda: self.parent.navigate_to("home"))
        top_row.addWidget(self.back_btn)
        top_row.addStretch()
        main_layout.addLayout(top_row)

        # Error Message
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #F87171; margin-bottom: 10px; font-weight: bold;")
        self.error_label.setWordWrap(True)
        self.error_label.setVisible(False)
        main_layout.addWidget(self.error_label)

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

        # API Key Input
        self.api_input = QLineEdit()
        self.api_input.setPlaceholderText("Enter your API key...")
        self.api_input.setStyleSheet("""
            background-color: #1F2937; 
            color: #D1D5DB; 
            padding: 12px; 
            border-radius: 5px;
            font-size: 14px;
        """)
        main_layout.addWidget(self.api_input)

        # Save Button
        self.save_btn = QPushButton("Save API Key")
        self.save_btn.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3B82F6, stop:1 #9333EA);
            color: white; 
            padding: 12px; 
            border-radius: 5px;
            font-size: 14px;
            font-weight: bold;
        """)
        main_layout.addWidget(self.save_btn)

        layout.addWidget(main_frame)
        self.setLayout(layout)

        # Connect signals
        self.api_input.returnPressed.connect(self.save_api_key)
        self.save_btn.clicked.connect(self.save_api_key)

    def save_api_key(self):
        api_key = self.api_input.text().strip()
        if not api_key:
            self.display_error("API Key cannot be empty")
            return

        model = "fast-gpt" if self.model_combo.currentText() == "GPT-4o" else "fast-gemini"

        # Show loading state
        self.save_btn.setText("Saving...")
        self.save_btn.setEnabled(False)
        self.error_label.setVisible(False)
        
        # Force UI to update before long task
        QCoreApplication.processEvents()

        try:
            response = requests.post(
                "http://127.0.0.1:8002/enter_api",
                json={"model": model, "api_key": api_key},
                timeout=5
            )
            response.raise_for_status()
            self.api_input.clear()
            self.error_label.setVisible(False)
            self.parent.navigate_to("home")

        except requests.exceptions.HTTPError as http_err:
            try:
                err_msg = response.json().get("detail", str(http_err))
            except Exception:
                err_msg = str(http_err)
            self.display_error(f"HTTP error: {err_msg}")

        except requests.exceptions.ConnectionError:
            self.display_error("Unable to connect to server. Is the backend running?")

        except requests.exceptions.Timeout:
            self.display_error("Request timed out. Please try again.")

        except requests.RequestException as e:
            self.display_error(f"Unexpected error: {str(e)}")

        finally:
            self.save_btn.setText("Save API Key")
            self.save_btn.setEnabled(True)

    def display_error(self, message: str):
        self.error_label.setText(message)
        self.error_label.setVisible(True)
