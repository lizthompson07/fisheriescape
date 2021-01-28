from django.test import tag

from .common_tests import CommonTest
from ..utils import decdeg2dm, dm2decdeg


class TestUtils(CommonTest):

    def setUp(self):
        super().setUp()  # used to import fixutres

    @tag("Utils", 'decdeg2dm')
    def test_decdeg2dm(self):
        self.assertEqual(decdeg2dm(90.55), (90, 33))
        self.assertEqual(decdeg2dm(-90.55), (-90, 33))

    @tag("Utils", 'dm2decdeg')
    def test_dm2decdeg(self):
        self.assertEqual(dm2decdeg(90, 33), 90.55)
        self.assertEqual(dm2decdeg(-90, 33), -90.55)
