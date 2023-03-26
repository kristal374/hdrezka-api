from unittest import TestCase, skip

from HDrezka.parse_page import Collections


class TestCollections(TestCase):
    def setUp(self) -> None:
        self.movie = Collections()

    def tearDown(self) -> None:
        del self.movie

    def test_positive_page(self):
        for page in range(1, 100):
            response = self.movie.page(page).__str__()
            correct_url = f"https://rezka.ag/collections/page/{page}/"
            self.assertEqual(correct_url, response)

    def test_negative_page(self):
        data = (0, -1, 4.458, -5.2, 6 - 10j, [5, 2, 3], (1, 2, 6), {1, 32, 3}, {"a": 1, "b": 2, "c": 3}, None,
                True, False, object, range(10), "hello world", b"hello world")
        for element in data:
            with self.assertRaises(AttributeError):
                self.movie.page(element)
                print(element)

    @skip
    def test_get(self):
        self.fail()
