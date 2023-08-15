from unittest import TestCase
from HDrezka import HDrezka, ShowCategory


class TestHDrezka(TestCase):

    def setUp(self) -> None:
        self.rezka = HDrezka()

    def tearDown(self) -> None:
        del self.rezka

    def test_url(self):
        self.assertEqual("https://rezka.ag", self.rezka.__str__())

    def test_film(self):
        self.assertEqual("https://rezka.ag/films/", self.rezka.films().__str__())

    def test_series(self):
        self.assertEqual("https://rezka.ag/series/", self.rezka.series().__str__())

    def test_cartoon(self):
        self.assertEqual("https://rezka.ag/cartoons/", self.rezka.cartoons().__str__())

    def test_new(self):
        self.assertEqual("https://rezka.ag/new/", self.rezka.new().__str__())

        for i in (ShowCategory.ALL, ShowCategory.FILMS, ShowCategory.SERIES,
                  ShowCategory.CARTOONS, ShowCategory.ANIMATION):
            response = self.rezka.new().filter().show_only(i).__str__()
            correct_url = f"https://rezka.ag/new/?filter=last{'&genre=' + str(i) if i != 0 else ''}"
            self.assertEqual(correct_url, response)

    def test_animation(self):
        self.assertEqual("https://rezka.ag/animation/", self.rezka.animation().__str__())

    def test_announce(self):
        self.assertEqual("https://rezka.ag/announce/", self.rezka.announce().__str__())

    def test_collections(self):
        self.assertEqual("https://rezka.ag/collections/", self.rezka.collections().__str__())

    def test_search(self):
        response = self.rezka.search("How Train To You Dragon").__str__()
        correct_url = "https://rezka.ag/search/?do=search&subaction=search&q=How+Train+To+You+Dragon"
        self.assertEqual(correct_url, response)
