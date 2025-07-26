import random
import asyncio
import time
import logging

def human_like_typing(text, page):
    for word in text.split():
        for char in word:
            page.keyboard.type(char)
            delay = random.uniform(0.05, 0.25)
            time.sleep(delay)

        # Random short pause after some words to simulate "thinking"
        if random.random() < 0.4:
            pause = random.uniform(0.3, 1.2)
            logging.debug(f"Pausing for {pause:.2f}s to simulate thinking...")
            time.sleep(pause)

        # Simulate space between words
        page.keyboard.type(' ')
        time.sleep(random.uniform(0.08, 0.18))