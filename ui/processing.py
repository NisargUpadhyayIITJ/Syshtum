# ui/processing.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt

class ProcessingScreen(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMaximumWidth(800)

        # Title
        title = QLabel("Processing Your Command")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #60A5FA; margin-bottom: 20px;")
        layout.addWidget(title)

        # Loading Animation (Indeterminate Progress Bar)
        progress = QProgressBar()
        progress.setRange(0, 0)  # Indeterminate mode
        progress.setStyleSheet("""
            QProgressBar {
                background-color: #1F2937;
                border-radius: 5px;
                height: 20px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3B82F6, stop:1 #9333EA);
                border-radius: 5px;
            }
        """)
        layout.addWidget(progress)

        # Status Message
        status = QLabel("Please wait while we process your request...")
        status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status.setStyleSheet("font-size: 16px; color: #D1D5DB;")
        layout.addWidget(status)

        self.setLayout(layout)