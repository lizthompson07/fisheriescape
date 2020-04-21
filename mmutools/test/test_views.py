from django.test import tag
from django.urls import reverse_lazy
from django.utils.translation import activate

from mmutools.test.common_tests import CommonMMUToolsTest as CommonTest
from .. import views

class TestIndexView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('mmutools:index')
        self.expected_template = 'mmutools/index.html'

    @tag("mmutools", 'index', "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url)

