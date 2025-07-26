import random
import asyncio
import time

def human_like_mouse_move(page, target_selector):
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
        time.sleep(random.uniform(0.005, 0.02))  # very fast movement, small pauses
