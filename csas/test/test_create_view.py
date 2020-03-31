from django.test import TestCase, RequestFactory
from django.urls import reverse_lazy
from django.contrib.auth.models import AnonymousUser

from csas.views import CsasCreateCommon, RequestEntry
from csas.test import csas_common_test as cct

from csas import models

from shared_models import views as shared_views


class CreateCommonTest(TestCase):

    view = None

    def setUp(self) -> None:
        self.view = CsasCreateCommon()
        self.view.title = 'EXAMPLE TITLE'

    def test_create_extends(self):
        self.assertIsInstance(self.view, shared_views.CreateCommon)

    def test_create_nav_menu(self):
        nav = self.view.get_nav_menu()
        self.assertEquals(nav, cct.EXPECTED_NAV)

    def test_create_css(self):
        css = self.view.get_site_css()
        self.assertEquals(css, cct.EXPECTED_CSS)


class ReqCreateViewTest(TestCase):

    view = None

    def setUp(self) -> None:
        self.view = RequestEntry()

    def test_req_create_extends(self):
        self.assertIsInstance(self.view, CsasCreateCommon)

    def test_req_create_model(self):
        self.assertEquals(self.view.model, models.ReqRequest)

    def test_req_redirect(self):
        addr = self.view.get_success_url()
        self.assertEquals(addr, reverse_lazy('csas:list_req'))

    def test_req_test_func_fail(self):
        # have to initialize the view as though Django did it.
        req_factory = RequestFactory()
        request = req_factory.get(reverse_lazy("csas:create_req"))
        request.user = AnonymousUser()

        view = cct.setup_view(self.view, request)

        auth = view.test_func()

        self.assertFalse(auth)

    def test_req_test_func_pass(self):

        # have to initialize the view as though Django did it.
        req_factory = RequestFactory()
        request = req_factory.get(reverse_lazy("csas:create_req"))

        request.user = cct.login_csas_user(self)

        view = cct.setup_view(self.view, request)

        auth = view.test_func()

        self.assertTrue(auth)
