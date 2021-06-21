from django.test import tag
from django.urls import reverse_lazy
from django.utils.translation import activate
from faker import Factory

from lib.functions.custom_functions import listrify
from shared_models.test.common_tests import CommonTest
from shared_models.views import CommonCreateView, CommonFilterView, CommonUpdateView, CommonDeleteView, CommonDetailView, CommonFormView, \
    CommonPopoutUpdateView, CommonPopoutDeleteView, CommonPopoutCreateView, CommonTemplateView
from . import FactoryFloor
from .. import models
from ..views import biofouling_views, shared_views, ir_views, gc_views

faker = Factory.create()


class TestReportSearchFormView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('grais:reports')
        self.expected_template = 'grais/reports.html'
        self.user = self.get_and_login_user(in_group="grais_admin")

    @tag("ReportSearch", "reports", "view")
    def test_view_class(self):
        self.assert_inheritance(shared_views.ReportSearchFormView, CommonFormView)

    @tag("ReportSearch", "reports", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("ReportSearch", "reports", "submit")
    def test_submit(self):
        data = dict(report=2)
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("ReportSearch", "reports", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:reports", f"/en/grais/reports/search/")


class TestSampleCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.site = FactoryFloor.SiteFactory()
        self.test_url = reverse_lazy('grais:sample_new')
        self.expected_template = 'grais/form.html'
        self.user = self.get_and_login_user(in_group="grais_crud")

    @tag("Sample", "sample_new", "view")
    def test_view_class(self):
        self.assert_inheritance(biofouling_views.SampleCreateView, CommonCreateView)

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
        self.assert_correct_url("grais:sample_new", f"/en/grais/samples/new/")


class TestSampleDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SampleFactory()
        self.test_url = reverse_lazy('grais:sample_delete', args=[self.instance.pk, ])
        self.expected_template = 'grais/confirm_delete.html'
        self.user = self.get_and_login_user(in_group="grais_crud")

    @tag("Sample", "sample_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(biofouling_views.SampleDeleteView, CommonDeleteView)

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
        self.assert_correct_url("grais:sample_delete", f"/en/grais/samples/{self.instance.pk}/delete/", [self.instance.pk])


class TestSampleDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SampleFactory()
        self.test_url = reverse_lazy('grais:sample_detail', args=[self.instance.pk, ])
        self.expected_template = 'grais/biofouling/sample_detail/main.html'
        self.user = self.get_and_login_user(in_group="grais_admin")

    @tag("Sample", "sample_detail", "view")
    def test_view_class(self):
        self.assert_inheritance(biofouling_views.SampleDetailView, CommonDetailView)

    @tag("Sample", "sample_detail", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Sample", "sample_detail", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:sample_detail", f"/en/grais/samples/{self.instance.pk}/view/", [self.instance.pk])


class TestSampleListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('grais:sample_list')
        self.expected_template = 'grais/list.html'
        self.user = self.get_and_login_user(in_group="grais_crud")

    @tag("Sample", "sample_list", "view")
    def test_view_class(self):
        self.assert_inheritance(biofouling_views.SampleListView, CommonFilterView)

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
        self.assert_correct_url("grais:sample_list", f"/en/grais/samples/")


class TestSampleUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SampleFactory()
        self.test_url = reverse_lazy('grais:sample_edit', args=[self.instance.pk, ])
        self.expected_template = 'grais/form.html'
        self.user = self.get_and_login_user(in_group="grais_crud")

    @tag("Sample", "sample_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(biofouling_views.SampleUpdateView, CommonUpdateView)

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
        self.assert_correct_url("grais:sample_edit", f"/en/grais/samples/{self.instance.pk}/edit/", [self.instance.pk])


class TestSpeciesCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('grais:species_new')
        self.expected_template = 'grais/form.html'
        self.user = self.get_and_login_user(in_group="grais_admin")

    @tag("Species", "species_new", "view")
    def test_view_class(self):
        self.assert_inheritance(shared_views.SpeciesCreateView, CommonCreateView)

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
        self.assert_correct_url("grais:species_new", f"/en/grais/species/new/")


class TestSpeciesDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SpeciesFactory()
        self.test_url = reverse_lazy('grais:species_delete', args=[self.instance.pk, ])
        self.expected_template = 'grais/confirm_delete.html'
        self.user = self.get_and_login_user(in_group="grais_admin")

    @tag("Species", "species_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(shared_views.SpeciesDeleteView, CommonDeleteView)

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
        self.assert_correct_url("grais:species_delete", f"/en/grais/species/{self.instance.pk}/delete/", [self.instance.pk])


class TestSpeciesDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SpeciesFactory()
        self.test_url = reverse_lazy('grais:species_detail', args=[self.instance.pk, ])
        self.expected_template = 'grais/biofouling/species_detail.html'
        self.user = self.get_and_login_user(in_group="grais_admin")

    @tag("Species", "species_detail", "view")
    def test_view_class(self):
        self.assert_inheritance(shared_views.SpeciesDetailView, CommonDetailView)

    @tag("Species", "species_detail", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Species", "species_detail", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:species_detail", f"/en/grais/species/{self.instance.pk}/view/", [self.instance.pk])


class TestSpeciesListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('grais:species_list')
        self.expected_template = 'grais/list.html'
        self.user = self.get_and_login_user(in_group="grais_admin")

    @tag("Species", "species_list", "view")
    def test_view_class(self):
        self.assert_inheritance(shared_views.SpeciesListView, CommonFilterView)

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
        self.assert_correct_url("grais:species_list", f"/en/grais/species/")


class TestSpeciesUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SpeciesFactory()
        self.test_url = reverse_lazy('grais:species_edit', args=[self.instance.pk, ])
        self.expected_template = 'grais/form.html'
        self.user = self.get_and_login_user(in_group="grais_admin")

    @tag("Species", "species_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(shared_views.SpeciesUpdateView, CommonUpdateView)

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
        self.assert_correct_url("grais:species_edit", f"/en/grais/species/{self.instance.pk}/edit/", [self.instance.pk])


class TestStationCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.site = FactoryFloor.SiteFactory()
        self.test_url = reverse_lazy('grais:station_new')
        self.expected_template = 'grais/form.html'
        self.user = self.get_and_login_user(in_group="grais_admin")

    @tag("Station", "station_new", "view")
    def test_view_class(self):
        self.assert_inheritance(biofouling_views.StationCreateView, CommonCreateView)

    @tag("Station", "station_new", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Station", "station_new", "submit")
    def test_submit(self):
        data = FactoryFloor.StationFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Station", "station_new", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:station_new", f"/en/grais/stations/new/")


class TestStationDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.StationFactory()
        self.test_url = reverse_lazy('grais:station_delete', args=[self.instance.pk, ])
        self.expected_template = 'grais/confirm_delete.html'
        self.user = self.get_and_login_user(in_group="grais_admin")

    @tag("Station", "station_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(biofouling_views.StationDeleteView, CommonDeleteView)

    @tag("Station", "station_delete", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Station", "station_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.StationFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(models.Station.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("Station", "station_delete", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:station_delete", f"/en/grais/stations/{self.instance.pk}/delete/", [self.instance.pk])


class TestStationDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.StationFactory()
        self.test_url = reverse_lazy('grais:station_detail', args=[self.instance.pk, ])
        self.expected_template = 'grais/biofouling/station_detail.html'
        self.user = self.get_and_login_user(in_group="grais_admin")

    @tag("Station", "station_detail", "view")
    def test_view_class(self):
        self.assert_inheritance(biofouling_views.StationDetailView, CommonDetailView)

    @tag("Station", "station_detail", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Station", "station_detail", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:station_detail", f"/en/grais/stations/{self.instance.pk}/view/", [self.instance.pk])


class TestStationListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('grais:station_list')
        self.expected_template = 'grais/list.html'
        self.user = self.get_and_login_user(in_group="grais_access")

    @tag("Station", "station_list", "view")
    def test_view_class(self):
        self.assert_inheritance(biofouling_views.StationListView, CommonFilterView)

    @tag("Station", "station_list", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Station", "station_list", "context")
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    @tag("Station", "station_list", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:station_list", f"/en/grais/stations/")


class TestStationUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.StationFactory()
        self.test_url = reverse_lazy('grais:station_edit', args=[self.instance.pk, ])
        self.expected_template = 'grais/form.html'
        self.user = self.get_and_login_user(in_group="grais_admin")

    @tag("Station", "station_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(biofouling_views.StationUpdateView, CommonUpdateView)

    @tag("Station", "station_edit", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Station", "station_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.StationFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Station", "station_edit", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:station_edit", f"/en/grais/stations/{self.instance.pk}/edit/", [self.instance.pk])


class TestSampleNoteCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.sample = FactoryFloor.SampleFactory()
        self.test_url = reverse_lazy('grais:sample_note_new', args=[self.sample.id])
        self.expected_template = 'shared_models/generic_popout_form.html'
        self.user = self.get_and_login_user(in_group="grais_crud")

    @tag("SampleNote", "sample_note_new", "view")
    def test_view_class(self):
        self.assert_inheritance(biofouling_views.SampleNoteCreateView, CommonPopoutCreateView)

    @tag("SampleNote", "sample_note_new", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("SampleNote", "sample_note_new", "submit")
    def test_submit(self):
        data = FactoryFloor.SampleNoteFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("SampleNote", "sample_note_new", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:sample_note_new", f"/en/grais/samples/{self.sample.pk}/new-note/", test_url_args=[self.sample.id])


class TestSampleNoteDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SampleNoteFactory()
        self.test_url = reverse_lazy('grais:sample_note_delete', args=[self.instance.pk, ])
        self.expected_template = 'shared_models/generic_popout_confirm_delete.html'
        self.user = self.get_and_login_user(in_group="grais_crud")

    @tag("SampleNote", "sample_note_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(biofouling_views.SampleNoteDeleteView, CommonPopoutDeleteView)

    @tag("SampleNote", "sample_note_delete", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("SampleNote", "sample_note_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.SampleNoteFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(models.SampleNote.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("SampleNote", "sample_note_delete", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:sample_note_delete", f"/en/grais/sample-notes/{self.instance.pk}/delete/", [self.instance.pk])


class TestSampleNoteUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SampleNoteFactory()
        self.test_url = reverse_lazy('grais:sample_note_edit', args=[self.instance.pk, ])
        self.expected_template = 'shared_models/generic_popout_form.html'
        self.user = self.get_and_login_user(in_group="grais_crud")

    @tag("SampleNote", "sample_note_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(biofouling_views.SampleNoteUpdateView, CommonPopoutUpdateView)

    @tag("SampleNote", "sample_note_edit", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("SampleNote", "sample_note_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.SampleNoteFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("SampleNote", "sample_note_edit", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:sample_note_edit", f"/en/grais/sample-notes/{self.instance.pk}/edit/", [self.instance.pk])


class TestProbeMeasurementCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.sample = FactoryFloor.SampleFactory()
        self.test_url = reverse_lazy('grais:measurement_new', args=[self.sample.id])
        self.expected_template = 'shared_models/generic_popout_form.html'
        self.user = self.get_and_login_user(in_group="grais_crud")

    @tag("ProbeMeasurement", "measurement_new", "view")
    def test_view_class(self):
        self.assert_inheritance(biofouling_views.ProbeMeasurementCreateView, CommonPopoutCreateView)

    @tag("ProbeMeasurement", "measurement_new", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("ProbeMeasurement", "measurement_new", "submit")
    def test_submit(self):
        data = FactoryFloor.ProbeMeasurementFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("ProbeMeasurement", "measurement_new", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:measurement_new", f"/en/grais/samples/{self.sample.pk}/new-measurement/", test_url_args=[self.sample.id])


class TestProbeMeasurementDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ProbeMeasurementFactory()
        self.test_url = reverse_lazy('grais:measurement_delete', args=[self.instance.pk, ])
        self.expected_template = 'shared_models/generic_popout_confirm_delete.html'
        self.user = self.get_and_login_user(in_group="grais_crud")

    @tag("ProbeMeasurement", "measurement_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(biofouling_views.ProbeMeasurementDeleteView, CommonPopoutDeleteView)

    @tag("ProbeMeasurement", "measurement_delete", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("ProbeMeasurement", "measurement_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.ProbeMeasurementFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(models.ProbeMeasurement.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("ProbeMeasurement", "measurement_delete", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:measurement_delete", f"/en/grais/measurements/{self.instance.pk}/delete/", [self.instance.pk])


class TestProbeMeasurementUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ProbeMeasurementFactory()
        self.test_url = reverse_lazy('grais:measurement_edit', args=[self.instance.pk, ])
        self.expected_template = 'shared_models/generic_popout_form.html'
        self.user = self.get_and_login_user(in_group="grais_crud")

    @tag("ProbeMeasurement", "measurement_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(biofouling_views.ProbeMeasurementUpdateView, CommonPopoutUpdateView)

    @tag("ProbeMeasurement", "measurement_edit", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("ProbeMeasurement", "measurement_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.ProbeMeasurementFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("ProbeMeasurement", "measurement_edit", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:measurement_edit", f"/en/grais/measurements/{self.instance.pk}/edit/", [self.instance.pk])


class TestSpeciesObservationTemplateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.sample = FactoryFloor.SampleFactory()
        self.line = FactoryFloor.LineFactory()
        self.surface = FactoryFloor.SurfaceFactory()

        self.test_url1 = reverse_lazy('grais:species_observations', args=['samples', self.sample.id])
        self.test_url2 = reverse_lazy('grais:species_observations', args=['lines', self.line.id])
        self.test_url3 = reverse_lazy('grais:species_observations', args=['surfaces', self.surface.id])
        self.expected_template = 'grais/biofouling/species_observations.html'
        self.user = self.get_and_login_user(in_group="grais_crud")

    @tag("ReportSearch", "reports", "view")
    def test_view_class(self):
        self.assert_inheritance(biofouling_views.SpeciesObservationTemplateView, CommonDetailView)

    @tag("ReportSearch", "reports", "access")
    def test_view(self):
        self.assert_good_response(self.test_url1)
        self.assert_good_response(self.test_url2)
        self.assert_good_response(self.test_url3)
        self.assert_non_public_view(test_url=self.test_url1, expected_template=self.expected_template, user=self.user)
        self.assert_non_public_view(test_url=self.test_url2, expected_template=self.expected_template, user=self.user)
        self.assert_non_public_view(test_url=self.test_url3, expected_template=self.expected_template, user=self.user)

    @tag("ReportSearch", "reports", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:species_observations", f"/en/grais/samples/{self.sample.id}/observations/", test_url_args=["samples", self.sample.id])
        self.assert_correct_url("grais:species_observations", f"/en/grais/lines/{self.line.id}/observations/", test_url_args=["lines", self.line.id])
        self.assert_correct_url("grais:species_observations", f"/en/grais/surfaces/{self.surface.id}/observations/",
                                test_url_args=["surfaces", self.surface.id])


class TestIndexTemplateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('grais:index')
        self.expected_template = 'grais/index.html'
        self.user = self.get_and_login_user(in_group="grais_access")

    @tag("ReportSearch", "reports", "view")
    def test_view_class(self):
        self.assert_inheritance(shared_views.IndexView, CommonTemplateView)

    @tag("ReportSearch", "reports", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("ReportSearch", "reports", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:index", f"/en/grais/")


class TestIncidentalReportCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('grais:ir_new')
        self.expected_template = 'grais/form.html'
        self.user = self.get_and_login_user(in_group="grais_admin")

    @tag("IncidentalReport", "ir_new", "view")
    def test_view_class(self):
        self.assert_inheritance(ir_views.ReportCreateView, CommonCreateView)

    @tag("IncidentalReport", "ir_new", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("IncidentalReport", "ir_new", "submit")
    def test_submit(self):
        data = FactoryFloor.IncidentalReportFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("IncidentalReport", "ir_new", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:ir_new", f"/en/grais/incidental-reports/new/")


class TestIncidentalReportDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.IncidentalReportFactory()
        self.test_url = reverse_lazy('grais:ir_delete', args=[self.instance.pk, ])
        self.expected_template = 'grais/confirm_delete.html'
        self.user = self.get_and_login_user(in_group="grais_admin")

    @tag("IncidentalReport", "ir_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(ir_views.ReportDeleteView, CommonDeleteView)

    @tag("IncidentalReport", "ir_delete", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("IncidentalReport", "ir_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.IncidentalReportFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(models.IncidentalReport.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("IncidentalReport", "ir_delete", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:ir_delete", f"/en/grais/incidental-reports/{self.instance.pk}/delete/", [self.instance.pk])


class TestIncidentalReportDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.IncidentalReportFactory()
        self.test_url = reverse_lazy('grais:ir_detail', args=[self.instance.pk, ])
        self.expected_template = 'grais/incidental_reports/report_detail.html'
        self.user = self.get_and_login_user(in_group="grais_admin")

    @tag("IncidentalReport", "ir_detail", "view")
    def test_view_class(self):
        self.assert_inheritance(ir_views.ReportDetailView, CommonDetailView)

    @tag("IncidentalReport", "ir_detail", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("IncidentalReport", "ir_detail", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:ir_detail", f"/en/grais/incidental-reports/{self.instance.pk}/view/", [self.instance.pk])


class TestIncidentalReportListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('grais:ir_list')
        self.expected_template = 'grais/list.html'
        self.user = self.get_and_login_user(in_group="grais_access")

    @tag("IncidentalReport", "ir_list", "view")
    def test_view_class(self):
        self.assert_inheritance(ir_views.ReportListView, CommonFilterView)

    @tag("IncidentalReport", "ir_list", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("IncidentalReport", "ir_list", "context")
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    @tag("IncidentalReport", "ir_list", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:ir_list", f"/en/grais/incidental-reports/")


class TestIncidentalReportUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.IncidentalReportFactory()
        self.test_url = reverse_lazy('grais:ir_edit', args=[self.instance.pk, ])
        self.expected_template = 'grais/form.html'
        self.user = self.get_and_login_user(in_group="grais_admin")

    @tag("IncidentalReport", "ir_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(ir_views.ReportUpdateView, CommonUpdateView)

    @tag("IncidentalReport", "ir_edit", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("IncidentalReport", "ir_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.IncidentalReportFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("IncidentalReport", "ir_edit", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:ir_edit", f"/en/grais/incidental-reports/{self.instance.pk}/edit/", [self.instance.pk])


class TestFollowUpCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.ir = FactoryFloor.IncidentalReportFactory()
        self.test_url = reverse_lazy('grais:followup_new', args=[self.ir.id])
        self.expected_template = 'shared_models/generic_popout_form.html'
        self.user = self.get_and_login_user(in_group="grais_crud")

    @tag("FollowUp", "follow_up_new", "view")
    def test_view_class(self):
        self.assert_inheritance(ir_views.FollowUpCreateView, CommonPopoutCreateView)

    @tag("FollowUp", "follow_up_new", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("FollowUp", "follow_up_new", "submit")
    def test_submit(self):
        data = FactoryFloor.FollowUpFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("FollowUp", "follow_up_new", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:followup_new", f"/en/grais/incidental-reports/{self.ir.pk}/new-followup/", test_url_args=[self.ir.id])


class TestFollowUpDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.FollowUpFactory()
        self.test_url = reverse_lazy('grais:followup_delete', args=[self.instance.pk, ])
        self.expected_template = 'shared_models/generic_popout_confirm_delete.html'
        self.user = self.get_and_login_user(in_group="grais_crud")

    @tag("FollowUp", "follow_up_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(ir_views.FollowUpDeleteView, CommonPopoutDeleteView)

    @tag("FollowUp", "follow_up_delete", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("FollowUp", "follow_up_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.FollowUpFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(models.FollowUp.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("FollowUp", "follow_up_delete", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:followup_delete", f"/en/grais/follow-up/{self.instance.pk}/delete/", [self.instance.pk])


class TestFollowUpUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.FollowUpFactory()
        self.test_url = reverse_lazy('grais:followup_edit', args=[self.instance.pk, ])
        self.expected_template = 'shared_models/generic_popout_form.html'
        self.user = self.get_and_login_user(in_group="grais_crud")

    @tag("FollowUp", "follow_up_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(ir_views.FollowUpUpdateView, CommonPopoutUpdateView)

    @tag("FollowUp", "follow_up_edit", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("FollowUp", "follow_up_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.FollowUpFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("FollowUp", "follow_up_edit", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:followup_edit", f"/en/grais/follow-up/{self.instance.pk}/edit/", [self.instance.pk])


class TestLineCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.sample = FactoryFloor.SampleFactory()
        self.test_url = reverse_lazy('grais:line_new', args=[self.sample.id])
        self.expected_template = 'grais/form.html'
        self.user = self.get_and_login_user(in_group="grais_crud")

    @tag("Line", "line_new", "view")
    def test_view_class(self):
        self.assert_inheritance(biofouling_views.LineCreateView, CommonCreateView)

    @tag("Line", "line_new", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Line", "line_new", "submit")
    def test_submit(self):
        data = FactoryFloor.LineFactory.get_valid_data()
        data['number_petris'] = 3
        data['number_plates'] = 3
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Line", "line_new", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:line_new", f"/en/grais/samples/{self.sample.id}/new-line/", test_url_args=[self.sample.id])


class TestLineDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.LineFactory()
        self.test_url = reverse_lazy('grais:line_delete', args=[self.instance.pk, ])
        self.expected_template = 'grais/confirm_delete.html'
        self.user = self.get_and_login_user(in_group="grais_crud")

    @tag("Line", "line_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(biofouling_views.LineDeleteView, CommonDeleteView)

    @tag("Line", "line_delete", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Line", "line_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.LineFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(models.Line.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("Line", "line_delete", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:line_delete", f"/en/grais/lines/{self.instance.pk}/delete/", [self.instance.pk])


class TestLineDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.LineFactory()
        self.test_url = reverse_lazy('grais:line_detail', args=[self.instance.pk, ])
        self.expected_template = 'grais/biofouling/line_detail/main.html'
        self.user = self.get_and_login_user(in_group="grais_admin")

    @tag("Line", "line_detail", "view")
    def test_view_class(self):
        self.assert_inheritance(biofouling_views.LineDetailView, CommonDetailView)

    @tag("Line", "line_detail", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Line", "line_detail", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:line_detail", f"/en/grais/lines/{self.instance.pk}/view/", [self.instance.pk])


class TestLineUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.LineFactory()
        self.test_url = reverse_lazy('grais:line_edit', args=[self.instance.pk, ])
        self.expected_template = 'grais/form.html'
        self.user = self.get_and_login_user(in_group="grais_crud")

    @tag("Line", "line_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(biofouling_views.LineUpdateView, CommonUpdateView)

    @tag("Line", "line_edit", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Line", "line_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.LineFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Line", "line_edit", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:line_edit", f"/en/grais/lines/{self.instance.pk}/edit/", [self.instance.pk])


class TestSurfaceCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.line = FactoryFloor.LineFactory()
        self.test_url = reverse_lazy('grais:surface_new', args=[self.line.id])
        self.expected_template = 'grais/form.html'
        self.user = self.get_and_login_user(in_group="grais_crud")

    @tag("Surface", "surface_new", "view")
    def test_view_class(self):
        self.assert_inheritance(biofouling_views.SurfaceCreateView, CommonCreateView)

    @tag("Surface", "surface_new", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Surface", "surface_new", "submit")
    def test_submit(self):
        data = FactoryFloor.SurfaceFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Surface", "surface_new", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:surface_new", f"/en/grais/lines/{self.line.id}/new-surface/", test_url_args=[self.line.id])


class TestSurfaceDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SurfaceFactory()
        self.test_url = reverse_lazy('grais:surface_delete', args=[self.instance.pk, ])
        self.expected_template = 'grais/confirm_delete.html'
        self.user = self.get_and_login_user(in_group="grais_crud")

    @tag("Surface", "surface_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(biofouling_views.SurfaceDeleteView, CommonDeleteView)

    @tag("Surface", "surface_delete", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Surface", "surface_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.SurfaceFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(models.Surface.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("Surface", "surface_delete", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:surface_delete", f"/en/grais/surfaces/{self.instance.pk}/delete/", [self.instance.pk])


class TestSurfaceDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SurfaceFactory()
        self.test_url = reverse_lazy('grais:surface_detail', args=[self.instance.pk, ])
        self.expected_template = 'grais/biofouling/surface_detail/main.html'
        self.user = self.get_and_login_user(in_group="grais_admin")

    @tag("Surface", "surface_detail", "view")
    def test_view_class(self):
        self.assert_inheritance(biofouling_views.SurfaceDetailView, CommonDetailView)

    @tag("Surface", "surface_detail", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Surface", "surface_detail", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:surface_detail", f"/en/grais/surfaces/{self.instance.pk}/view/", [self.instance.pk])


class TestSurfaceUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SurfaceFactory()
        self.test_url = reverse_lazy('grais:surface_edit', args=[self.instance.pk, ])
        self.expected_template = 'grais/form.html'
        self.user = self.get_and_login_user(in_group="grais_crud")

    @tag("Surface", "surface_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(biofouling_views.SurfaceUpdateView, CommonUpdateView)

    @tag("Surface", "surface_edit", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Surface", "surface_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.SurfaceFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Surface", "surface_edit", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:surface_edit", f"/en/grais/surfaces/{self.instance.pk}/edit/", [self.instance.pk])


class TestEstuaryCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.site = FactoryFloor.SiteFactory()
        self.test_url = reverse_lazy('grais:estuary_new')
        self.expected_template = 'grais/form.html'
        self.user = self.get_and_login_user(in_group="grais_crud")

    @tag("Estuary", "estuary_new", "view")
    def test_view_class(self):
        self.assert_inheritance(gc_views.EstuaryCreateView, CommonCreateView)

    @tag("Estuary", "estuary_new", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Estuary", "estuary_new", "submit")
    def test_submit(self):
        data = FactoryFloor.EstuaryFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Estuary", "estuary_new", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:estuary_new", f"/en/grais/estuaries/new/")


class TestEstuaryDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.EstuaryFactory()
        self.test_url = reverse_lazy('grais:estuary_delete', args=[self.instance.pk, ])
        self.expected_template = 'grais/confirm_delete.html'
        self.user = self.get_and_login_user(in_group="grais_crud")

    @tag("Estuary", "estuary_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(gc_views.EstuaryDeleteView, CommonDeleteView)

    @tag("Estuary", "estuary_delete", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Estuary", "estuary_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.EstuaryFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(models.Estuary.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("Estuary", "estuary_delete", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:estuary_delete", f"/en/grais/estuaries/{self.instance.pk}/delete/", [self.instance.pk])


class TestEstuaryDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.EstuaryFactory()
        self.test_url = reverse_lazy('grais:estuary_detail', args=[self.instance.pk, ])
        self.expected_template = 'grais/green_crab/estuary_detail.html'
        self.user = self.get_and_login_user(in_group="grais_admin")

    @tag("Estuary", "estuary_detail", "view")
    def test_view_class(self):
        self.assert_inheritance(gc_views.EstuaryDetailView, CommonDetailView)

    @tag("Estuary", "estuary_detail", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Estuary", "estuary_detail", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:estuary_detail", f"/en/grais/estuaries/{self.instance.pk}/view/", [self.instance.pk])


class TestEstuaryListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('grais:estuary_list')
        self.expected_template = 'grais/list.html'
        self.user = self.get_and_login_user(in_group="grais_crud")

    @tag("Estuary", "estuary_list", "view")
    def test_view_class(self):
        self.assert_inheritance(gc_views.EstuaryListView, CommonFilterView)

    @tag("Estuary", "estuary_list", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Estuary", "estuary_list", "context")
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    @tag("Estuary", "estuary_list", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:estuary_list", f"/en/grais/estuaries/")


class TestEstuaryUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.EstuaryFactory()
        self.test_url = reverse_lazy('grais:estuary_edit', args=[self.instance.pk, ])
        self.expected_template = 'grais/form.html'
        self.user = self.get_and_login_user(in_group="grais_crud")

    @tag("Estuary", "estuary_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(gc_views.EstuaryUpdateView, CommonUpdateView)

    @tag("Estuary", "estuary_edit", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Estuary", "estuary_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.EstuaryFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Estuary", "estuary_edit", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:estuary_edit", f"/en/grais/estuaries/{self.instance.pk}/edit/", [self.instance.pk])


class TestSiteCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.estuary = FactoryFloor.EstuaryFactory()
        self.test_url = reverse_lazy('grais:site_new', args=[self.estuary.id])
        self.expected_template = 'grais/form.html'
        self.user = self.get_and_login_user(in_group="grais_crud")

    @tag("Site", "site_new", "view")
    def test_view_class(self):
        self.assert_inheritance(gc_views.SiteCreateView, CommonCreateView)

    @tag("Site", "site_new", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Site", "site_new", "submit")
    def test_submit(self):
        data = FactoryFloor.SiteFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Site", "site_new", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:site_new", f"/en/grais/estuaries/{self.estuary.id}/new-site/", test_url_args=[self.estuary.id])


class TestSiteDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SiteFactory()
        self.test_url = reverse_lazy('grais:site_delete', args=[self.instance.pk, ])
        self.expected_template = 'grais/confirm_delete.html'
        self.user = self.get_and_login_user(in_group="grais_crud")

    @tag("Site", "site_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(gc_views.SiteDeleteView, CommonDeleteView)

    @tag("Site", "site_delete", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Site", "site_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.SiteFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(models.Site.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("Site", "site_delete", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:site_delete", f"/en/grais/sites/{self.instance.pk}/delete/", [self.instance.pk])


class TestSiteDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SiteFactory()
        self.test_url = reverse_lazy('grais:site_detail', args=[self.instance.pk, ])
        self.expected_template = 'grais/green_crab/site_detail.html'
        self.user = self.get_and_login_user(in_group="grais_admin")

    @tag("Site", "site_detail", "view")
    def test_view_class(self):
        self.assert_inheritance(gc_views.SiteDetailView, CommonDetailView)

    @tag("Site", "site_detail", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Site", "site_detail", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:site_detail", f"/en/grais/sites/{self.instance.pk}/view/", [self.instance.pk])


class TestSiteUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SiteFactory()
        self.test_url = reverse_lazy('grais:site_edit', args=[self.instance.pk, ])
        self.expected_template = 'grais/form.html'
        self.user = self.get_and_login_user(in_group="grais_crud")

    @tag("Site", "site_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(gc_views.SiteUpdateView, CommonUpdateView)

    @tag("Site", "site_edit", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Site", "site_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.SiteFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Site", "site_edit", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:site_edit", f"/en/grais/sites/{self.instance.pk}/edit/", [self.instance.pk])


class TestGCSampleCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('grais:gcsample_new')
        self.expected_template = 'grais/form.html'
        self.user = self.get_and_login_user(in_group="grais_crud")

    @tag("GCSample", "gcsample_new", "view")
    def test_view_class(self):
        self.assert_inheritance(gc_views.GCSampleCreateView, CommonCreateView)

    @tag("GCSample", "gcsample_new", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("GCSample", "gcsample_new", "submit")
    def test_submit(self):
        data = FactoryFloor.GCSampleFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("GCSample", "gcsample_new", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:gcsample_new", f"/en/grais/green-crab-samples/new/")


class TestGCSampleDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.GCSampleFactory()
        self.test_url = reverse_lazy('grais:gcsample_delete', args=[self.instance.pk, ])
        self.expected_template = 'grais/confirm_delete.html'
        self.user = self.get_and_login_user(in_group="grais_crud")

    @tag("GCSample", "gcsample_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(gc_views.GCSampleDeleteView, CommonDeleteView)

    @tag("GCSample", "gcsample_delete", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("GCSample", "gcsample_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.GCSampleFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(models.GCSample.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("GCSample", "gcsample_delete", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:gcsample_delete", f"/en/grais/green-crab-samples/{self.instance.pk}/delete/", [self.instance.pk])


class TestGCSampleDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.GCSampleFactory()
        self.test_url = reverse_lazy('grais:gcsample_detail', args=[self.instance.pk, ])
        self.expected_template = 'grais/green_crab/sample_detail/main.html'
        self.user = self.get_and_login_user(in_group="grais_admin")

    @tag("GCSample", "gcsample_detail", "view")
    def test_view_class(self):
        self.assert_inheritance(gc_views.GCSampleDetailView, CommonDetailView)

    @tag("GCSample", "gcsample_detail", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("GCSample", "gcsample_detail", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:gcsample_detail", f"/en/grais/green-crab-samples/{self.instance.pk}/view/", [self.instance.pk])


class TestGCSampleListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('grais:gcsample_list')
        self.expected_template = 'grais/list.html'
        self.user = self.get_and_login_user(in_group="grais_crud")

    @tag("GCSample", "gcsample_list", "view")
    def test_view_class(self):
        self.assert_inheritance(gc_views.GCSampleListView, CommonFilterView)

    @tag("GCSample", "gcsample_list", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("GCSample", "gcsample_list", "context")
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    @tag("GCSample", "gcsample_list", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:gcsample_list", f"/en/grais/green-crab-samples/")


class TestGCSampleUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.GCSampleFactory()
        self.test_url = reverse_lazy('grais:gcsample_edit', args=[self.instance.pk, ])
        self.expected_template = 'grais/form.html'
        self.user = self.get_and_login_user(in_group="grais_crud")

    @tag("GCSample", "gcsample_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(gc_views.GCSampleUpdateView, CommonUpdateView)

    @tag("GCSample", "gcsample_edit", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("GCSample", "gcsample_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.GCSampleFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("GCSample", "gcsample_edit", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:gcsample_edit", f"/en/grais/green-crab-samples/{self.instance.pk}/edit/", [self.instance.pk])


class TestGCProbeMeasurementCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.sample = FactoryFloor.SampleFactory()
        self.test_url = reverse_lazy('grais:gcmeasurement_new', args=[self.sample.id])
        self.expected_template = 'shared_models/generic_popout_form.html'
        self.user = self.get_and_login_user(in_group="grais_crud")

    @tag("GCProbeMeasurement", "gcmeasurement_new", "view")
    def test_view_class(self):
        self.assert_inheritance(gc_views.GCProbeMeasurementCreateView, CommonPopoutCreateView)

    @tag("GCProbeMeasurement", "gcmeasurement_new", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("GCProbeMeasurement", "gcmeasurement_new", "submit")
    def test_submit(self):
        data = FactoryFloor.GCProbeMeasurementFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("GCProbeMeasurement", "gcmeasurement_new", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:gcmeasurement_new", f"/en/grais/green-crab-samples/{self.sample.pk}/new-measurement/", test_url_args=[self.sample.id])


class TestGCProbeMeasurementDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.GCProbeMeasurementFactory()
        self.test_url = reverse_lazy('grais:gcmeasurement_delete', args=[self.instance.pk, ])
        self.expected_template = 'shared_models/generic_popout_confirm_delete.html'
        self.user = self.get_and_login_user(in_group="grais_crud")

    @tag("GCProbeMeasurement", "gcmeasurement_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(gc_views.GCProbeMeasurementDeleteView, CommonPopoutDeleteView)

    @tag("GCProbeMeasurement", "gcmeasurement_delete", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("GCProbeMeasurement", "gcmeasurement_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.GCProbeMeasurementFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(models.GCProbeMeasurement.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("GCProbeMeasurement", "gcmeasurement_delete", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:gcmeasurement_delete", f"/en/grais/green-crab-measurements/{self.instance.pk}/delete/", [self.instance.pk])


class TestGCProbeMeasurementUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.GCProbeMeasurementFactory()
        self.test_url = reverse_lazy('grais:gcmeasurement_edit', args=[self.instance.pk, ])
        self.expected_template = 'shared_models/generic_popout_form.html'
        self.user = self.get_and_login_user(in_group="grais_crud")

    @tag("GCProbeMeasurement", "gcmeasurement_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(gc_views.GCProbeMeasurementUpdateView, CommonPopoutUpdateView)

    @tag("GCProbeMeasurement", "gcmeasurement_edit", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("GCProbeMeasurement", "gcmeasurement_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.GCProbeMeasurementFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("GCProbeMeasurement", "gcmeasurement_edit", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:gcmeasurement_edit", f"/en/grais/green-crab-measurements/{self.instance.pk}/edit/", [self.instance.pk])


class TestTrapCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.sample = FactoryFloor.GCSampleFactory()
        self.test_url = reverse_lazy('grais:trap_new', args=[self.sample.id])
        self.expected_template = 'grais/form.html'
        self.user = self.get_and_login_user(in_group="grais_crud")

    @tag("Trap", "trap_new", "view")
    def test_view_class(self):
        self.assert_inheritance(gc_views.TrapCreateView, CommonCreateView)

    @tag("Trap", "trap_new", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Trap", "trap_new", "submit")
    def test_submit(self):
        data = FactoryFloor.TrapFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Trap", "trap_new", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:trap_new", f"/en/grais/green-crab-samples/{self.sample.id}/new-trap/", test_url_args=[self.sample.id])


class TestTrapDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.TrapFactory()
        self.test_url = reverse_lazy('grais:trap_delete', args=[self.instance.pk, ])
        self.expected_template = 'grais/confirm_delete.html'
        self.user = self.get_and_login_user(in_group="grais_crud")

    @tag("Trap", "trap_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(gc_views.TrapDeleteView, CommonDeleteView)

    @tag("Trap", "trap_delete", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Trap", "trap_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.TrapFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(models.Trap.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("Trap", "trap_delete", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:trap_delete", f"/en/grais/traps/{self.instance.pk}/delete/", [self.instance.pk])


class TestTrapDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.TrapFactory()
        self.test_url = reverse_lazy('grais:trap_detail', args=[self.instance.pk, ])
        self.expected_template = 'grais/green_crab/trap_detail/main.html'
        self.user = self.get_and_login_user(in_group="grais_admin")

    @tag("Trap", "trap_detail", "view")
    def test_view_class(self):
        self.assert_inheritance(gc_views.TrapDetailView, CommonDetailView)

    @tag("Trap", "trap_detail", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Trap", "trap_detail", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:trap_detail", f"/en/grais/traps/{self.instance.pk}/view/", [self.instance.pk])


class TestTrapUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.TrapFactory()
        self.test_url = reverse_lazy('grais:trap_edit', args=[self.instance.pk, ])
        self.expected_template = 'grais/form.html'
        self.user = self.get_and_login_user(in_group="grais_crud")

    @tag("Trap", "trap_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(gc_views.TrapUpdateView, CommonUpdateView)

    @tag("Trap", "trap_edit", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Trap", "trap_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.TrapFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Trap", "trap_edit", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:trap_edit", f"/en/grais/traps/{self.instance.pk}/edit/", [self.instance.pk])


class TestCatchObservationTemplateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.trap = FactoryFloor.TrapFactory()

        self.test_url1 = reverse_lazy('grais:catch_observations', args=[self.trap.id, 'crab'])
        self.test_url2 = reverse_lazy('grais:catch_observations', args=[self.trap.id, 'bycatch'])
        self.expected_template = 'grais/green_crab/species_observations.html'
        self.user = self.get_and_login_user(in_group="grais_crud")

    @tag("CatchObservation", "reports", "view")
    def test_view_class(self):
        self.assert_inheritance(biofouling_views.SpeciesObservationTemplateView, CommonDetailView)

    @tag("CatchObservation", "reports", "access")
    def test_view(self):
        self.assert_good_response(self.test_url1)
        self.assert_good_response(self.test_url2)
        self.assert_non_public_view(test_url=self.test_url1, expected_template=self.expected_template, user=self.user)
        self.assert_non_public_view(test_url=self.test_url2, expected_template=self.expected_template, user=self.user)

    @tag("CatchObservation", "reports", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("grais:catch_observations", f"/en/grais/traps/{self.trap.id}/crab-observations/", test_url_args=[self.trap.id, 'crab'])
        self.assert_correct_url("grais:catch_observations", f"/en/grais/traps/{self.trap.id}/bycatch-observations/", test_url_args=[self.trap.id, 'bycatch'])


class TestReportViews(CommonTest):
    def setUp(self):
        super().setUp()
        activate('en')
        self.species = FactoryFloor.SpeciesFactory()
        for id in [24, 48, 23, 25, 47, 59, 26, 55]:
            FactoryFloor.SpeciesFactory(id=id)
        for i in range(1, 19):
            FactoryFloor.SampleFactory()
        self.test_urls = [
            reverse_lazy('grais:spp_sample_xlsx', args=[listrify([self.species.id]), "None"]),
            reverse_lazy('grais:biofouling_pa_xlsx') + "?year=2019",
            reverse_lazy('grais:biofouling_pa_xlsx') + "?year=None",
            reverse_lazy('grais:od1_report'),
            reverse_lazy('grais:od1_report', args=[2019]),
            reverse_lazy('grais:od1_dictionary'),
            reverse_lazy('grais:od1_wms', args=[2019, 1]),
            reverse_lazy('grais:gc_cpue_report', args=[2019]),
            reverse_lazy('grais:gc_envr_report', args=[2019]),
            reverse_lazy('grais:gc_site_report'),
        ]

    @tag("grais", 'reports')
    def test_view(self):
        for url in self.test_urls:
            self.assert_good_response(url)

