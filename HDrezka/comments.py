from __future__ import annotations

import re
import time
from dataclasses import dataclass
from typing import List, Optional

import bs4

from .core_navigation import PageIterator
from .exceptions import EmptyPage, ServiceUnavailable
from .html_representation import PageRepresentation
from .utility import convert_string_into_datetime, get_count_messages


@dataclass
class User:
    name: str = None  # Имя пользователя
    img_url: str = None  # Ссылка на аватар-изображение пользователя

    def __repr__(self):
        return f"<User({self.name})>"


@dataclass
class Comment:
    id: int = None  # идентификатор комментария
    author: User = None  # автор комментария
    timestamp: str = None  # дата и время когда был оставлен комментарий
    text: str = None  # текст комментария
    replies: List[Comment] = None  # комментарии-ответы на данный комментарий
    likes_num: int = None  # количество отметок "нравиться"
    edit: bool = None  # был ли комментарий отредактирован администрацией

    def __repr__(self):
        return f"Comment({self.author.name})"


class CommentsIterator(PageIterator[List[Comment]]):
    def __init__(self, film_id, page_type=0):
        super().__init__()
        self.film_id = film_id
        self.page_type = page_type  # 0 - film page or 1 - question page

    def get(self, number: Optional[int] = None):
        if self._last_page is not None and number is not None and number > self.last_page:
            raise AttributeError(
                f'The value of "number"={number} is greater than ' f'the value of "last_page"={self.last_page}'
            )

        response = self._query(page=number if number is not None else self.current_page)
        soup = bs4.BeautifulSoup(response["comments"], "lxml")

        if self._last_page is None:
            self._fetch_last_page(response)
        result_list = self.extreact_comments(soup)

        number_comments = response["comments"].count(">оставлен ")
        if number_comments != get_count_messages(result_list) - 1:  # pragma: NO COVER
            # Sometimes the server sends incorrect html code, in this case you need to use another stricter parser
            soup = bs4.BeautifulSoup(response["comments"], "html5lib")
            return self.extreact_comments(soup)
        if not result_list:  # pragma: NO COVER
            raise EmptyPage("No comments found on the page")
        return result_list

    def _fetch_last_page(self, response):
        navigation_bar = PageRepresentation(response.get("navigation"))
        self.last_page = self._get_last_page_number(navigation_bar)

    def extreact_comments(self, comments):
        child = comments.find(class_="comments-tree-list")
        result_lst = []
        if child is not None:
            items = child.find_all(class_="comments-tree-item", recursive=False)

            for comment_tree in items:
                comment = Comment()
                comment.id = int(comment_tree.get("data-id"))
                comment.author = User()
                if comment_tree.next.get("class", [None])[0] == "b-comment__removed":  # pragma: NO COVER
                    comment.author.name = "Администрация"
                    comment.author.img_url = "https://static.hdrezka.ac/templates/hdrezka/images/avatar.png"
                    comment.text = self._extract_text(comment_tree.find("div", class_="b-comment__removed"))
                    comment.replies = self.extreact_comments(comment_tree)
                else:
                    comment.author.name = comment_tree.next.find("span", class_="name").text.strip()
                    comment.author.img_url = comment_tree.next.find("div", class_="ava").img.get("src").strip()
                    comment.timestamp = self._extract_timestamp(comment_tree)
                    comment.text = self._extract_text(comment_tree.next.find("div", class_="text").next)
                    comment.replies = self.extreact_comments(comment_tree)
                    comment.likes_num = int(
                        comment_tree.next.find("span", class_="b-comment__likes_count").i.text.strip()
                    )
                    comment.edit = bool(comment_tree.next.find("span", class_="edited"))
                result_lst.append(comment)
        return result_lst

    @staticmethod
    def _extract_timestamp(comment_tree):
        return convert_string_into_datetime(comment_tree.next.find("span", class_="date").text.strip()[9:])

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
        if tag.name == "a" and "youtu-link" in tag.get("class", []):
            return tag.get("href").strip()

        text_from_tag = self._extract_text(tag)
        if tag.name == "a" and (
                tag.get("href") == text_from_tag or not re.search(r'https?://[^\s"]*', tag.get("href"))
        ):
            return text_from_tag

        new_tag = bs4.BeautifulSoup().new_tag(tag.name)
        new_tag.attrs = tag.attrs
        new_tag.string = "{}"
        return str(new_tag).format(text_from_tag)

    def _query(self, page: Optional[int] = None):
        data = {
            "t": int(time.time() * 1000),
            "news_id": self.film_id,
            "cstart": self.current_page if page is None else page,
            "type": self.page_type,
            "comment_id": 0,
            "skin": "hdrezka",
        }
        response = self._connector.get(f"{self._connector.url}/ajax/get_comments/", params=data)
        if response.status_code == 200:
            return response.json()
        raise ServiceUnavailable("Service is temporarily unavailable")

    def __repr__(self):
        return f'<{CommentsIterator.__name__}(film_id="{self.film_id}")>'
