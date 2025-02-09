import pyautogui
import platform
import time
import math
from loguru import logger

from utils.misc import convert_percent_to_decimal


class OperatingSystem:
    def write(self, content):
        logger.info("Write function executed by OS.")
        try:
            content = content.replace("\\n", "\n")
            for char in content:
                pyautogui.write(char)
        except Exception as e:
            print("[OperatingSystem][write] error:", e)

    def press(self, keys):
        logger.info("Press function executed by OS.")
        try:
            for key in keys:
                pyautogui.keyDown(key)
            time.sleep(0.1)
            for key in keys:
                pyautogui.keyUp(key)
        except Exception as e:
            print("[OperatingSystem][press] error:", e)

    def mouse(self, click_detail):
        logger.info("Click function executed by OS.")
        try:
            x = convert_percent_to_decimal(click_detail.get("x"))
            y = convert_percent_to_decimal(click_detail.get("y"))

            if click_detail and isinstance(x, float) and isinstance(y, float):
                self.click_at_percentage(x, y)

        except Exception as e:
            print("[OperatingSystem][mouse] error:", e)

    def click_at_percentage(
        self,
        x_percentage,
        y_percentage,
        duration=0.8,
    ):
        logger.info("Percentage calculated with click function executed by OS.")
        try:
            if(int(x_percentage) < 1):
                screen_width, screen_height = pyautogui.size()
                x_pixel = int(screen_width * float(x_percentage))
                y_pixel = int(screen_height * float(y_percentage))
            else:
                x_pixel = x_percentage
                y_pixel = y_percentage

            pyautogui.moveTo(x_pixel, y_pixel, duration, pyautogui.easeInBounce)
            logger.debug(f"Moving to X: {x_pixel}, Y: {y_pixel}")

            pyautogui.click(x_pixel, y_pixel)
        except Exception as e:
            print("[OperatingSystem][click_at_percentage] error:", e)

    def scroll(self):
        logger.info("Scroll function executed by OS.")
        try:
            pyautogui.scroll(-10)

        except Exception as e:
            print("[OperatingSystem][mouse] error:", e)
    
