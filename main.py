from selenium.common.exceptions import WebDriverException

from crawlers import ceneo_negative_crawler

if __name__ == '__main__':
    while True:
        try:
            ceneo = ceneo_negative_crawler.CeneoCrawler()
            # ceneo.crawl()
            ceneo.scrape_queued_products()
            ceneo.crawl_category('https://www.ceneo.pl/Biuro_i_firma')
            ceneo.crawl_category('https://www.ceneo.pl/Budowa_i_remont')
            ceneo.crawl_category('https://www.ceneo.pl/Dla_dziecka')
            ceneo.crawl_category('https://www.ceneo.pl/Komputery')
            ceneo.crawl_category('https://www.ceneo.pl/Motoryzacja')
            ceneo.crawl_category('https://www.ceneo.pl/Ogrod')
            ceneo.crawl_category('https://www.ceneo.pl/Sport_i_rekreacja')
            ceneo.crawl_category('https://www.ceneo.pl/Sprzet_AGD')
            ceneo.crawl_category('https://www.ceneo.pl/Telefony_i_akcesoria')
        except WebDriverException:
            raise
            continue
        else:
            break

