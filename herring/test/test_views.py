from django.test import tag
from django.urls import reverse_lazy
from faker import Factory

from shared_models.models import Port
from shared_models.views import CommonCreateView, CommonFilterView, CommonUpdateView, CommonDeleteView, CommonDetailView, CommonFormView, CommonTemplateView, \
    CommonListView
from . import FactoryFloor
from .common_tests import CommonHerringTest as CommonTest
from .. import views, models

faker = Factory.create()


class TestSpeciesCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('herring:species_new')
        self.expected_template = 'herring/form.html'
        self.user = self.get_and_login_user(is_crud_user=True)

    @tag("Species", "species_new", "view")
    def test_view_class(self):
        self.assert_inheritance(views.SpeciesCreateView, CommonCreateView)

    @tag("Species", "species_new", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Species", "species_new", "submit")
    def test_submit(self):
        data = FactoryFloor.SpeciesFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Species", "species_new", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("herring:species_new", f"/en/herman/species/new/")


class TestSpeciesDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SpeciesFactory()
        self.test_url = reverse_lazy('herring:species_delete', args=[self.instance.pk, ])
        self.expected_template = 'herring/confirm_delete.html'
        self.user = self.get_and_login_user(is_crud_user=True)

    @tag("Species", "species_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(views.SpeciesDeleteView, CommonDeleteView)

    @tag("Species", "species_delete", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Species", "species_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.SpeciesFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(models.Species.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("Species", "species_delete", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("herring:species_delete", f"/en/herman/species/delete/{self.instance.pk}/", [self.instance.pk])


class TestSpeciesDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SpeciesFactory()
        self.test_url = reverse_lazy('herring:species_detail', args=[self.instance.pk, ])
        self.expected_template = 'herring/detail.html'
        self.user = self.get_and_login_user(is_read_only=True)

    @tag("Species", "species_detail", "view")
    def test_view_class(self):
        self.assert_inheritance(views.SpeciesDetailView, CommonDetailView)

    @tag("Species", "species_detail", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Species", "species_detail", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("herring:species_detail", f"/en/herman/species/view/{self.instance.pk}/", [self.instance.pk])


class TestSpeciesListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('herring:species_list')
        self.expected_template = 'herring/list.html'
        self.user = self.get_and_login_user(is_read_only=True)

    @tag("Species", "species_list", "view")
    def test_view_class(self):
        self.assert_inheritance(views.SpeciesListView, CommonFilterView)

    @tag("Species", "species_list", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Species", "species_list", "context")
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    @tag("Species", "species_list", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("herring:species_list", f"/en/herman/species/")


class TestSpeciesUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SpeciesFactory()
        self.test_url = reverse_lazy('herring:species_edit', args=[self.instance.pk, ])
        self.expected_template = 'herring/form.html'
        self.user = self.get_and_login_user(is_crud_user=True)

    @tag("Species", "species_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.SpeciesUpdateView, CommonUpdateView)

    @tag("Species", "species_edit", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Species", "species_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.SpeciesFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Species", "species_edit", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("herring:species_edit", f"/en/herman/species/edit/{self.instance.pk}/", [self.instance.pk])


class TestPortCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('herring:port_new')
        self.expected_template = 'herring/form.html'
        self.user = self.get_and_login_user(is_admin=True)

    @tag("Port", "port_new", "view")
    def test_view_class(self):
        self.assert_inheritance(views.PortCreateView, CommonCreateView)

    @tag("Port", "port_new", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Port", "port_new", "submit")
    def test_submit(self):
        data = FactoryFloor.PortFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Port", "port_new", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("herring:port_new", f"/en/herman/ports/new/")


class TestPortDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.PortFactory()
        self.test_url = reverse_lazy('herring:port_delete', args=[self.instance.pk, ])
        self.expected_template = 'herring/confirm_delete.html'
        self.user = self.get_and_login_user(is_admin=True)

    @tag("Port", "port_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(views.PortDeleteView, CommonDeleteView)

    @tag("Port", "port_delete", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Port", "port_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.PortFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(Port.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("Port", "port_delete", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("herring:port_delete", f"/en/herman/ports/delete/{self.instance.pk}/", [self.instance.pk])


class TestPortDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.PortFactory()
        self.test_url = reverse_lazy('herring:port_detail', args=[self.instance.pk, ])
        self.expected_template = 'herring/detail.html'
        self.user = self.get_and_login_user(is_admin=True)

    @tag("Port", "port_detail", "view")
    def test_view_class(self):
        self.assert_inheritance(views.PortDetailView, CommonDetailView)

    @tag("Port", "port_detail", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Port", "port_detail", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("herring:port_detail", f"/en/herman/ports/view/{self.instance.pk}/", [self.instance.pk])


class TestPortListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('herring:port_list')
        self.expected_template = 'herring/list.html'
        self.user = self.get_and_login_user(is_admin=True)

    @tag("Port", "port_list", "view")
    def test_view_class(self):
        self.assert_inheritance(views.PortListView, CommonFilterView)

    @tag("Port", "port_list", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Port", "port_list", "context")
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    @tag("Port", "port_list", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("herring:port_list", f"/en/herman/ports/")


class TestPortUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.PortFactory()
        self.test_url = reverse_lazy('herring:port_edit', args=[self.instance.pk, ])
        self.expected_template = 'herring/form.html'
        self.user = self.get_and_login_user(is_admin=True)

    @tag("Port", "port_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.PortUpdateView, CommonUpdateView)

    @tag("Port", "port_edit", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Port", "port_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.PortFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Port", "port_edit", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("herring:port_edit", f"/en/herman/ports/edit/{self.instance.pk}/", [self.instance.pk])


class TestSampleCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('herring:sample_new')
        self.expected_template = 'herring/sample_form.html'
        self.user = self.get_and_login_user(is_crud_user=True)

    @tag("Sample", "sample_new", "view")
    def test_view_class(self):
        self.assert_inheritance(views.SampleCreateView, CommonCreateView)

    @tag("Sample", "sample_new", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Sample", "sample_new", "submit")
    def test_submit(self):
        data = FactoryFloor.SampleFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Sample", "sample_new", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("herring:sample_new", f"/en/herman/samples/new/")


class TestSampleDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SampleFactory()
        self.test_url = reverse_lazy('herring:sample_delete', args=[self.instance.pk, ])
        self.expected_template = 'herring/confirm_delete.html'
        self.user = self.get_and_login_user(is_crud_user=True)

    @tag("Sample", "sample_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(views.SampleDeleteView, CommonDeleteView)

    @tag("Sample", "sample_delete", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Sample", "sample_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.SampleFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(models.Sample.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("Sample", "sample_delete", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("herring:sample_delete", f"/en/herman/samples/{self.instance.pk}/delete/", [self.instance.pk])


class TestSampleDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SampleFactory()
        self.test_url = reverse_lazy('herring:sample_detail', args=[self.instance.pk, ])
        self.expected_template = 'herring/sample_detail/main.html'
        self.user = self.get_and_login_user(is_crud_user=True)

    @tag("Sample", "sample_detail", "view")
    def test_view_class(self):
        self.assert_inheritance(views.SampleDetailView, CommonDetailView)

    @tag("Sample", "sample_detail", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Sample", "sample_detail", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("herring:sample_detail", f"/en/herman/samples/{self.instance.pk}/detail/", [self.instance.pk])


class TestSampleListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('herring:sample_list')
        self.expected_template = 'herring/sample_list.html'
        self.user = self.get_and_login_user(is_crud_user=True)

    @tag("Sample", "sample_list", "view")
    def test_view_class(self):
        self.assert_inheritance(views.SampleFilterView, CommonFilterView)

    @tag("Sample", "sample_list", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Sample", "sample_list", "context")
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    @tag("Sample", "sample_list", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("herring:sample_list", f"/en/herman/samples/")


class TestSampleUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SampleFactory()
        self.test_url = reverse_lazy('herring:sample_edit', args=[self.instance.pk, ])
        self.expected_template = 'herring/sample_form.html'
        self.user = self.get_and_login_user(is_crud_user=True)

    @tag("Sample", "sample_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.SampleUpdateView, CommonUpdateView)

    @tag("Sample", "sample_edit", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Sample", "sample_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.SampleFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Sample", "sample_edit", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("herring:sample_edit", f"/en/herman/samples/{self.instance.pk}/edit/", [self.instance.pk])


class TestSampleSearchView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('herring:sample_search')
        self.expected_template = 'herring/form.html'
        self.user = self.get_and_login_user(is_read_only=True)

    @tag("Sample", "sample_search", "view")
    def test_view_class(self):
        self.assert_inheritance(views.SampleSearchFormView, CommonFormView)

    @tag("Sample", "sample_search", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Sample", "sample_search", "submit")
    def test_submit(self):
        data = {}
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Sample", "sample_search", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("herring:sample_search", f"/en/herman/samples/search/")


class TestLengthFrequencyDataEntryView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SampleFactory()
        self.test_url = reverse_lazy('herring:lf', args=[self.instance.pk, ])
        self.expected_template = 'herring/lf.html'
        self.user = self.get_and_login_user(is_crud_user=True)

    @tag("LengthFrequency", "lf", "view")
    def test_view_class(self):
        self.assert_inheritance(views.LengthFrequencyDataEntryView, CommonTemplateView)

    @tag("LengthFrequency", "lf", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("LengthFrequency", "lf", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("herring:lf", f"/en/herman/samples/{self.instance.pk}/length-frequencies/", [self.instance.pk])


class TestIndex(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('herring:index')
        self.expected_template = 'herring/index.html'
        self.user = self.get_and_login_user(is_read_only=True)

    @tag("Index", "index", "view")
    def test_view_class(self):
        self.assert_inheritance(views.IndexView, CommonTemplateView)

    @tag("Index", "index", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Index", "index", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("herring:index", f"/en/herman/")


class TestMoveNextSample(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SampleFactory()
        self.test_url = reverse_lazy('herring:move_sample_next', args=[self.instance.pk, ])
        self.user = self.get_and_login_user(is_read_only=True)

    @tag("Index", "index", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, user=self.user, expected_code=302)


class TestFishDetailDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.FishDetailFactory()
        self.test_url = reverse_lazy('herring:fish_delete', args=[self.instance.pk, ])
        self.expected_template = 'herring/confirm_delete.html'
        self.user = self.get_and_login_user(is_crud_user=True)

    @tag("FishDetail", "fish_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(views.FishDeleteView, CommonDeleteView)

    @tag("FishDetail", "fish_delete", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("FishDetail", "fish_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.FishDetailFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(models.FishDetail.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("FishDetail", "fish_delete", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("herring:fish_delete", f"/en/herman/fish/{self.instance.pk}/delete/", [self.instance.pk])


class TestFishDetailDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.FishDetailFactory()
        self.test_url = reverse_lazy('herring:fish_detail', args=[self.instance.pk, ])
        self.expected_template = 'herring/fish_detail.html'
        self.user = self.get_and_login_user(is_crud_user=True)

    @tag("FishDetail", "fish_detail", "view")
    def test_view_class(self):
        self.assert_inheritance(views.FishDetailView, CommonDetailView)

    @tag("FishDetail", "fish_detail", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("FishDetail", "fish_detail", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("herring:fish_detail", f"/en/herman/fish/{self.instance.pk}/view/", [self.instance.pk])


class TestFishDetailUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.FishDetailFactory()
        self.test_url = reverse_lazy('herring:fish_update', args=[self.instance.pk, ])
        self.expected_template = 'herring/form.html'
        self.user = self.get_and_login_user(is_crud_user=True)

    @tag("FishDetail", "fish_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.FishUpdateView, CommonUpdateView)

    @tag("FishDetail", "fish_edit", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("FishDetail", "fish_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.FishDetailFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("FishDetail", "fish_edit", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("herring:fish_update", f"/en/herman/fish/{self.instance.pk}/edit/", [self.instance.pk])


class TestFishboardTemplateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SampleFactory()
        self.test_url = reverse_lazy('herring:fishboard_test_form', args=[self.instance.id])
        self.expected_template = 'herring/fishboard_test_form.html'
        self.user = self.get_and_login_user(is_crud_user=True)

    @tag("Index", "index", "view")
    def test_view_class(self):
        self.assert_inheritance(views.IndexView, CommonTemplateView)

    @tag("Index", "index", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Index", "index", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("herring:fishboard_test_form", f"/en/herman/lab/samples/{self.instance.pk}/fish-board-test/", [self.instance.pk])


class TestLabSampleConfirmation(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SampleFactory()
        self.test_url = reverse_lazy('herring:lab_sample_confirmation', args=[self.instance.id])
        self.expected_template = 'herring/lab_sample_confirmation.html'
        self.user = self.get_and_login_user(is_crud_user=True)

    @tag("Index", "index", "view")
    def test_view_class(self):
        self.assert_inheritance(views.IndexView, CommonTemplateView)

    @tag("Index", "index", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Index", "index", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("herring:lab_sample_confirmation", f"/en/herman/lab/samples/{self.instance.pk}/lab-sample-confirmation/", [self.instance.pk])


class TestLabSamplePrimer(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SampleFactory()
        self.test_url = reverse_lazy('herring:lab_sample_primer', args=[self.instance.pk, ])
        self.user = self.get_and_login_user(is_crud_user=True)

    @tag("Index", "index", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, user=self.user, expected_code=302)


class TestLabUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.FishDetailFactory()
        self.test_url = reverse_lazy('herring:lab_sample_form', args=[self.instance.pk, ])
        self.expected_template = 'herring/lab_detailing/main.html'
        self.user = self.get_and_login_user(is_crud_user=True)

    @tag("FishDetail", "fish_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.LabSampleUpdateView, CommonUpdateView)

    @tag("FishDetail", "fish_edit", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("FishDetail", "fish_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.FishDetailFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("FishDetail", "fish_edit", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("herring:lab_sample_form", f"/en/herman/lab/fish/{self.instance.pk}/", [self.instance.pk])


class TestLabUpdateViewV2(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.FishDetailFactory()
        self.test_url = reverse_lazy('herring:lab_sample_form_v2', args=[self.instance.pk, ])
        self.expected_template = 'herring/lab_detailing_v2/main.html'
        self.user = self.get_and_login_user(is_crud_user=True)

    @tag("FishDetail", "fish_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.LabSampleUpdateViewV2, CommonDetailView)

    @tag("FishDetail", "fish_edit", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("FishDetail", "fish_edit", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("herring:lab_sample_form_v2", f"/en/herman/lab/fish/v2/{self.instance.pk}/", [self.instance.pk])


class TestOtolithUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.FishDetailFactory()
        self.test_url = reverse_lazy('herring:otolith_form', args=[self.instance.pk, ])
        self.expected_template = 'herring/otolith_detailing_v2/main.html'
        self.user = self.get_and_login_user(is_crud_user=True)

    @tag("FishDetail", "fish_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.OtolithUpdateView, CommonDetailView)

    @tag("FishDetail", "fish_edit", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("FishDetail", "fish_edit", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("herring:otolith_form", f"/en/herman/otolith/fish/{self.instance.pk}/", [self.instance.pk])


class TestProgressReportListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SampleFactory()
        self.test_url = reverse_lazy('herring:progress_report_detail') + f"?species={self.instance.species.id}&year={self.instance.season}"
        self.expected_template = 'herring/progress_list.html'
        self.user = self.get_and_login_user(is_crud_user=True)

    @tag("ProgressReport", "progress_report_detail", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ProgressReportListView, CommonListView)

    @tag("ProgressReport", "progress_report_detail", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("ProgressReport", "progress_report_detail", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("herring:progress_report_detail", f"/en/herman/progress-report/")


class TestCheckUsageListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.FishDetailFactory()
        self.test_url = reverse_lazy('herring:check_usage', args=[])
        self.expected_template = 'herring/check_usage.html'
        self.user = self.get_and_login_user(is_admin=True)

    @tag("CheckUsage", "check_usage", "view")
    def test_view_class(self):
        self.assert_inheritance(views.CheckUsageListView, CommonListView)

    @tag("CheckUsage", "check_usage", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("CheckUsage", "check_usage", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("herring:check_usage", f"/en/herman/check-usage/")
