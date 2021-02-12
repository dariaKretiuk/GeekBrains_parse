import re
from urllib.parse import urljoin
from scrapy import Selector
from scrapy.loader import ItemLoader
from .items import HHItem
from itemloaders.processors import TakeFirst, MapCompose


def get_description(item):
    print(1)
    return


def get_skills(item):
    print(1)
    return


def clear_unicode(item):
    return item.replace(u"\xa0", "")


def get_url_company(item):
    return 'https://spb.hh.ru' + item


class HHLoader(ItemLoader):
    default_item_class = HHItem
    title_out = TakeFirst()
    salary_in = MapCompose(clear_unicode)
    salary_out = "".join
    description_out = "\n".join
    skills_out = ", ".join
    url_company_in = MapCompose(get_url_company)
    url_company_out = TakeFirst()
    name_out = TakeFirst()
    url_site_out = TakeFirst()
    activity_out = TakeFirst()
    description_company_out = TakeFirst()
    vacancies_company_out = TakeFirst()
