import datetime as dt
import json
import scrapy
from ..items import InstagramTagItem, InstagramPostItem
from datetime import datetime


class InstagramSpider(scrapy.Spider):
    name = "instagram"
    allowed_domains = ["www.instagram.com"]
    start_urls = ["https://www.instagram.com/"]
    login_url = "https://www.instagram.com/accounts/login/ajax/"
    api_url = "/graphql/query/"
    query_hash = {
        "posts": "56a7068fea504063273cc2120ffd54f3",
        "tag_posts": "9b498c08113f1e09617a1703c22b2f32",
    }

    def __init__(self, login, password, *args, **kwargs):
        self.tags = ["python", "программирование", "developers"]
        self.login = login
        self.enc_passwd = password
        super().__init__(*args, **kwargs)

    def parse(self, response, **kwargs):
        try:
            js_data = self.js_data_extract(response)
            yield scrapy.FormRequest(
                self.login_url,
                method="POST",
                callback=self.parse,
                formdata={
                    "username": self.login,
                    "enc_password": self.enc_passwd,
                },
                headers={"X-CSRFToken": js_data["config"]["csrf_token"]},
            )
        except AttributeError as e:
            if response.json().get("authenticated"):
                for tag in self.tags:
                    yield response.follow(f"/explore/tags/{tag}/", callback=self.tags_parse)

    def tags_parse(self, response):
        data = self.js_data_extract(response)["entry_data"]["TagPage"][0]["graphql"]["hashtag"]
        data_tag = {'id': data['id'], 'name': data['name'], 'count': data['edge_hashtag_to_media']['count']}
        yield InstagramTagItem(date_parse=datetime.now(), data=data_tag)
        yield from self.tag_pag_parse(data, response)

    def tag_api_parse(self, response):
        yield from self.tag_pag_parse(response.json()["data"]["hashtag"], response)

    def tag_pag_parse(self, js_data, response):
        if js_data['edge_hashtag_to_media']['page_info']['has_next_page']:
            headers = {
                'tag_name': js_data['name'],
                'first': 50,
                'after': js_data['edge_hashtag_to_media']['page_info']['end_cursor']
            }
            url = f'{self.api_url}?query_hash={self.query_hash["tag_posts"]}&variables={json.dumps(headers)}'
            yield response.follow(url, callback=self.tag_api_parse)
        yield from self.get_posts(js_data['edge_hashtag_to_media']['edges'])

    @staticmethod
    def get_posts(edges):
        for edge in edges:
            yield InstagramPostItem(date_parse=datetime.now(), data=edge['node'], images=[edge['node']['display_url']])

    @staticmethod
    def js_data_extract(response):
        script = response.xpath('//script[contains(text(), "window._sharedData =")]/text()').get()
        return json.loads(script.replace("window._sharedData =", "")[:-1])
