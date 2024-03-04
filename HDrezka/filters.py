from enum import Enum

__all__ = ['GenreFilm', 'GenreCartoons', 'GenreSeries', 'GenreAnimation',
           'Filters', 'ShowCategory', 'convert_genres', "all_genres"]

all_genres = {
    'военные': 'military',
    'семейные': 'family',
    'театр': 'theatre',
    'реальное тв': 'realtv',
    'сёнэн-ай': 'shounenai',
    'пародия': 'parody',
    'сёдзё': 'shoujo',
    'исторические': 'historical',
    'фэнтези': 'fantasy',
    'детские': 'kids',
    'концерт': 'concert',
    'мультсериалы': 'multseries',
    'драмы': 'drama',
    'боевики': 'action',
    'биографические': 'biographical',
    'романтические': 'romance',
    'зарубежные': 'foreign',
    'кодомо': 'kodomo',
    'криминал': 'crime',
    'путешествия': 'travel',
    'спортивные': 'sport',
    'арт-хаус': 'arthouse',
    'мистические': 'mystery',
    'короткометражные': 'short',
    'украинские': 'ukrainian',
    'стендап': 'standup',
    'ужасы': 'horror',
    'телепередачи': 'telecasts',
    'сказки': 'fairytale',
    'приключения': 'adventures',
    'познавательные': 'cognitive',
    'сёнэн': 'shounen',
    'для взрослых': 'adult',
    'полнометражные': 'full-length',
    'советские': 'soyzmyltfilm',
    'этти': 'ecchi',
    'мелодрамы': 'melodrama',
    'сёдзё-ай': 'shoujoai',
    'образовательные': 'educational',
    'документальные': 'documentary',
    'школа': 'school',
    'триллеры': 'thriller',
    'самурайский боевик': 'samurai',
    'вестерны': 'western',
    'махо-сёдзё': 'mahoushoujo',
    'эротика': 'erotic',
    'комедии': 'comedy',
    'боевые искусства': 'fighting',
    'детективы': 'detective',
    'мюзиклы': 'musical',
    'музыкальные': 'musical',
    'фантастика': 'fiction',
    'повседневность': 'everyday',
    'меха': 'mecha',
    'русские': 'russian',
    'аниме': 'anime',
    'реалити-шоу': 'reality-shows',
    'юмористические': 'humor',
    'конкурсы': 'contests',
    'охота и рыбалка': 'hunting'
}


def convert_genres(genre: str):
    return all_genres.get(genre.lower())


class GenreFilm(Enum):
    ACTION = 'action'
    ADVENTURES = 'adventures'
    ARTHOUSE = 'arthouse'
    BIOGRAPHICAL = 'biographical'
    COGNITIVE = 'cognitive'
    COMEDY = 'comedy'
    CONCERT = 'concert'
    CRIME = 'crime'
    DETECTIVE = 'detective'
    DOCUMENTARY = 'documentary'
    DRAMA = 'drama'
    EROTIC = 'erotic'
    FAMILY = 'family'
    FANTASY = 'fantasy'
    FICTION = 'fiction'
    FOREIGN = 'foreign'
    HISTORICAL = 'historical'
    HORROR = 'horror'
    KIDS = 'kids'
    MELODRAMA = 'melodrama'
    MILITARY = 'military'
    MUSICAL = 'musical'
    RUSSIAN = 'russian'
    SHORT = 'short'
    SPORT = 'sport'
    STANDUP = 'standup'
    THEATRE = 'theatre'
    THRILLER = 'thriller'
    TRAVEL = 'travel'
    UKRAINIAN = 'ukrainian'
    WESTERN = 'western'


class GenreSeries(Enum):
    ACTION = 'action'
    ADVENTURES = 'adventures'
    ARTHOUSE = 'arthouse'
    BIOGRAPHICAL = 'biographical'
    COMEDY = 'comedy'
    CRIME = 'crime'
    DETECTIVE = 'detective'
    DOCUMENTARY = 'documentary'
    DRAMA = 'drama'
    EROTIC = 'erotic'
    FAMILY = 'family'
    FANTASY = 'fantasy'
    FICTION = 'fiction'
    FOREIGN = 'foreign'
    HISTORICAL = 'historical'
    HORROR = 'horror'
    MELODRAMA = 'melodrama'
    MILITARY = 'military'
    MUSICAL = 'musical'
    REALTV = 'realtv'
    RUSSIAN = 'russian'
    SPORT = 'sport'
    STANDUP = 'standup'
    TELECASTS = 'telecasts'
    THRILLER = 'thriller'
    UKRAINIAN = 'ukrainian'
    WESTERN = 'western'


class GenreCartoons(Enum):
    ACTION = 'action'
    ADULT = 'adult'
    ADVENTURES = 'adventures'
    ANIME = 'anime'
    ARTHOUSE = 'arthouse'
    BIOGRAPHICAL = 'biographical'
    COGNITIVE = 'cognitive'
    COMEDY = 'comedy'
    CRIME = 'crime'
    DETECTIVE = 'detective'
    DOCUMENTARY = 'documentary'
    DRAMA = 'drama'
    EROTIC = 'erotic'
    FAIRYTALE = 'fairytale'
    FAMILY = 'family'
    FANTASY = 'fantasy'
    FICTION = 'fiction'
    FOREIGN = 'foreign'
    FULL_LENGTH = 'full-length'
    HISTORICAL = 'historical'
    HORROR = 'horror'
    KIDS = 'kids'
    MELODRAMA = 'melodrama'
    MILITARY = 'military'
    MULTSERIES = 'multseries'
    MUSICAL = 'musical'
    RUSSIAN = 'russian'
    SHORT = 'short'
    SOYZMYLTFILM = 'soyzmyltfilm'
    SPORT = 'sport'
    THRILLER = 'thriller'
    UKRAINIAN = 'ukrainian'
    WESTERN = 'western'


class GenreAnimation(Enum):
    ACTION = 'action'
    ADVENTURES = 'adventures'
    COMEDY = 'comedy'
    DETECTIVE = 'detective'
    DRAMA = 'drama'
    ECCHI = 'ecchi'
    EDUCATIONAL = 'educational'
    EROTIC = 'erotic'
    EVERYDAY = 'everyday'
    FAIRYTALE = 'fairytale'
    FANTASY = 'fantasy'
    FICTION = 'fiction'
    FIGHTING = 'fighting'
    HISTORICAL = 'historical'
    HORROR = 'horror'
    KIDS = 'kids'
    KODOMO = 'kodomo'
    MAHOUSHOUJO = 'mahoushoujo'
    MECHA = 'mecha'
    MILITARY = 'military'
    MUSICAL = 'musical'
    MYSTERY = 'mystery'
    PARODY = 'parody'
    ROMANCE = 'romance'
    SAMURAI = 'samurai'
    SCHOOL = 'school'
    SHOUJO = 'shoujo'
    SHOUJOAI = 'shoujoai'
    SHOUNEN = 'shounen'
    SHOUNENAI = 'shounenai'
    SPORT = 'sport'
    THRILLER = 'thriller'


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
