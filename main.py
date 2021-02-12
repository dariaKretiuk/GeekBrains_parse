from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from gb_parse.spiders.hhru import HhruSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule('gb_parse.settings')
    crawler_process = CrawlerProcess(settings=crawler_settings)
    crawler_process.crawl(HhruSpider)
    crawler_process.start()
