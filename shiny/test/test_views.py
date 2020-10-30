from django.contrib.auth.mixins import LoginRequiredMixin
from django.test import tag
from django.urls import reverse_lazy

from shared_models.views import CommonCreateView, CommonDeleteView, CommonFilterView, CommonUpdateView
from shiny.test import FactoryFloor
from shiny.test.common_tests import CommonShinyTest as CommonTest
from .. import views, models


class TestAppCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.AppFactory()
        self.test_url = reverse_lazy('shiny:create')
        self.expected_template = 'shared_models/generic_form.html'

    @tag("shiny", 'create', "view")
    def test_view_class(self):
        self.assert_inheritance(views.AppCreateView, CommonCreateView)
        self.assert_inheritance(views.AppCreateView, LoginRequiredMixin)

    @tag("shiny", 'create', "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template)

    @tag("shiny", 'create', "submit")
    def test_submit(self):
        data = FactoryFloor.AppFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data)


class TestAppDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.AppFactory()
        self.test_url = reverse_lazy('shiny:delete', kwargs={"pk": self.instance.pk})
        self.expected_template = 'shared_models/generic_confirm_delete.html'

    @tag("shiny", 'delete', "view")
    def test_view_class(self):
        self.assert_inheritance(views.AppDeleteView, CommonDeleteView)

    @tag("shiny", 'delete', "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template)

    @tag("shiny", 'delete', "submit")
    def test_submit(self):
        data = FactoryFloor.AppFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data)

        # for delete views...
        self.assertEqual(models.App.objects.filter(pk=self.instance.pk).count(), 0)


class TestAppListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.AppFactory()
        self.test_url = reverse_lazy('shiny:index')
        self.expected_template = 'shiny/index.html'

    @tag("shiny", 'list', "view")
    def test_view_class(self):
        self.assert_inheritance(views.IndexTemplateView, CommonFilterView)

    @tag("shiny", 'list', "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_public_view(test_url=self.test_url, expected_template=self.expected_template)

    @tag("shiny", 'list', "context")
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars)


class TestAppUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.AppFactory()
        self.test_url = reverse_lazy('shiny:update', kwargs={"pk": self.instance.pk})
        self.expected_template = 'shared_models/generic_form.html'

    @tag("shiny", 'update', "view")
    def test_view_class(self):
        self.assert_inheritance(views.AppUpdateView, CommonUpdateView)

    @tag("shiny", 'update', "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template)

    @tag("shiny", 'update', "submit")
    def test_submit(self):
        data = FactoryFloor.AppFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data)
