import pymongo
import scrapy

import os
import pymongo
from dotenv import load_dotenv

class AutoyoulaSpider(scrapy.Spider):
    name = "autoyoula"
    allowed_domains = ["auto.youla.ru"]
    start_urls = ["https://auto.youla.ru/"]

    css_query = {
        "brands": "div.TransportMainFilters_block__3etab a.blackLink",
        "pagination": "div.Paginator_block__2XAPy a.Paginator_button__u1e7D",
        "ads": "article.SerpSnippet_snippet__3O1t2 a.SerpSnippet_name__3F7Yu",
    }

    data_query = {
        "title": lambda response: response.css("div.AdvertCard_advertTitle__1S1Ak::text").get(),
        "price": lambda response: response.css("div.AdvertCard_price__3dDCr::text").get(),
        "url_image": lambda response: response.css("img.PhotoGallery_photoImage__2mHGn::attr(src)").getall(),
        "characteristics": lambda response: "\n".join(
            f"{characteristic.css('div.AdvertSpecs_label__2JHnS::text').get()}: {characteristic.css('div.AdvertSpecs_data__xK2Qx::text').get()}"
            for characteristic in response.css("div.AdvertSpecs_row__ljPcX") if
            characteristic.css('div.AdvertSpecs_data__xK2Qx::text').get() != None),
        "description": lambda response: response.css("div.AdvertCard_descriptionInner__KnuRi::text").get(),
        "url_author": lambda response: response.css("div.app_gridAsideChildren__wB756 a.SellerInfo_name__3Iz2N::attr(href)").get()
    }

    def __init__(self):
        load_dotenv(".env")
        data_base_url = os.getenv("DATA_BASE_URL")
        data_client = pymongo.MongoClient(data_base_url)
        self.data_base = data_client["gb_parse_13_01_2021"]

    @staticmethod
    def characteristics_parse(response):
        pass

    def parse(self, response, **kwargs):
        yield from self.gen_task(response, response.css(self.css_query["brands"]), self.brand_parse)

    def brand_parse(self, response):
        yield from self.gen_task(response, response.css(self.css_query["pagination"]), self.brand_parse)
        yield from self.gen_task(response, response.css(self.css_query["ads"]), self.ads_parse)

    def ads_parse(self, response):
        data = {}
        for name, query in self.data_query.items():
            data[name] = query(response)
        self.save(data)

    def save(self, data):
        collection = self.data_base["autoyoula"]
        collection.insert_one(data)
        pass


    @staticmethod
    def gen_task(response, link_list, callback):
        for link in link_list:
            yield response.follow(link.attrib.get("href"), callback=callback)
