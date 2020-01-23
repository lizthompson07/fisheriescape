from django.test import TestCase, tag
from django.urls import reverse_lazy
from django.utils.translation import activate

from whalesdb import views, models


class CommonTest(TestCase):
    test_url = None
    test_expected_template = None
    login_url_base = '/accounts/login_required/?next='
    login_url_en = login_url_base + "/en/"
    login_url_fr = login_url_base + "/fr/"


class TestIndexView(CommonTest):

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

        # expect to see an 'entry form' section as the first element of section
        entry_forms = response.context['section'][0]

        self.assertEquals('Entry Forms', entry_forms['title'])

        # Expected there to be a station list object
        stn_list = entry_forms['forms'][0]
        self.assertEquals('Station List', stn_list['title'])


class ListTest(CommonTest):

    def setUp(self):
        super().setUp()

        self.test_expected_template = 'whalesdb/whale_filter.html'

    # Users doesn't have to be logged in to view a list
    def test_list_en(self):
        activate('en')

        response = self.client.get(self.test_url)

        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed(self.test_expected_template)

    # Users doesn't have to be logged in to view a list
    def test_list_fr(self):
        activate('fr')

        response = self.client.get(self.test_url)

        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed(self.test_expected_template)

    # List context should return:
    #   - a list of fields to display
    #   - a title to display in the html template
    def test_list_context_fields(self):
        activate('en')

        response = self.client.get(self.test_url)

        self.assertIn("fields", response.context)
        self.assertIn("title", response.context)


class TestListStation(ListTest):

    def setUp(self):
        super().setUp()

        self.test_url = reverse_lazy('whalesdb:list_stn')


class TestListProject(ListTest):

    def setUp(self):
        super().setUp()

        self.test_url = reverse_lazy('whalesdb:list_prj')


class TestCreateStation(CommonTest):
    def setUp(self):
        super().setUp()

        self.test_url = reverse_lazy('whalesdb:create_stn')

        # Since this is intended to be used as a pop-out form, the html file should start with an underscore
        self.test_expected_template = 'whalesdb/_stn_form.html'

    # Users must be logged in to create new stations
    @tag('create_stn', 'response', 'access')
    def test_create_stn_en(self):
        activate('en')

        response = self.client.get(self.test_url)

        # user not logged in, should get 302 redirect to login page.
        self.assertEquals(302, response.status_code)
        self.assertTemplateUsed(self.test_expected_template)

    # Users must be logged in to create new stations
    @tag('create_stn', 'response', 'access')
    def test_create_stn_fr(self):
        activate('fr')

        response = self.client.get(self.test_url)

        # user not logged in, should get 302 redirect to login page.
        self.assertEquals(302, response.status_code)
        self.assertTemplateUsed(self.test_expected_template)


class TestDetailsStation(CommonTest):

    station_dic = None

    def createStn(self):
        if self.station_dic:
            return self.station_dic

        self.station_dic = {}

        stn_1 = models.StnStation(stn_name='Station 1', stn_code='ST1', stn_revision=1, stn_planned_lat=52,
                                  stn_planned_lon=25, stn_planned_depth=1)
        stn_1.save()

        self.station_dic['stn_1'] = stn_1

        return self.station_dic

    def setUp(self):
        super().setUp()

        stn_dic = self.createStn()

        self.test_url = reverse_lazy('whalesdb:details_stn', args=(stn_dic['stn_1'].pk,))
        self.test_expected_template = 'whalesdb/station_details.html'

    # Station Details are visible to all
    @tag('details_stn', 'response', 'access')
    def test_details_stn_en(self):
        activate('en')

        response = self.client.get(self.test_url)

        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed(self.test_expected_template)

    # Station Details are visible to all
    @tag('details_stn', 'response', 'access')
    def test_details_stn_fr(self):
        activate('fr')

        response = self.client.get(self.test_url)

        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed(self.test_expected_template)
