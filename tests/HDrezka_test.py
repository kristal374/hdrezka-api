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

    def test_page_new(self):
        self.assertEqual(str(HDrezka().new()), f"new/")
        for i in [ShowCategory.ALL, ShowCategory.FILMS, ShowCategory.SERIES,
                  ShowCategory.CARTOONS, ShowCategory.ANIMATION]:
            self.assertEqual(str(HDrezka().new().filter().show_only(i).page(3)), f"new/page/3/?filter=last&genre={i}")

    def test_page_filter(self):
        self.assertEqual(str(HDrezka().films().filter().page(1)), f"films/page/1/?filter=last")
        self.assertEqual(str(HDrezka().series().filter().page(2)), f"series/page/2/?filter=last")
        self.assertEqual(str(HDrezka().cartoons().filter().page(3)), f"cartoons/page/3/?filter=last")
        self.assertEqual(str(HDrezka().animation().filter().page(4)), f"animation/page/4/?filter=last")

        for j in [Filters.LAST, Filters.POPULAR, Filters.SOON, Filters.WATCHING]:
            self.assertEqual(str(HDrezka().films().filter(j).page(5)), f"films/page/5/?filter={j}")
            self.assertEqual(str(HDrezka().series().filter(j).page(6)), f"series/page/6/?filter={j}")
            self.assertEqual(str(HDrezka().cartoons().filter(j).page(7)), f"cartoons/page/7/?filter={j}")
            self.assertEqual(str(HDrezka().animation().filter(j).page(8)), f"animation/page/8/?filter={j}")
            self.assertEqual(str(HDrezka().new().filter(j).page(9)), f"new/page/9/?filter={j}")

    def test_page_announce(self):
        self.assertEqual(str(HDrezka().announce().page(4)), f"announce/page/4/")

    def test_page_collections(self):
        self.assertEqual(str(HDrezka().collections().page(5)), f"collections/page/5/")

    def test_page_search(self):
        self.assertEqual(str(HDrezka().search("How Train To You Dragon").page(6)),
                         f"search/?do=search&subaction=search&q=How+Train+To+You+Dragon&page=6")

    def test_best_film(self):
        for i in get_genre(GenreFilm):
            self.assertEqual(str(HDrezka().films(i).find_best()), f"films/best/{i}/")
            self.assertEqual(str(HDrezka().films().find_best(genre=i, year=2021)), f"films/best/{i}/2021/")

    def test_best_series(self):
        for i in get_genre(GenreSeries):
            self.assertEqual(str(HDrezka().series(i).find_best()), f"series/best/{i}/")
            self.assertEqual(str(HDrezka().series().find_best(genre=i, year=2022)), f"series/best/{i}/2022/")

    def test_best_cartoon(self):
        for i in get_genre(GenreFilm):
            self.assertEqual(str(HDrezka().cartoons(i).find_best()), f"cartoons/best/{i}/")
            self.assertEqual(str(HDrezka().cartoons().find_best(genre=i, year=2023)), f"cartoons/best/{i}/2023/")

    def test_best_animation(self):
        for i in get_genre(GenreFilm):
            self.assertEqual(str(HDrezka().animation(i).find_best()), f"animation/best/{i}/")
            self.assertEqual(str(HDrezka().animation().find_best(genre=i, year=2024)), f"animation/best/{i}/2024/")

    def test_best_page_film(self):
        for i in get_genre(GenreFilm):
            self.assertEqual(str(HDrezka().films(i).find_best().page(7)), f"films/best/{i}/page/7/")

    def test_best_page_series(self):
        for i in get_genre(GenreSeries):
            self.assertEqual(str(HDrezka().series(i).find_best().page(8)), f"series/best/{i}/page/8/")

    def test_best_page_cartoon(self):
        for i in get_genre(GenreFilm):
            self.assertEqual(str(HDrezka().cartoons(i).find_best().page(9)), f"cartoons/best/{i}/page/9/")

    def test_best_page_animation(self):
        for i in get_genre(GenreFilm):
            self.assertEqual(str(HDrezka().animation(i).find_best().page(10)), f"animation/best/{i}/page/10/")


if __name__ == '__main__':
    main()
