from unittest import TestCase, main
from HDrezka import *
from HDrezka.filters import BaseGenre


def get_genre(_class):
    base_genre = list(BaseGenre.__dict__.values())
    base_genre.remove('HDrezka.filters')
    base_genre.remove(None)
    lst_genre = list(_class.__dict__.values())
    lst_genre.remove('HDrezka.filters')
    lst_genre.remove(None)
    return lst_genre + base_genre[:14:]


class HDrezkaTest(TestCase):
    def test_name(self):
        self.assertEqual(str(HDrezka().films()), "films/")
        self.assertEqual(str(HDrezka().series()), "series/")
        self.assertEqual(str(HDrezka().cartoons()), f"cartoons/")
        self.assertEqual(str(HDrezka().animation()), f"animation/")

    def test_film_genre(self):
        for i in get_genre(GenreFilm):
            self.assertEqual(str(HDrezka().films(i)), f"films/{i}/")

    def test_series_genre(self):
        for i in get_genre(GenreSeries):
            self.assertEqual(str(HDrezka().series(i)), f"series/{i}/")

    def test_cartoon_genre(self):
        for i in get_genre(GenreFilm):
            self.assertEqual(str(HDrezka().cartoons(i)), f"cartoons/{i}/")

    def test_animation_genre(self):
        for i in get_genre(GenreFilm):
            self.assertEqual(str(HDrezka().animation(i)), f"animation/{i}/")

    def test_filter(self):
        self.assertEqual(str(HDrezka().films().filter()), f"films/?filter=last")
        self.assertEqual(str(HDrezka().series().filter()), f"series/?filter=last")
        self.assertEqual(str(HDrezka().cartoons().filter()), f"cartoons/?filter=last")
        self.assertEqual(str(HDrezka().animation().filter()), f"animation/?filter=last")

        for j in [Filters.LAST, Filters.POPULAR, Filters.SOON, Filters.WATCHING]:
            self.assertEqual(str(HDrezka().films().filter(j)), f"films/?filter={j}")
            self.assertEqual(str(HDrezka().series().filter(j)), f"series/?filter={j}")
            self.assertEqual(str(HDrezka().cartoons().filter(j)), f"cartoons/?filter={j}")
            self.assertEqual(str(HDrezka().animation().filter(j)), f"animation/?filter={j}")
            self.assertEqual(str(HDrezka().new().filter(j)), f"new/?filter={j}")

    def test_film_filter(self):
        for i in get_genre(GenreFilm):
            for j in [Filters.LAST, Filters.POPULAR, Filters.SOON, Filters.WATCHING]:
                self.assertEqual(str(HDrezka().films(i).filter(j)), f"films/{i}/?filter={j}")

    def test_series_filter(self):
        for i in get_genre(GenreSeries):
            for j in [Filters.LAST, Filters.POPULAR, Filters.SOON, Filters.WATCHING]:
                self.assertEqual(str(HDrezka().series(i).filter(j)), f"series/{i}/?filter={j}")

    def test_cartoon_filter(self):
        for i in get_genre(GenreFilm):
            for j in [Filters.LAST, Filters.POPULAR, Filters.SOON, Filters.WATCHING]:
                self.assertEqual(str(HDrezka().cartoons(i).filter(j)), f"cartoons/{i}/?filter={j}")

    def test_animation_filter(self):
        for i in get_genre(GenreFilm):
            for j in [Filters.LAST, Filters.POPULAR, Filters.SOON, Filters.WATCHING]:
                self.assertEqual(str(HDrezka().animation(i).filter(j)), f"animation/{i}/?filter={j}")

    def test_new(self):
        self.assertEqual(str(HDrezka().new()), f"new/")
        for i in [ShowCategory.ALL, ShowCategory.FILMS, ShowCategory.SERIES,
                  ShowCategory.CARTOONS, ShowCategory.ANIMATION]:
            self.assertEqual(str(HDrezka().new().filter().show_only(i)), f"new/?filter=last&genre={i}")

    def test_announce(self):
        self.assertEqual(str(HDrezka().announce()), f"announce/")

    def test_collections(self):
        self.assertEqual(str(HDrezka().collections()), f"collections/")

    def test_search(self):
        self.assertEqual(str(HDrezka().search("How Train To You Dragon")),
                         f"search/?do=search&subaction=search&q=How+Train+To+You+Dragon")

    def test_page_film(self):
        for i in get_genre(GenreFilm):
            self.assertEqual(str(HDrezka().films(i).page(12)), f"films/{i}/page/12/")

    def test_page_series(self):
        for i in get_genre(GenreSeries):
            self.assertEqual(str(HDrezka().series(i).page(13)), f"series/{i}/page/13/")

    def test_page_cartoons(self):
        for i in get_genre(GenreFilm):
            self.assertEqual(str(HDrezka().cartoons(i).page(14)), f"cartoons/{i}/page/14/")

    def test_page_animation(self):
        for i in get_genre(GenreFilm):
            self.assertEqual(str(HDrezka().animation(i).page(15)), f"animation/{i}/page/15/")


if __name__ == '__main__':
    main()
