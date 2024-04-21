from unittest import TestCase

from HDrezka import HDrezka, ShowCategory


class TestHDrezka(TestCase):

    def setUp(self) -> None:
        self.rezka = HDrezka()

    def tearDown(self) -> None:
        del self.rezka

    def test_url(self):
        self.assertEqual("https://rezka.ag/", str(self.rezka))

    def test_film(self):
        self.assertEqual("https://rezka.ag/films/", str(self.rezka.films()))

    def test_series(self):
        self.assertEqual("https://rezka.ag/series/", str(self.rezka.series()))

    def test_cartoon(self):
        self.assertEqual("https://rezka.ag/cartoons/", str(self.rezka.cartoons()))

    def test_new(self):
        self.assertEqual("https://rezka.ag/new/", str(self.rezka.new()))

        for i in (ShowCategory.ALL, ShowCategory.FILMS, ShowCategory.SERIES,
                  ShowCategory.CARTOONS, ShowCategory.ANIMATION):
            response = str(self.rezka.new().filter().show_only(i))

            correct_url = f"https://rezka.ag/new/{f'?filter=last&genre={i.value}' if i.value != 0 else ''}"
            self.assertEqual(correct_url, response)

    def test_animation(self):
        self.assertEqual("https://rezka.ag/animation/", str(self.rezka.animation()))

    def test_announce(self):
        self.assertEqual("https://rezka.ag/announce/", str(self.rezka.announce()))

    def test_collections(self):
        self.assertEqual("https://rezka.ag/collections/", str(self.rezka.collections()))

    def test_search(self):
        response = str(self.rezka.search("How Train To You Dragon"))
        correct_url = "https://rezka.ag/search/?do=search&subaction=search&q=How+Train+To+You+Dragon"
        self.assertEqual(correct_url, response)
