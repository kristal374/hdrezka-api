from __future__ import annotations

import re
from datetime import datetime, timedelta
from enum import Enum
from typing import TYPE_CHECKING, List, Optional
from urllib import parse

if TYPE_CHECKING:
    from .comments import Comment


class URLsType(Enum):
    """Enumeration class to represent different types of URLs belonging to the site "rezka.ag".

    Attributes:
        unknown: An unknown URL type.
        main: The main page of a website.
        movie: The URL of a movie.
        collections: The URL of a collection of movies.
        qa_info: URL of page answering questions about the film.
        qa: The URL of page with questions about films.
        franchises_info: The URL of a franchise information page.
        franchises: The URL of a franchises page.
        person_info: The URL to the person's information page.
        poster: The URL of a movie posters page.
    """

    unknown = 0
    main = 1
    movie = 2
    collections = 3
    qa_info = 4
    qa = 5
    franchises_info = 6
    franchises = 7
    person_info = 8
    poster = 9


URL_REGEX_DICT = {
    URLsType.main: r"/(?:page/1/?)?$",
    URLsType.movie: r"/(?:[0-9a-zA-Z-_]+/)+\d+(?:-.+?)+\.html",
    URLsType.collections: r"/collections/?(?:page/\d+/?)?$",
    URLsType.qa_info: r"/qa/.+\.html",
    URLsType.qa: r"/qa/?(?:page/\d+/?)?$",
    URLsType.franchises_info: r"/franchises/\d+(?:-[^/]+)/?$",
    URLsType.franchises: r"/franchises/?(?:page/\d+/?)?$",
    URLsType.person_info: r"/person/\d+(?:-[^/]+)/?",
    URLsType.poster: r"^/(?:ua/)?(?:films|series|cartoons|animation|show|games|new|announce|collections/\d+"
    r"(?:-[^/]+)|search|country/(?:(?:%[A-F0-9+-]+)+|[А-я+-]+)|year/(?:\d+)|page/(?:(?!1\b)"
    r"\d+))/?(?:best/(?:[a-z\-_]+/\d+|[a-z-_]+|\d+)?/?)?(?:(?!page)[a-z-]+/?)?(?:page/\d+/?)?",
}
REGEX_QUERY = (
    r"(?:filter=(?:last|popular|soon|watching)(?:&genre=\d+)?|" r"do=(?:lostpassword|search&subaction=search&q=.*))"
)
REGEX_FRAGMENT = r"(?:akter|aktrisa|hudozhnik|kompozitor|montazher|operator|prodyuser|rezhisser|scenarist)"
REGEX_MOVIE_FRAGMENT = r"t:\d+-s:\d+-e:\d+"


def determine_url_type(url: str) -> URLsType:
    """Determines the type of URL passed in using regular expressions.

    :param url:
        The URL to be checked for its type.
    :return:
        The type of the URL.

    Usage::

        >>> from HDrezka.utility import determine_url_type
        >>>
        >>> url_type = determine_url_type("https://rezka.ag/")
        >>> if url_type == URLsType.main:
        >>>     # Handle main URL
        >>> elif url_type == URLsType.movie:
        >>>     # Handle movie URL
        >>> elif url_type == URLsType.person_info:
        >>>     # Handle person info URL
        >>> else:
        >>>     # Handle other URL types
    """
    url_split = parse.urlsplit(url)
    if url_split.path == "":
        return URLsType.main
    if re.fullmatch(REGEX_QUERY, url_split.query):
        return URLsType.poster
    if re.fullmatch(REGEX_FRAGMENT, url_split.fragment):
        return URLsType.person_info
    if re.fullmatch(REGEX_MOVIE_FRAGMENT, url_split.fragment):
        return URLsType.movie
    for page_type, pattern in URL_REGEX_DICT.items():
        if re.fullmatch(pattern, url_split.path):
            return page_type
    return URLsType.unknown


def extract_datetime(datetime_string: str) -> datetime:
    """Using regular expressions, extracts a date from a string
    and converts it into a datetime object.

    :param datetime_string:
        A string representing a datetime in a specific format.
    :raise ValueError:
        If the datetime_string is not recognized as datetime string.
    :return:
        A datetime object extracted from the given datetime_string.

    Usage::

        >>> from HDrezka.utility import extract_datetime
        >>> raw_datetime_string = "сегодня, 10:30"
        >>> result = extract_datetime(raw_datetime_string)
        >>> print(result)
        2021-07-27 10:30:00
    """
    match = re.search(r"(сегодня|вчера|\d+ [А-я]+ \d{4})?,?\s?(\d{2}:\d{2})", datetime_string)

    if not match:
        raise ValueError(f"No match found for string: {datetime_string}")

    date_string, time_string = match.groups()
    hours, minutes = map(int, time_string.strip().split(":"))
    return extract_date(date_string) + timedelta(hours=hours, minutes=minutes)


def extract_date(datetime_string: str) -> datetime:
    """Using regular expressions, extracts a date from a string
    and converts it into a date object.

    :param datetime_string:
        A string representing a datetime in a specific format.
    :raise ValueError:
        If the datetime_string is not recognized as date string,
        or if it is not possible to correctly determine the month.
    :return:
        A datetime object extracted from the given datetime_string.

    Usage::

        >>> from HDrezka.utility import extract_date
        >>> raw_datetime_string = "сегодня, 10:30"
        >>> result = extract_date(raw_datetime_string)
        >>> print(result)
        2021-07-27 00:00:00
    """
    if datetime_string == "сегодня":
        return datetime.combine(datetime.now(), datetime.min.time())
    if datetime_string == "вчера":
        return datetime.combine(datetime.now(), datetime.min.time()) - timedelta(days=1)

    match = re.search(r"(\d+)?\s?([А-я]+)?,?\s?(\d{4})\s?(года?|-\s\.{3})?", datetime_string)

    if not match:
        raise ValueError(f"No match found for string: {datetime_string}")

    day, month, year, _ = match.groups()

    month_name = (
        ("",),
        ("январь", "января"),
        ("февраль", "февраля"),
        ("март", "марта"),
        ("апрель", "апреля"),
        ("май", "мая"),
        ("июнь", "июня"),
        ("июль", "июля"),
        ("август", "августа"),
        ("сентябрь", "сентября"),
        ("октябрь", "октября"),
        ("ноябрь", "ноября"),
        ("декабрь", "декабря"),
    )

    day = int(day) if day is not None else 1
    if month is not None:
        month_num = [month_name.index(m) for m in month_name if month in m]
        if len(month_num) != 1:
            raise ValueError(f"Unexpected month name: {month}")
        month = month_num[0]
    else:
        month = 1

    return datetime(year=int(year), month=month, day=day)


def convert_string_into_datetime(datetime_string: str) -> Optional[datetime]:
    """Convert a string into a datetime object.
    Automatically determines which method to use `extract_datetime` or `extract_date`.

    :param datetime_string:
        A string representing a datetime in a specific format.
    :raise ValueError:
        If the datetime_string is not recognized as date string,
        or if it is not possible to correctly determine the month.
    :return:
        A datetime object or None if datetime_string is None or empty string.

    Usage::

        >>> from HDrezka.utility import convert_string_into_datetime
        >>> raw_datetime_string = "сегодня, 10:30"
        >>> result = convert_string_into_datetime(raw_datetime_string)
        >>> print(result)
        2021-07-27 10:30:00
    """
    if datetime_string is None or datetime_string == "":
        return None
    if re.search(r"(\d{2}:\d{2})", datetime_string):
        return extract_datetime(datetime_string)
    return extract_date(datetime_string)


def calculate_count_comments(comments_list: List[Comment]) -> int:
    """Calculate the total number of comments.

    :param comments_list:
        The list with comments.
    :return:
        The total number of messages.
    """
    return sum(calculate_count_comments(item.replies) for item in comments_list) + 1


def make_filename_from_movie_title(title: str, separator="_"):
    """A simple function for quickly creating a file name from a movie title.
    Removes most characters that may conflict with the file system.

    :param title:
        Movie title.
    :param separator:
        The character with which to replace the space in the title.
    :return:
        A file name that can be used when downloading a movie.

    Usage::

        >>> from HDrezka import HDrezka
        >>> from HDrezka.utility import make_filename_from_movie_title
        >>>
        >>> movie = HDrezka.get(url="https://rezka.ag/cartoons/fantasy/30073-drakony-gonka-na-grani-2015.html")
        >>> filename = make_filename_from_movie_title(movie.title)
        >>> movie.player.load(filename)
        >>> print(filename)
        "Драконы Гонка на грани"
    """
    return re.sub(r"[\\/:;*?&^#%!$\"`<>|]", "", title.split("/")[0]).strip().replace(" ", separator)
