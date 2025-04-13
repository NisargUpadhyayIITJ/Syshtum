import sys
import os
import uvicorn
import threading
import time
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from ui.home import HomeScreen
from ui.save_api import SaveApiScreen
from ui.processing import ProcessingScreen  # Import the new screen

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Self Operating Computer")
        self.setStyleSheet("background-color: #000000;")
        self.resize(800, 600)

        # Stacked widget for navigation
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Add screens
        self.home_screen = HomeScreen(self)
        self.save_api_screen = SaveApiScreen(self)
        self.processing_screen = ProcessingScreen(self)  # Add processing screen

        self.stack.addWidget(self.home_screen)
        self.stack.addWidget(self.save_api_screen)
        self.stack.addWidget(self.processing_screen)

        self.stack.setCurrentWidget(self.home_screen)

    def start_fastapi_server(self):
        def run_fastapi():
            try:
                operate_path = resource_path("operate")
                sys.path.append(operate_path)
                print(f"sys.path updated with: {operate_path}")
                uvicorn.run("main_server:app", host="127.0.0.1", port=8002, log_level="info")
            except Exception as e:
                print(f"FastAPI failed: {str(e)}")

        threading.Thread(target=run_fastapi, daemon=True).start()
        time.sleep(2)

    def navigate_to(self, screen_name):
        if screen_name == "home":
            self.stack.setCurrentWidget(self.home_screen)
        elif screen_name == "save_api":
            self.stack.setCurrentWidget(self.save_api_screen)
        elif screen_name == "processing":
            self.stack.setCurrentWidget(self.processing_screen)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())