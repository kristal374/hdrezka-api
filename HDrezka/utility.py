import re
from datetime import datetime, timedelta
from enum import Enum
from urllib import parse


class URLsType(Enum):
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


def get_url_type(url: str) -> URLsType:
    """
    Позволяет определить на какую страницу ведёт url исходя из его пути.
    Необходимо если заранее неизвестно с помощью какого класса обрабатывать ответ сервера.
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


def extract_datetime(datetime_string):
    match = re.search(r"(сегодня|вчера|\d+ [А-я]+ \d{4})?,?\s?(\d{2}:\d{2})", datetime_string)
    date_string, time_string = match.groups()
    hours, minutes = map(int, time_string.strip().split(":"))
    return extract_date(date_string) + timedelta(hours=hours, minutes=minutes)


def extract_date(datetime_string):
    day, month, year, _ = re.search(r"(\d+)?\s?([А-я]+)?\s?(\d{4})\s?(года?|-\s\.{3})?", datetime_string).groups()

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
            raise AttributeError("Incorrect month name")
        month = month_num[0]
    else:
        month = 1

    if datetime_string == "сегодня":
        return datetime.now()
    if datetime_string == "вчера":
        return datetime.now() - timedelta(days=1)
    return datetime(year=int(year), month=month, day=day)


def convert_string_into_datetime(datetime_string: str):
    if datetime_string is None or datetime_string == "":
        return None
    if re.search(r"(\d{2}:\d{2})", datetime_string):
        return extract_datetime(datetime_string)
    return extract_date(datetime_string).date()


def get_count_messages(data) -> int:
    """
    Calculate the total number of messages.

    :param data: The list with messages.
    :return: The total number of messages.
    """
    return sum(get_count_messages(item.replies) for item in data) + 1
