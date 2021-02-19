import datetime as dt
import json
import scrapy
from ..items import InstagramTagItem, InstagramPostItem, InstagramUserItem, InstagramFollowItem, InstagramFollowerItem
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
        "following": "d04b0a864b4b54837c0d870b0e77e076",  # подписки
        "followers": "c76146de99bb02f6415203be841dd25a",  # подписчики
    }

    def __init__(self, login, password, *args, **kwargs):
        self.tags = ["python", "программирование", "developers"]
        self.users = ["oly_ilchenko", "kuzkaty_", "incredulous_fox", "polifeniks"]
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
                for user in self.users:
                    yield response.follow(f"/{user}/", callback=self.users_parse)

    def users_parse(self, response):
        js_data = self.js_data_extract(response)
        user_data = {
            'id': js_data['entry_data']['ProfilePage'][0]['graphql']['user']['id'],
            'name': js_data['entry_data']['ProfilePage'][0]['graphql']['user']['username'],
        }
        variables = {
            'id': user_data['id'],
            'include_reel': True,
            'fetch_mutual': False,
            'first': 100
        }
        url = f'{self.api_url}?query_hash={self.query_hash["following"]}&variables={json.dumps(variables)}'
        yield InstagramUserItem(date_parse=datetime.now(), data=user_data)
        yield response.follow(url, callback=self.get_follow_parse, cb_kwargs={"user_data": user_data})

    def get_pag_follow_parse(self, response, user_data):
        js_data = response.json()['data']['user']['edge_follow']
        if js_data['page_info']['has_next_page']:
            veriables = {
                'id': user_data['id'],
                'include_reel': True,
                'fetch_mutual': False,
                'first': 100,
                'after': js_data['page_info']['end_cursor']
            }
            url = f'{self.api_url}?query_hash={self.query_hash["following"]}&variables={json.dumps(veriables)}'
            yield response.follow(url, callback=self.get_pag_follow_parse,cb_kwargs={'user_data': user_data})
        yield from self.get_follows(js_data['edges'], user_data)

    def get_follow_parse(self, response, user_data):
        yield from self.get_pag_follow_parse(response, user_data)

    def get_followers_parse(self):
        pass

    # def parse(self, response, **kwargs):
    #     try:
    #         js_data = self.js_data_extract(response)
    #         yield scrapy.FormRequest(
    #             self.login_url,
    #             method="POST",
    #             callback=self.parse,
    #             formdata={
    #                 "username": self.login,
    #                 "enc_password": self.enc_passwd,
    #             },
    #             headers={"X-CSRFToken": js_data["config"]["csrf_token"]},
    #         )
    #     except AttributeError as e:
    #         if response.json().get("authenticated"):
    #             for tag in self.tags:
    #                 yield response.follow(f"/explore/tags/{tag}/", callback=self.tags_parse)

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
    def get_follows(edges, user_data):
        for edge in edges:
            yield InstagramFollowItem(date_parse=datetime.now(),
                                      data={'user_id': user_data['id'],
                                            'user_name': user_data['name'],
                                            'follow_id': edge['node']['id'],
                                            'follow_name': edge['node']['username']
                                      })

    @staticmethod
    def get_posts(edges):
        for edge in edges:
            yield InstagramPostItem(date_parse=datetime.now(), data=edge['node'], images=[edge['node']['display_url']])

    @staticmethod
    def js_data_extract(response):
        script = response.xpath('//script[contains(text(), "window._sharedData =")]/text()').get()
        return json.loads(script.replace("window._sharedData =", "")[:-1])
