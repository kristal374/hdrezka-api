from enum import Enum

__all__ = [
    "GenreFilm",
    "GenreCartoons",
    "GenreSeries",
    "GenreAnimation",
    "Filters",
    "ShowCategory",
    "convert_genres",
    "all_genres",
]

all_genres = {
    "аниме": "anime",
    "арт-хаус": "arthouse",
    "биографические": "biographical",
    "боевики": "action",
    "боевые искусства": "fighting",
    "вестерны": "western",
    "военные": "military",
    "детективы": "detective",
    "детские": "kids",
    "для взрослых": "adult",
    "документальные": "documentary",
    "драмы": "drama",
    "зарубежные": "foreign",
    "исторические": "historical",
    "кодомо": "kodomo",
    "комедии": "comedy",
    "конкурсы": "contests",
    "концерт": "concert",
    "короткометражные": "short",
    "криминал": "crime",
    "махо-сёдзё": "mahoushoujo",
    "мелодрамы": "melodrama",
    "меха": "mecha",
    "мистические": "mystery",
    "музыкальные": "musical",
    "мультсериалы": "multseries",
    "мюзиклы": "musical",
    "образовательные": "educational",
    "охота и рыбалка": "hunting",
    "пародия": "parody",
    "повседневность": "everyday",
    "познавательные": "cognitive",
    "полнометражные": "full-length",
    "приключения": "adventures",
    "путешествия": "travel",
    "реалити-шоу": "reality-shows",
    "реальное тв": "realtv",
    "романтические": "romance",
    "русские": "russian",
    "самурайский боевик": "samurai",
    "семейные": "family",
    "сказки": "fairytale",
    "советские": "soyzmyltfilm",
    "спортивные": "sport",
    "стендап": "standup",
    "сёдзё": "shoujo",
    "сёдзё-ай": "shoujoai",
    "сёнэн": "shounen",
    "сёнэн-ай": "shounenai",
    "театр": "theatre",
    "телепередачи": "telecasts",
    "триллеры": "thriller",
    "ужасы": "horror",
    "украинские": "ukrainian",
    "фантастика": "fiction",
    "фэнтези": "fantasy",
    "школа": "school",
    "эротика": "erotic",
    "этти": "ecchi",
    "юмористические": "humor",
}


def convert_genres(genre: str):
    return all_genres.get(genre.lower())


class GenreFilm(Enum):
    ACTION = "action"
    ADVENTURES = "adventures"
    ARTHOUSE = "arthouse"
    BIOGRAPHICAL = "biographical"
    COGNITIVE = "cognitive"
    COMEDY = "comedy"
    CONCERT = "concert"
    CRIME = "crime"
    DETECTIVE = "detective"
    DOCUMENTARY = "documentary"
    DRAMA = "drama"
    EROTIC = "erotic"
    FAMILY = "family"
    FANTASY = "fantasy"
    FICTION = "fiction"
    FOREIGN = "foreign"
    HISTORICAL = "historical"
    HORROR = "horror"
    KIDS = "kids"
    MELODRAMA = "melodrama"
    MILITARY = "military"
    MUSICAL = "musical"
    RUSSIAN = "russian"
    SHORT = "short"
    SPORT = "sport"
    STANDUP = "standup"
    THEATRE = "theatre"
    THRILLER = "thriller"
    TRAVEL = "travel"
    UKRAINIAN = "ukrainian"
    WESTERN = "western"


class GenreSeries(Enum):
    ACTION = "action"
    ADVENTURES = "adventures"
    ARTHOUSE = "arthouse"
    BIOGRAPHICAL = "biographical"
    COMEDY = "comedy"
    CRIME = "crime"
    DETECTIVE = "detective"
    DOCUMENTARY = "documentary"
    DRAMA = "drama"
    EROTIC = "erotic"
    FAMILY = "family"
    FANTASY = "fantasy"
    FICTION = "fiction"
    FOREIGN = "foreign"
    HISTORICAL = "historical"
    HORROR = "horror"
    MELODRAMA = "melodrama"
    MILITARY = "military"
    MUSICAL = "musical"
    REALTV = "realtv"
    RUSSIAN = "russian"
    SPORT = "sport"
    STANDUP = "standup"
    TELECASTS = "telecasts"
    THRILLER = "thriller"
    UKRAINIAN = "ukrainian"
    WESTERN = "western"


class GenreCartoons(Enum):
    ACTION = "action"
    ADULT = "adult"
    ADVENTURES = "adventures"
    ANIME = "anime"
    ARTHOUSE = "arthouse"
    BIOGRAPHICAL = "biographical"
    COGNITIVE = "cognitive"
    COMEDY = "comedy"
    CRIME = "crime"
    DETECTIVE = "detective"
    DOCUMENTARY = "documentary"
    DRAMA = "drama"
    EROTIC = "erotic"
    FAIRYTALE = "fairytale"
    FAMILY = "family"
    FANTASY = "fantasy"
    FICTION = "fiction"
    FOREIGN = "foreign"
    FULL_LENGTH = "full-length"
    HISTORICAL = "historical"
    HORROR = "horror"
    KIDS = "kids"
    MELODRAMA = "melodrama"
    MILITARY = "military"
    MULTSERIES = "multseries"
    MUSICAL = "musical"
    RUSSIAN = "russian"
    SHORT = "short"
    SOYZMYLTFILM = "soyzmyltfilm"
    SPORT = "sport"
    THRILLER = "thriller"
    UKRAINIAN = "ukrainian"
    WESTERN = "western"


class GenreAnimation(Enum):
    ACTION = "action"
    ADVENTURES = "adventures"
    COMEDY = "comedy"
    DETECTIVE = "detective"
    DRAMA = "drama"
    ECCHI = "ecchi"
    EDUCATIONAL = "educational"
    EROTIC = "erotic"
    EVERYDAY = "everyday"
    FAIRYTALE = "fairytale"
    FANTASY = "fantasy"
    FICTION = "fiction"
    FIGHTING = "fighting"
    HISTORICAL = "historical"
    HORROR = "horror"
    KIDS = "kids"
    KODOMO = "kodomo"
    MAHOUSHOUJO = "mahoushoujo"
    MECHA = "mecha"
    MILITARY = "military"
    MUSICAL = "musical"
    MYSTERY = "mystery"
    PARODY = "parody"
    ROMANCE = "romance"
    SAMURAI = "samurai"
    SCHOOL = "school"
    SHOUJO = "shoujo"
    SHOUJOAI = "shoujoai"
    SHOUNEN = "shounen"
    SHOUNENAI = "shounenai"
    SPORT = "sport"
    THRILLER = "thriller"


class Filters(Enum):
    LAST = "last"  # Последние поступления
    POPULAR = "popular"  # Популярные
    SOON = "soon"  # В ожидании
    WATCHING = "watching"  # Сейчас смотрят


class ShowCategory(Enum):
    ALL = 0
    FILMS = 1
    SERIES = 2
    CARTOONS = 3
    ANIMATION = 82
