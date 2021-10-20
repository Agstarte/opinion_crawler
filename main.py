import time

from crawlers import ceneo_crawler

if __name__ == '__main__':
    ceneo = ceneo_crawler.CeneoCrawler()
    ceneo.crawl()
