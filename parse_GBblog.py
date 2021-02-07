import os
import requests
import bs4
from urllib.parse import urljoin
from dotenv import load_dotenv

from database import Database

from datetime import datetime


class GbParse:
    def __init__(self, global_url, start_url, database):
        self.global_url = global_url
        self.start_url = start_url
        self.done_url = set()
        self.tasks = [self.parse_task(self.start_url, self.pag_parse)]
        self.done_url.add(self.start_url)
        self.database = database

    def _get_soup(self, *args, **kwargs):
        response = requests.get(*args, **kwargs)
        soup = bs4.BeautifulSoup(response.text, "lxml")
        return soup

    def parse_task(self, url, callback):
        def task():
            soup = self._get_soup(url)
            return callback(url, soup)

        return task

    def run(self):
        for task in self.tasks:
            result = task()
            if result:
                self.database.create_post(result)

    @staticmethod
    def parse_datetime(soup):
        date = str(soup.find("time").get("datetime")).split("T")[0][2:]
        time = str(soup.find("time").get("datetime")).split("T")[1].split("+")[0]

        return f"{date} {time}"

    @staticmethod
    def parse_comment(soup, global_url):
        comments = []
        commentable_id = soup.find("div", attrs={"class": "m-t-xl"}).find("comments").get("commentable-id")
        comments_json = requests.get(f"{global_url}/api/v2/comments?commentable_type=Post&commentable_id={commentable_id}&order=desc").json()

        for comment in comments_json:
            text = comment['comment']['body']
            name_author = comment['comment']['user']['full_name']

            comments.append({
                "author": name_author,
                "text": text
            })

        return comments

    def post_parse(self, url, soup: bs4.BeautifulSoup) -> dict:
        author_name_tag = soup.find("div", attrs={"itemprop": "author"})
        url_image = soup.find("div", attrs={"class": "blogpost-content"}).find_all("img")
        data = {
            "post_data": {
                "url": url,
                "title": soup.find("h1", attrs={"class": "blogpost-title"}).text,
                "url_image": url_image[0].get("src") if len(url_image)!= 0 else None,
                "date_public": datetime.strptime(self.parse_datetime(soup), "%y-%m-%d %H:%M:%S")
            },
            "author": {
                "url": urljoin(url, author_name_tag.parent.get("href")),
                "name": author_name_tag.text,
            },
            "tags": [
                {
                    "name": tag.text,
                    "url": urljoin(url, tag.get("href")),
                }
                for tag in soup.find_all("a", attrs={"class": "small"})
            ],
            "comments": self.parse_comment(soup, self.global_url)
        }
        return data

    def pag_parse(self, url, soup: bs4.BeautifulSoup):
        self.create_parse_tasks(url,
                                soup.find("ul", attrs={"class": "gb__pagination"}).find_all('a'),
                                self.pag_parse)
        self.create_parse_tasks(url,
                                soup.find('div', attrs={'class': 'post-items-wrapper'}).find_all("a", attrs={"class": "post-item__title"}),
                                self.post_parse)

    def create_parse_tasks(self, url, tag_list, callback):
        for a_tag in tag_list:
            a_url = urljoin(url, a_tag.get('href'))
            if a_url not in self.done_url:
                task = self.parse_task(a_url, callback)
                self.tasks.append(task)
                self.done_url.add(a_url)


if __name__ == "__main__":
    global_url = "https://geekbrains.ru"
    load_dotenv(".env")
    parser = GbParse(global_url, f"{global_url}/posts", Database(os.getenv("SQL_DB_URL")))
    parser.run()
