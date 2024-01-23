import re
import time
from dataclasses import dataclass
from typing import List

import bs4

from HDrezka.connector import NetworkClient
from HDrezka.exceptions import EmptyPage, ServiceUnavailable


@dataclass
class User:
    name: str = None  # Имя пользователя
    image: str = None  # Ссылка на аватар-изображение пользователя

    def __repr__(self):
        return f"<User({self.name})>"


@dataclass
class Comment:
    id: int = None  # идентификатор комментария
    author: User = None  # автор комментария
    date: str = None  # дата и время когда был оставлен комментарий
    text: str = None  # текст комментария
    replies: List["Comment"] = None  # комментарии-ответы на данный комментарий
    likes_num: int = None  # количество отметок "нравиться"
    edit: bool = None  # был ли комментарий отредактирован администрацией

    def __repr__(self):
        return f"Comment({self.author.name})"


class CommentsIterator:
    def __new__(cls, *args, **kwargs):  # pylint: disable= W0613
        if not hasattr(cls, "connector"):
            cls.connector = NetworkClient()
        return super().__new__(cls)

    def __init__(self, film_id, type_page=0):
        self.film_id = film_id
        self.page_number = 0
        self.type_page = type_page  # 0 - film page or 1 - question page
        self.last_page = None

    def __iter__(self):
        return self

    def __next__(self):
        self.page_number += 1
        try:
            list_comments = self.get_page(self.page_number)
        except EmptyPage:
            self.page_number = 0
            raise StopIteration  # pylint: disable= W0707
        return list_comments

    def __count_elements(self, data):
        return sum(self.__count_elements(item.replies) for item in data) + 1

    def get_page(self, number=1):
        if self.last_page is not None and number > self.last_page:
            raise EmptyPage("No comments found on the page")

        response = self._get(page=number)
        soup = bs4.BeautifulSoup(response["comments"], "lxml")

        if self.last_page is None:
            self.last_page = self._extract_last_page_number(response.get("navigation"))
        result_list = self.extreact_comments(soup)

        number_comments = response["comments"].count(">оставлен ")
        if number_comments != self.__count_elements(result_list) - 1:  # pragma: NO COVER
            # Sometimes the server sends incorrect html code, in this case you need to use another stricter parser
            soup = bs4.BeautifulSoup(response["comments"], "html5lib")
            return self.extreact_comments(soup)
        if not result_list:  # pragma: NO COVER
            raise EmptyPage("No comments found on the page")
        return result_list

    @staticmethod
    def _extract_last_page_number(navigation):
        if not navigation:
            return 1
        soup = bs4.BeautifulSoup(navigation, "lxml")
        preview_element = soup.find(class_="b-navigation__next")
        if preview_element:
            return int(preview_element.parent.find_previous("a").string)
        return int(soup.find_all("span")[-1].text)

    def extreact_comments(self, comments):
        child = comments.find(class_="comments-tree-list")
        result_lst = []
        if child is not None:
            items = child.find_all(class_="comments-tree-item", recursive=False)

            for comment_tree in items:
                comment = Comment()
                comment.id = int(comment_tree.get("data-id"))
                comment.author = User()
                comment.author.name = comment_tree.next.find("span", class_="name").text.strip()
                comment.author.image = comment_tree.next.find("div", class_="ava").img.get("src").strip()
                comment.date = comment_tree.next.find("span", class_="date").text.strip()[9:]
                comment.text = self._extract_text(comment_tree.next.find("div", class_="text").next)
                comment.replies = self.extreact_comments(comment_tree)
                comment.likes_num = int(comment_tree.next.find("span", class_="b-comment__likes_count").i.text.strip())
                comment.edit = bool(comment_tree.next.find("span", class_="edited"))
                result_lst.append(comment)
        return result_lst

    def _extract_text(self, tag: bs4.element.Tag) -> str:
        result_string = ""
        for item in tag.contents:
            if isinstance(item, bs4.element.Comment):
                continue
            if isinstance(item, bs4.element.NavigableString):
                result_string += str(item)
            elif isinstance(item, bs4.element.Tag):
                result_string += self._process_tag(item)
            else:
                # In theory, this should never work; otherwise a raw string will be added
                result_string += str(item)  # pragma: NO COVER
        return result_string

    def _process_tag(self, tag: bs4.element.Tag) -> str:
        tag_classes = tag.get("class", [])

        if "title_spoiler" in tag_classes:
            return ""
        if "text_spoiler" in tag_classes:
            return f"<spoiler>{self._extract_text(tag)}</spoiler>"
        if tag.name == "br":
            return "<br>"
        if tag.name in ("b", "i", "u", "s", "a"):
            return self._process_inline_tag(tag)
        # In theory, this should never work; otherwise a raw string will be added
        return str(tag)  # pragma: NO COVER

    def _process_inline_tag(self, tag: bs4.element.Tag) -> str:
        if tag.name == "a" and 'youtu-link' in tag.get("class", []):
            return tag.get("href").strip()

        text_from_tag = self._extract_text(tag)
        if tag.name == "a" and (
                tag.get("href") == text_from_tag or not re.search(r'https?://[^\s"]*', tag.get("href"))):
            return text_from_tag

        new_tag = bs4.BeautifulSoup().new_tag(tag.name)
        new_tag.attrs = tag.attrs
        new_tag.string = "{}"
        return str(new_tag).format(text_from_tag)

    def _get(self, page=None):
        data = {
            "t": int(time.time() * 1000),
            "news_id": self.film_id,
            "cstart": self.page_number if page is None else page,
            "type": self.type_page,
            "comment_id": 0,
            "skin": "hdrezka"
        }
        response = self.connector.get(f"{self.connector.url}/ajax/get_comments/", params=data)
        if response.status_code == 200:
            return response.json()
        raise ServiceUnavailable("Service is temporarily unavailable")

    def __repr__(self):
        return f"<{CommentsIterator.__name__}(film_id=\"{self.film_id}\")>"
