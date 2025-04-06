import sys
import os
import uvicorn
import threading
import time
import json
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox, QSplashScreen
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QIcon
from ui.home import HomeScreen
from ui.save_api import SaveApiScreen

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller temp folder
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Self Operating Computer")
        self.setStyleSheet("""
            QMainWindow {
                background-color: #030712;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #1F2937;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #4B5563;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        self.resize(800, 700)
        self.setMinimumSize(650, 550)
        
        # Create data directory if it doesn't exist
        self.data_dir = Path.home() / ".self_operating_computer"
        self.data_dir.mkdir(exist_ok=True)
        
        # Start FastAPI server
        self.server_started = self.start_fastapi_server()

        # Stacked widget for navigation
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Add screens
        self.home_screen = HomeScreen(self)
        self.save_api_screen = SaveApiScreen(self)

        self.stack.addWidget(self.home_screen)
        self.stack.addWidget(self.save_api_screen)

        # Start at home screen
        self.stack.setCurrentWidget(self.home_screen)

    def start_fastapi_server(self):
        def run_fastapi():
            try:
                # Add the 'operate' directory to sys.path
                operate_path = resource_path("operate")
                sys.path.append(operate_path)
                print(f"sys.path updated with: {operate_path}")
                
                # Set up recent commands storage
                self.setup_commands_storage()
                
                # Start the server
                uvicorn.run("main_server:app", host="127.0.0.1", port=8002, log_level="info")
            except Exception as e:
                print(f"FastAPI server error: {str(e)}")
                return False
                
        self.server_thread = threading.Thread(target=run_fastapi, daemon=True)
        self.server_thread.start()
        
        # Wait a bit and check if server is responsive
        time.sleep(2)
        try:
            import requests
            response = requests.get("http://127.0.0.1:8002/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def setup_commands_storage(self):
        """Set up storage for recent commands"""
        commands_file = self.data_dir / "recent_commands.json"
        if not commands_file.exists():
            with open(commands_file, 'w') as f:
                json.dump({"commands": []}, f)
    
    def navigate_to(self, screen_name):
        if screen_name == "home":
            self.stack.setCurrentWidget(self.home_screen)
            # Refresh data when returning to home
            self.home_screen.validate_api_key()
            self.home_screen.load_recent_commands()
        elif screen_name == "save_api":
            self.stack.setCurrentWidget(self.save_api_screen)

def show_splash_screen():
    """Show a splash screen while loading"""
    splash_pixmap = QPixmap(resource_path("assets/splash.png"))
    if splash_pixmap.isNull():
        # Create a default splash if image not found
        splash_pixmap = QPixmap(400, 300)
        splash_pixmap.fill(Qt.GlobalColor.black)
    
    splash = QSplashScreen(splash_pixmap)
    splash.show()
    return splash

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Self Operating Computer")
    
    # Set app icon
    icon_path = resource_path("assets/icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Show splash screen
    splash = show_splash_screen()
    
    # Create and show main window after a delay
    def show_main_window():
        window = MainApp()
        
        # Check if server started successfully
        if not window.server_started:
            QMessageBox.critical(
                None, 
                "Server Error",
                "Failed to start the FastAPI server. Please check logs and ensure port 8002 is available."
            )
        
        window.show()
        splash.finish(window)
    
    # Use timer to show splash for a minimum time
    QTimer.singleShot(1500, show_main_window)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()