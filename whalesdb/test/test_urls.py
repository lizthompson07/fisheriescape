from django.test import tag

from django.urls import reverse, resolve
from django.test import TestCase
from django.utils.translation import activate

from whalesdb import urls, views


class URLTest(TestCase):

    # test that a url signature can be reversed into an address,
    # an address gives an expected signature and the address
    # will link to the expected view or function
    def basic_en_url_test(self, signature, url, view, args=None):
        activate('en')
        en_url = "/en/{}".format(url)

        # Test a URL can be reversed
        if args:
            addr = reverse(signature, args=args)
        else:
            addr = reverse(signature)

        self.assertEqual(addr, en_url)

        # Test the URL can be resolved
        found = resolve(en_url)
        self.assertEqual(found.view_name, signature)

        # Test the resolved URL points to the proper view
        self.assertEqual(found.func.__name__, view.__name__)

    @tag('index', 'url')
    def test_root_url_index_view(self):
        self.basic_en_url_test('whalesdb:index', 'whalesdb/', views.IndexView)

    @tag('close', 'url')
    def test_close_url_close_view(self):
        self.basic_en_url_test('whalesdb:close_me', 'whalesdb/close', views.CloserTemplateView)

    @tag('dep', 'url', 'create')
    def test_url_create_dep_view(self):
        self.basic_en_url_test('whalesdb:create_dep', 'whalesdb/create/dep/', views.CreateDep)

    @tag('dep', 'url', 'update')
    def test_url_update_dep_view(self):
        self.basic_en_url_test('whalesdb:update_dep', 'whalesdb/update/dep/1/', views.UpdateDep, {1})

    @tag('dep', 'url', 'list')
    def test_url_list_dep_view(self):
        self.basic_en_url_test('whalesdb:list_dep', 'whalesdb/list/dep/', views.ListDep)

    @tag('dep', 'url', 'details')
    def test_url_details_dep_view(self):
        self.basic_en_url_test('whalesdb:details_dep', 'whalesdb/details/dep/1/', views.DetailsDep, {1})

    @tag('mor', 'url', 'create')
    def test_url_create_mor_view(self):
        self.basic_en_url_test('whalesdb:create_mor', 'whalesdb/create/mor/', views.CreateMor)

    @tag('mor', 'url', 'update')
    def test_url_update_mor_view(self):
        self.basic_en_url_test('whalesdb:update_mor', 'whalesdb/update/mor/1/', views.UpdateMor, {1})

    @tag('mor', 'url', 'list')
    def test_url_list_mor_view(self):
        self.basic_en_url_test('whalesdb:list_mor', 'whalesdb/list/mor/', views.ListMor)

    @tag('mor', 'url', 'details')
    def test_url_details_mor_view(self):
        self.basic_en_url_test('whalesdb:details_mor', 'whalesdb/details/mor/1/', views.DetailsMor, {1})

    @tag('prj', 'url', 'create')
    def test_url_create_prj_view(self):
        self.basic_en_url_test('whalesdb:create_prj', 'whalesdb/create/prj/', views.CreatePrj)

    @tag('prj', 'url', 'update')
    def test_url_update_prj_view(self):
        self.basic_en_url_test('whalesdb:update_prj', 'whalesdb/update/prj/1/', views.UpdatePrj, {1})

    @tag('prj', 'url', 'list')
    def test_url_list_prj_view(self):
        self.basic_en_url_test('whalesdb:list_prj', 'whalesdb/list/prj/', views.ListPrj)

    @tag('prj', 'url', 'details')
    def test_url_details_prj_view(self):
        self.basic_en_url_test('whalesdb:details_prj', 'whalesdb/details/prj/1/', views.DetailsPrj, {1})

    @tag('stn', 'url', 'create')
    def test_url_create_stn_view(self):
        self.basic_en_url_test('whalesdb:create_stn', 'whalesdb/create/stn/', views.CreateStn)

    @tag('stn', 'url', 'update')
    def test_url_update_stn_view(self):
        self.basic_en_url_test('whalesdb:update_stn', 'whalesdb/update/stn/1/', views.UpdateStn, {1})

    @tag('stn', 'url', 'list')
    def test_url_list_stn_view(self):
        self.basic_en_url_test('whalesdb:list_stn', 'whalesdb/list/stn/', views.ListStn)

    @tag('stn', 'url', 'details')
    def test_url_details_stn_view(self):
        self.basic_en_url_test('whalesdb:details_stn', 'whalesdb/details/stn/1/', views.DetailsStn, {1})

    @tag('ste', 'url', 'create')
    def test_url_create_ste_view(self):
        self.basic_en_url_test('whalesdb:create_ste', 'whalesdb/create/ste/', views.CreateSte)

