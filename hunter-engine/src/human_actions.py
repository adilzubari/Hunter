# Simulates human-like interactions for anti-bot evasion.
# - Provides methods for mouse movement and typing with randomness.
# - Used by domain scripts to interact with web pages more naturally.
import random
import time
import logging

class HumanActions:
    @staticmethod
    def mouse_move(page, target_selector):
        box = page.locator(target_selector).bounding_box()
        if box is None:
            raise Exception("Search box bounding box not found")
        start_x = random.randint(0, int(box['x'] + box['width']//2))
        start_y = random.randint(0, int(box['y'] + box['height']//2))
        end_x = box['x'] + box['width'] / 2
        end_y = box['y'] + box['height'] / 2
        steps = random.randint(20, 40)
        for step in range(steps):
            intermediate_x = start_x + (end_x - start_x) * (step / steps)
            intermediate_y = start_y + (end_y - start_y) * (step / steps)
            page.mouse.move(intermediate_x, intermediate_y)
            time.sleep(random.uniform(0.005, 0.02))

    @staticmethod
    def typing(text, page):
        for word in text.split():
            for char in word:
                page.keyboard.type(char)
                delay = random.uniform(0.05, 0.25)
                time.sleep(delay)
            if random.random() < 0.4:
                pause = random.uniform(0.3, 1.2)
                logging.debug(f"Pausing for {pause:.2f}s to simulate thinking...")
                time.sleep(pause)
            page.keyboard.type(' ')
            time.sleep(random.uniform(0.08, 0.18))
