from unittest import TestCase

from HDrezka import __version__


class TestMetaData(TestCase):
    def test_metadata_variables(self):
        def is_non_empty_string(s):
            self.assertIsInstance(s, (str, bytes))
            self.assertEqual(bool(s), True, msg="Element is empty")

        is_non_empty_string(__version__.__title__)
        is_non_empty_string(__version__.__version__)
        is_non_empty_string(__version__.__license__)
        is_non_empty_string(__version__.__author__)
        is_non_empty_string(__version__.__contact__)
        is_non_empty_string(__version__.__url__)
        is_non_empty_string(__version__.__description__)
