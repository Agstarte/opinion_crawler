import os
import pickle
import re
import threading
import time

from selenium import webdriver
import queue

from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, \
    ElementClickInterceptedException
from selenium.webdriver import ActionChains

from .browser_support import HumanLikeScroll
from . import utils


class CeneoCrawler(object):
    def __init__(self):
        self.browser = utils.set_browser()
        self.browser.get('https://www.ceneo.pl')
        self.accept_cookies()

        self.categories_crawler = CrawlCategories(self.browser)
        self.products_crawler = CrawlProducts(self.browser)
        self.opinions_crawler = CrawlOpinions(self.browser)

    def accept_cookies(self):
        try:
            accept_button = self.browser.find_element_by_xpath('//button[contains(@class,"cookie-monster-agree")]')
            accept_button.click()
            return True
        except NoSuchElementException:
            return False
        except ElementNotInteractableException:
            time.sleep(1)
            return self.accept_cookies()

    def crawl(self):
        self.categories_crawler.find_subpages()
        self.products_crawler.find_products()

        while not self.categories_crawler.categories_queue.empty():
            category = self.categories_crawler.categories_queue.get()
            self.crawl_category(category)

    def crawl_category(self, category_url):
        utils.logger.info(f'Got page: {category_url}')
        self.browser.get(category_url)
        while True:
            self.categories_crawler.find_subpages()
            self.products_crawler.find_products()
            if not self.categories_crawler.get_next_category_page():
                break
            utils.logger.info(f'Next page of: {category_url}')

        while not self.products_crawler.products_queue.empty():
            product = self.products_crawler.products_queue.get()
            self.crawl_product(product)

    def scrape_queued_products(self):
        while not self.products_crawler.products_queue.empty():
            product = self.products_crawler.products_queue.get()
            self.crawl_product(product)

    def crawl_product(self, product_url):
        utils.logger.info(f'Got product page: {product_url}')
        self.browser.get(product_url)
        self.scrape_opinions()

    def scrape_opinions(self):
        self.opinions_crawler.find_opinions()
        count = 0
        while not self.opinions_crawler.opinions_queue.empty():
            opinion = self.opinions_crawler.opinions_queue.get()
            utils.append_row_to_csv('ceneo_negative.csv', opinion)
            count += 1

        utils.logger.info(f'Fetched {count} opinions')

    def __del__(self):
        self.browser.close()


class CrawlCategories(object):
    categories_queue = queue.Queue()
    all_categories = set()

    def __init__(self, browser: webdriver):
        self.browser = browser

        self.load_pickle()
        save_object_every_minute(self.categories_queue, 'categories_queue.pkl')
        save_object_every_minute(self.all_categories, 'all_categories.pkl')

    def load_pickle(self):
        if os.path.isfile('categories_queue.pkl'):
            categories_list = pickle.load(open('categories_queue.pkl', 'rb'))
            for category in categories_list:
                self.categories_queue.put(category)
        if os.path.isfile('all_categories.pkl'):
            self.all_categories = pickle.load(open('all_categories.pkl', 'rb'))

    def find_subpages(self):
        urls = self.browser.find_elements_by_xpath('//a')
        urls = [url.get_attribute('href') for url in urls if url.get_attribute('href')]

        subpage_regex = re.compile(r"https://www\.ceneo\.pl\/[A-Za-z_-]+?\/?$")

        for url in urls:
            if re.search(subpage_regex, url):
                if url not in self.all_categories:
                    self.all_categories.add(url)
                    self.categories_queue.put(url)

    def get_next_category_page(self):
        try:
            next_page_button = self.browser.find_element_by_xpath('//a[@class="pagination__item pagination__next"]')
            scroll = HumanLikeScroll(self.browser)
            scroll.scroll_into_view(next_page_button)
            next_page_button.click()
            return True
        except NoSuchElementException:
            return False
        except ElementClickInterceptedException:
            scroll.scroll_down_once()
            next_page_button.click()
            return True


class CrawlProducts(object):
    products_queue = queue.Queue()
    all_products = set()

    def __init__(self, browser: webdriver):
        self.browser = browser

        self.load_pickle()
        save_object_every_minute(self.products_queue, 'products_queue.pkl')
        save_object_every_minute(self.all_products, 'all_products.pkl')

    def load_pickle(self):
        if os.path.isfile('products_queue.pkl'):
            products_list = pickle.load(open('products_queue.pkl', 'rb'))
            for product in products_list:
                self.products_queue.put(product)
        if os.path.isfile('all_products.pkl'):
            self.all_products = pickle.load(open('all_products.pkl', 'rb'))

    def find_products(self):
        products = self.browser.find_elements_by_xpath('//span[@class="prod-review__stars"]')
        for product in products:
            url = product.find_element_by_xpath('.//a').get_attribute('href')
            rate = product.find_element_by_xpath('.//span[@class="product-score"]').text
            if float(rate.replace(',', '.')) < 4:
                if url not in self.all_products:
                    self.all_products.add(url)
                    self.products_queue.put(url)


class CrawlOpinions(object):
    opinions_queue = queue.Queue()

    def __init__(self, browser: webdriver):
        self.browser = browser
        self.scroll = HumanLikeScroll(browser)

    def find_opinions(self):
        if not self.get_reviews_page():
            return

        while True:
            self.find_visible_opinions()
            if not self.get_next_reviews_page():
                break

    def get_reviews_page(self):
        try:
            reviews_tab = self.browser.find_element_by_xpath('//a[contains(@href,"reviews")]')
            self.scroll.scroll_into_view(reviews_tab)
            reviews_tab.click()
            return True
        except NoSuchElementException:
            return False
        except ElementClickInterceptedException:
            self.scroll.scroll_down_once()
            reviews_tab.click()
            return True

    def find_visible_opinions(self):
        user_posts = self.browser.find_elements_by_xpath('//div[contains(@class,"user-post") '
                                                         'and contains(@class,"product-review")]')
        try:
            product_name = self.browser.find_element_by_xpath('.//div[@class="product-top__title"]').text
        except NoSuchElementException:
            product_name = ''
        current_url = self.browser.current_url

        for post in user_posts:
            try:
                rate = post.find_element_by_xpath('.//span[@class="user-post__score-count"]').text
                text = post.find_element_by_xpath('.//div[@class="user-post__text"]').text
                while rate == '':
                    time.sleep(1)
                    rate = post.find_element_by_xpath('.//span[@class="user-post__score-count"]').text
                    text = post.find_element_by_xpath('.//div[@class="user-post__text"]').text

                self.opinions_queue.put({
                    'rate': rate,
                    'text': text.replace('\n', '\\n'),
                    'product_name': product_name,
                    'url': current_url
                })
            except NoSuchElementException:
                continue

    def get_next_reviews_page(self):
        try:
            next_page_button = self.browser.find_element_by_xpath('//a[@class="pagination__item pagination__next"]')
            self.scroll.scroll_into_view(next_page_button)
            next_page_button.click()
            return True
        except NoSuchElementException:
            return False
        except ElementClickInterceptedException:
            self.scroll.scroll_down_once()
            next_page_button.click()
            return True
        except ElementNotInteractableException:
            return False


def save_object_every_minute(object_to_save, filename):
    def thread():
        while True:
            temp = object_to_save
            if type(object_to_save) == queue.Queue:
                temp = list(object_to_save.queue)
            pickle.dump(temp, open(filename, 'wb'), protocol=4)
            time.sleep(60)

    threading.Thread(target=thread, daemon=True).start()


if __name__ == '__main__':
    ceneo = CeneoCrawler()
    ceneo.crawl()
