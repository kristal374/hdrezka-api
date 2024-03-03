from dataclasses import dataclass

__all__ = ['GenreFilm', 'GenreCartoons', 'GenreSeries', 'GenreAnimation',
           'Filters', 'ShowCategory', 'convert_genres', "all_genres"]

all_genres = {'военные': 'military',
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
              'охота и рыбалка': 'hunting'}


def convert_genres(genre: str):
    return all_genres.get(genre.lower())


class MediaGenres:
    FANTASY = 'fantasy'
    SPORT = 'sport'
    DETECTIVE = 'detective'
    DRAMA = 'drama'
    MUSICAL = 'musical'
    ADVENTURES = 'adventures'
    HISTORICAL = 'historical'
    COMEDY = 'comedy'
    ACTION = 'action'
    HORROR = 'horror'
    MILITARY = 'military'
    EROTIC = 'erotic'
    FICTION = 'fiction'
    THRILLER = 'thriller'


class GenreCartoons(MediaGenres):
    FAMILY = 'family'
    FOREIGN = 'foreign'
    SOYZMYLTFILM = 'soyzmyltfilm'
    FAIRYTALE = 'fairytale'
    ARTHOUSE = 'arthouse'
    ADULT = 'adult'
    WESTERN = 'western'
    RUSSIAN = 'russian'
    CRIME = 'crime'
    MULTSERIES = 'multseries'
    SHORT = 'short'
    FULL_LENGTH = 'full-length'
    BIOGRAPHICAL = 'biographical'
    COGNITIVE = 'cognitive'
    DOCUMENTARY = 'documentary'
    KIDS = 'kids'
    MELODRAMA = 'melodrama'
    UKRAINIAN = 'ukrainian'


class GenreFilm(MediaGenres):
    FAMILY = 'family'
    STANDUP = 'standup'
    FOREIGN = 'foreign'
    CONCERT = 'concert'
    ARTHOUSE = 'arthouse'
    UKRAINIAN = 'ukrainian'
    TRAVEL = 'travel'
    WESTERN = 'western'
    RUSSIAN = 'russian'
    CRIME = 'crime'
    SHORT = 'short'
    BIOGRAPHICAL = 'biographical'
    COGNITIVE = 'cognitive'
    DOCUMENTARY = 'documentary'
    KIDS = 'kids'
    MELODRAMA = 'melodrama'
    THEATRE = 'theatre'


class GenreSeries(MediaGenres):
    STANDUP = 'standup'
    FAMILY = 'family'
    FOREIGN = 'foreign'
    ARTHOUSE = 'arthouse'
    WESTERN = 'western'
    RUSSIAN = 'russian'
    CRIME = 'crime'
    TELECASTS = 'telecasts'
    BIOGRAPHICAL = 'biographical'
    DOCUMENTARY = 'documentary'
    REALTV = 'realtv'
    MELODRAMA = 'melodrama'
    UKRAINIAN = 'ukrainian'


class GenreAnimation(MediaGenres):
    MECHA = 'mecha'
    SAMURAI = 'samurai'
    FIGHTING = 'fighting'
    SHOUNENAI = 'shounenai'
    KODOMO = 'kodomo'
    FAIRYTALE = 'fairytale'
    ECCHI = 'ecchi'
    PARODY = 'parody'
    SHOUJOAI = 'shoujoai'
    MAHOUSHOUJO = 'mahoushoujo'
    MYSTERY = 'mystery'
    ROMANCE = 'romance'
    SHOUNEN = 'shounen'
    SHOUJO = 'shoujo'
    EVERYDAY = 'everyday'
    KIDS = 'kids'
    SCHOOL = 'school'
    EDUCATIONAL = 'educational'


@dataclass
class Filters:
    LAST = "last"  # Последние поступления
    POPULAR = "popular"  # Популярные
    SOON = "soon"  # В ожидании
    WATCHING = "watching"  # Сейчас смотрят


class ShowCategory:
    ALL = 0
    FILMS = 1
    SERIES = 2
    CARTOONS = 3
    ANIMATION = 82
