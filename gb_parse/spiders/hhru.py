import scrapy
from ..loaders import HHLoader
from urllib.parse import urljoin


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['spb.hh.ru']
    start_urls = ['https://spb.hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113']

    css_query = {
        "pagination": "span.bloko-button-group a.bloko-button",
        "vacancies": "div.vacancy-serp a.bloko-link",
        "company": "div.bloko-gap a.vacancy-company-name",
        "vacancies_company": "div.employer-sidebar a.employer-page__employer-vacancies-link"
    }

    data_query_2 = {
        "title": "//div[@class='bloko-columns-row']//h1[@class='bloko-header-1']//text()",
        "salary": "//div[@class='bloko-columns-row']//p[@class='vacancy-salary']//span[@data-qa='bloko-header-2']//text()",
        "description": "//div[@class='bloko-columns-row']//div[@class='vacancy-description']//div[@class='g-user-content']//text()",
        "skills": "//div[@class='vacancy-section']//div[@class='bloko-tag-list']//span[@data-qa='bloko-tag__text']//text()",
        "url_company": "//div[@class='bloko-columns-row']//div[@class='vacancy-company__details']//a[@class='vacancy-company-name']/@href",
        "name": "//div[@class='bloko-columns-row']//div[@class='vacancy-company__details']//a[@class='vacancy-company-name']//text()"
    }

    def parse(self, response, **kwargs):
        return self.vacancies_parse(response)

    def vacancies_parse(self, response):
        yield from self.gen_task(response, response.css(self.css_query["pagination"]), self.vacancies_parse)
        yield from self.gen_task(response, response.css(self.css_query["vacancies"]), self.vacancy_parse)

    def vacancy_parse(self, response):
        loader = HHLoader(response=response)
        for key, selector in self.data_query_2.items():
            loader.add_xpath(key, selector)
        yield loader.load_item()

    def vacancies_company_parse(self, response):
        loader = HHLoader(response=response)
        for key, selector in self.data_query_2.items():
            loader.add_xpath(key, selector)
        yield loader.load_item()

    @staticmethod
    def gen_task(response, link_list, callback):
        for link in link_list:
            yield response.follow(link.attrib.get("href"), callback=callback)
