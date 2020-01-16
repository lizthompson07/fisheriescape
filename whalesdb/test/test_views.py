from django.test import TestCase, tag
from django.urls import reverse_lazy
from django.utils.translation import activate

from whalesdb import views


class TestCommon(TestCase):
    test_url = None
    test_expected_template = None
    login_url_base = '/accounts/login_required/?next='
    login_url_en = login_url_base + "/en/"
    login_url_fr = login_url_base + "/fr/"


class TestIndexView(TestCommon):

    def setUp(self):
        super().setUp()

        self.test_url = reverse_lazy('whalesdb:index')
        self.test_expected_template = 'whalesdb/index.html'

    # Users should be able to view the whales index page which corresponds to the whalesdb/index.html template
    @tag('index_view', 'response', 'access')
    def test_index_view_en(self):
        activate('en')

        response = self.client.get(self.test_url)

        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed(self.test_expected_template)

    # Users should be able to view the whales index page corresponding to the whalesdb/index.html template, in French
    @tag('index_view', 'response', 'access')
    def test_index_view_fr(self):
        activate('fr')

        response = self.client.get(self.test_url)

        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed(self.test_expected_template)

    # The index view should return a context to be used on the index.html template
    # this should consist of a "Sections" dictionary containing sub-sections
    @tag('index_view', 'context')
    def test_index_view_context(self):
        activate('en')

        response = self.client.get(self.test_url)

        # expect to see section in the context
        self.assertIn("section", response.context)

        # expect to see 'entry' object under section
        self.assertIn('entry', response.context['section'])
