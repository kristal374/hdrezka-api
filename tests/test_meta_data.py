from unittest import TestCase

import HDrezka


class TestMetaData(TestCase):
    def test_metadata_variables(self):
        def is_non_empty_string(s):
            self.assertIsInstance(s, (str, bytes))
            self.assertEqual(bool(s), True, msg=f"Element is empty")

        is_non_empty_string(HDrezka.__title__)
        is_non_empty_string(HDrezka.__version__)
        is_non_empty_string(HDrezka.__license__)
        is_non_empty_string(HDrezka.__author__)
        is_non_empty_string(HDrezka.__contact__)
        is_non_empty_string(HDrezka.__url__)
        is_non_empty_string(HDrezka.__description__)
