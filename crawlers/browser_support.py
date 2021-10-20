import random
import time


class HumanLikeScroll(object):
    def __init__(self, browser):
        self.browser = browser

    def scroll_down_once(self, pixels=200):
        for i in range(int(pixels)):
            self.browser.execute_script("window.scrollBy(0, 1);")
            # pyautogui.moveRel(random.randint(-3, 2), random.randint(-2, 3))  # mouse jitter on scroll
        return pixels

    def scroll_up_once(self, pixels=200):
        for i in range(int(pixels)):
            self.browser.execute_script("window.scrollBy(0, -1);")
            # pyautogui.moveRel(random.randint(-3, 2), random.randint(-2, 3))  # mouse jitter on scroll
        return pixels

    def scroll_down_by_pixels(self, pixels: int):
        if pixels > self.get_scroll_height() - self.get_current_offset():
            pixels = self.get_scroll_height() - self.get_current_offset()

        while pixels > 200:
            self.scroll_down_once(200)
            pixels -= 200
            time.sleep(round(random.uniform(0.3, 0.5), 2))

        self.scroll_down_once(pixels)

    def scroll_up_by_pixels(self, pixels: int):
        while pixels > 200:
            self.scroll_up_once(200)
            pixels -= 200
            time.sleep(round(random.uniform(0.3, 0.5), 2))

        self.scroll_up_once(pixels)

    def get_current_offset(self):
        return self.browser.execute_script('return window.pageYOffset;')
        # body = self.browser.find_element_by_tag_name('body')
        # return self.browser.execute_script("return arguments[0].scrollTop;", body)

    def get_scroll_height(self):
        return self.browser.execute_script("return document.documentElement.scrollHeight")

    def scroll_into_view(self, element):
        location = element.location
        x, y = location['x'], location['y']

        max_y = self.browser.execute_script("return window.innerHeight;")
        current_scroll_y = self.get_current_offset()
        if y < 0 or current_scroll_y < y < current_scroll_y + max_y:
            return

        if y > self.get_scroll_height():
            self.scroll_to_the_bottom()

        while y < current_scroll_y + 300:
            pixels = self.scroll_up_once()
            current_scroll_y = self.get_current_offset()
            time.sleep(round(random.uniform(0.3, 0.5), 2))

            if current_scroll_y == 0:
                break

        while y > current_scroll_y + max_y - 300:
            pixels = self.scroll_down_once()
            current_scroll_y = self.get_current_offset()
            time.sleep(round(random.uniform(0.3, 0.5), 2))

            if current_scroll_y == self.get_scroll_height():
                break

    def scroll_to_the_top(self):
        current_scroll_y = self.get_current_offset()
        self.scroll_up_by_pixels(current_scroll_y)

    def scroll_to_the_bottom(self):
        scroll_height = self.get_scroll_height()
        self.scroll_down_by_pixels(scroll_height)
