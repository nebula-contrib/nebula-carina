import string
import unittest
import random
from nebula_model.ngql.schema.space import show_spaces, create_space, VidTypeEnum


class TestConnection(unittest.TestCase):
    test_space_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

    @classmethod
    def setUpClass(cls):
        assert cls.test_space_name not in show_spaces()
        create_space(cls.test_space_name, VidTypeEnum.FIXED_STRING_16)

    def setUp(self):
        pass

    def tearDown(self):
        print("do something after test : clean up.\n")

    def test_add(self):
        """Test method add(a, b)"""
        self.assertEqual(1, 1)
        self.assertNotEqual(1, 2)
