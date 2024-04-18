import re
from dataclasses import dataclass
from typing import List, TYPE_CHECKING, Optional

from bs4 import Tag

from . import movie_posters
from .comments import CommentsIterator
from .connector import NetworkClient
from .exceptions import EmptyPage, PageNotFound
from .html_representation import PageRepresentation

if TYPE_CHECKING:
    from .movie_posters import Poster


@dataclass
class Question:
    id: int
    title: str
    image: Optional[str]
    text: str
    date: str
    recommendations: List
    comment: CommentsIterator
    current_url: str
    url: Optional[str]

    def get(self):
        if self.url is None:
            raise PageNotFound("No correct URL was found for the request")
        return movie_posters.PosterBuilder(NetworkClient().get(self.url).text).extract_content()

    def __repr__(self):
        return f"<Question({self.title})>"


class QuestionsBuilder(PageRepresentation):
    def extract_content(self) -> Question:
        current_url = self.page.soup.find('meta', property='og:url').get("content")
        return Question(
            id=int(re.search(r"(\d+)\.html$", current_url).group(1)),
            title=self.page.soup.find("div", class_="b-content__htitle").text.strip(),
            image=self.extract_image(),
            text=self.extract_text(),
            date=self.page.soup.find("div", class_="b-qa__entity_date").text.strip(),
            recommendations=self.extract_recommendations(),
            comment=CommentsIterator(int(re.search(r"(\d+)\.html$", current_url).group(1)), page_type=1),
            current_url=current_url,
            url=self.extract_url(),
        )

    def extract_recommendations(self) -> List["Poster"]:
        recommendations = self.page.soup.find("div", class_="b-sidelist")
        return movie_posters.PosterBuilder(str(recommendations)).extract_content()

    def extract_image(self):
        image = self.page.soup.find("div", class_="b-qa__entity_text clearfix").find("img")
        if image is None:
            return image
        return image.get("src")

    def extract_text(self):
        tag_br = Tag(name="br", can_be_empty_element=True)
        for item in self.page.soup.find("div", class_="b-qa__entity_text clearfix"):
            if item == tag_br:
                item.replace_with("\n")
        text = self.page.soup.find("div", class_="b-qa__entity_text clearfix").text
        while "\n\n" in text:
            text = text.replace("\n\n", "\n")
        return text.strip()

    def extract_url(self):
        all_url = self.page.soup.find("div", class_="b-qa__entity_text clearfix").find_all("a")
        target_url = set(i.get("href") for i in all_url if i.get("href").split(".")[-1] == "html")
        if not target_url:
            return None
        return list(target_url)[0]


@dataclass
class QuestionBriefInfo:
    id: int = None
    title: str = None
    image: str = None
    url: str = None

    def get(self):
        return QuestionsBuilder(NetworkClient().get(self.url).text).extract_content()

    def __repr__(self):
        return f"<QuestionBriefInfo({self.title})>"


class QuestionsBriefInfoBuilder(PageRepresentation):
    def extract_content(self) -> List[QuestionBriefInfo]:
        result_list = []
        for item in self.page.soup.find_all("li", class_="b-post__qa_list_item"):
            question = QuestionBriefInfo()
            question.url = item.a.get("href").strip()
            question.id = int(re.search(r"(\d+)\.html$", question.url).group(1))
            question.title = item.find("div", class_="title").text.strip()
            question.image = item.find("div", class_="cycle").img.get("src").strip()
            result_list.append(question)

        if not result_list:
            raise EmptyPage("No frequently asked questions found on the page")
        return result_list
