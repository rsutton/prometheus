import unittest

from pythiam.lib.iam_manager import IAMManager


class IAMManagerTests(unittest.TestCase):
    m = IAMManager()

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_delete_non_existent_user_exits(self):
        self.assertFalse(self.m.delete_user('foo'))
