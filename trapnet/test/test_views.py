from django.shortcuts import get_object_or_404
from django.test import tag
from django.urls import reverse_lazy
from faker import Factory

from shared_models.utils import dm2decdeg
from shared_models.views import CommonCreateView, CommonFilterView, CommonUpdateView, CommonDeleteView, CommonDetailView, CommonFormView
from . import FactoryFloor
from .FactoryFloor import DiveFactory
from .common_tests import ScubaCommonTest as CommonTest
from .. import views, models

faker = Factory.create()


class TestBiologicalDetailingCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('trapnet:biological_detailing_new')
        self.expected_template = 'trapnet/form.html'
        self.user = self.get_and_login_user(is_crud_user=True)

    @tag("BiologicalDetailing", "biological_detailing_new", "view")
    def test_view_class(self):
        self.assert_inheritance(views.BiologicalDetailingCreateView, CommonCreateView)

    @tag("BiologicalDetailing", "biological_detailing_new", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("BiologicalDetailing", "biological_detailing_new", "submit")
    def test_submit(self):
        data = FactoryFloor.BiologicalDetailingFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("BiologicalDetailing", "biological_detailing_new", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("trapnet:biological_detailing_new", f"/en/trapnet/biological_detailings/new/")


class TestBiologicalDetailingDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.BiologicalDetailingFactory()
        self.test_url = reverse_lazy('trapnet:biological_detailing_delete', args=[self.instance.pk, ])
        self.expected_template = 'trapnet/confirm_delete.html'
        self.user = self.get_and_login_user(is_crud_user=True)

    @tag("BiologicalDetailing", "biological_detailing_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(views.BiologicalDetailingDeleteView, CommonDeleteView)

    @tag("BiologicalDetailing", "biological_detailing_delete", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("BiologicalDetailing", "biological_detailing_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.BiologicalDetailingFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(models.BiologicalDetailing.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("BiologicalDetailing", "biological_detailing_delete", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("trapnet:biological_detailing_delete", f"/en/trapnet/biological_detailings/delete/{self.instance.pk}/", [self.instance.pk])


class TestBiologicalDetailingDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.BiologicalDetailingFactory()
        self.test_url = reverse_lazy('trapnet:biological_detailing_detail', args=[self.instance.pk, ])
        self.expected_template = 'trapnet/detail.html'
        self.user = self.get_and_login_user(is_read_only=True)

    @tag("BiologicalDetailing", "biological_detailing_detail", "view")
    def test_view_class(self):
        self.assert_inheritance(views.BiologicalDetailingDetailView, CommonDetailView)

    @tag("BiologicalDetailing", "biological_detailing_detail", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("BiologicalDetailing", "biological_detailing_detail", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("trapnet:biological_detailing_detail", f"/en/trapnet/biological_detailings/view/{self.instance.pk}/", [self.instance.pk])


class TestBiologicalDetailingListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('trapnet:biological_detailing_list')
        self.expected_template = 'trapnet/list.html'
        self.user = self.get_and_login_user(is_read_only=True)

    @tag("BiologicalDetailing", "biological_detailing_list", "view")
    def test_view_class(self):
        self.assert_inheritance(views.BiologicalDetailingListView, CommonFilterView)

    @tag("BiologicalDetailing", "biological_detailing_list", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("BiologicalDetailing", "biological_detailing_list", "context")
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    @tag("BiologicalDetailing", "biological_detailing_list", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("trapnet:biological_detailing_list", f"/en/trapnet/biological_detailings/")


class TestBiologicalDetailingUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.BiologicalDetailingFactory()
        self.test_url = reverse_lazy('trapnet:biological_detailing_edit', args=[self.instance.pk, ])
        self.expected_template = 'trapnet/form.html'
        self.user = self.get_and_login_user(is_crud_user=True)

    @tag("BiologicalDetailing", "biological_detailing_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.BiologicalDetailingUpdateView, CommonUpdateView)

    @tag("BiologicalDetailing", "biological_detailing_edit", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("BiologicalDetailing", "biological_detailing_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.BiologicalDetailingFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("BiologicalDetailing", "biological_detailing_edit", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("trapnet:biological_detailing_edit", f"/en/trapnet/biological_detailings/edit/{self.instance.pk}/", [self.instance.pk])
