import string
import unittest
import random
from nebula_model.ngql.schema.space import show_spaces, create_space, VidTypeEnum, drop_space, use_space
from tests.base import TestWithNewSpace


class TestSpace(TestWithNewSpace):
    def test_show_spaces(self):
        self.assertTrue(self.test_space_name in show_spaces())

    # def test_use_space(self):
    #