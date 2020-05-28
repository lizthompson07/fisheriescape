from django.test import tag
from django.urls import reverse_lazy
from django.utils.translation import activate

from whalebrary.test.common_tests import CommonWhalebraryTest as CommonTest
from .. import views

class TestIndexView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('whalebrary:index')
        self.expected_template = 'whalebrary/index.html'

    @tag("whalebrary", 'index', "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url)

