from unittest import TestCase, skip

from HDrezka.parse_page import Announce


class TestAnnounce(TestCase):
    def setUp(self) -> None:
        self.movie = Announce()

    def tearDown(self) -> None:
        del self.movie

    def test_positive_page(self):
        for page in range(1, 100):
            response = self.movie.page(page).__str__()
            correct_url = f"https://rezka.ag/announce/page/{page}/"
            self.assertEqual(correct_url, response)

            response = self.movie.page(str(page)).__str__()  # noqa
            self.assertEqual(correct_url, response)

    def test_negative_page(self):
        data = (0, -4, 4.458, -5.2, 6 - 10j, [5, 2, 3], (1, 2, 3), {1, 32, 3}, {"a": 1, "b": 2, "c": 3}, None,
                True, False, object, range(10), "hello world", b"hello world")
        for element in data:
            with self.assertRaises(AttributeError, msg=element):
                self.movie.page(element)


    @skip
    def test_get(self):
        self.fail()
