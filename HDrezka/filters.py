from dataclasses import dataclass

__all__ = ['GenreFilm', 'GenreCartoons', 'GenreSeries', 'GenreAnimation', 'Filters', 'ShowCategory']


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


class GenreFilm(MediaGenres):
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


class GenreCartoons(MediaGenres):
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
