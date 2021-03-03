from django.test import tag
from django.urls import reverse_lazy
from django.utils.translation import activate
from faker import Faker

from shared_models.test.SharedModelsFactoryFloor import UserFactory
from shared_models.views import CommonListView, CommonUpdateView, CommonCreateView, CommonFilterView, CommonFormView, CommonTemplateView, CommonDetailView, \
    CommonDeleteView
from travel.test import FactoryFloor
from travel.test.common_tests import CommonTravelTest as CommonTest
from .. import views, models, utils

faker = Faker()


class TestDefaultReviewerListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.DefaultReviewerFactory()
        self.test_url = reverse_lazy('travel:default_reviewer_list')
        self.expected_template = 'travel/default_reviewer/default_reviewer_list.html'
        self.user = self.get_and_login_user(in_group="travel_adm_admin")

    @tag("DefaultReviewer", "default_reviewer_list", "view")
    def test_view_class(self):
        self.assert_inheritance(views.DefaultReviewerListView, CommonListView)

    @tag("DefaultReviewer", "default_reviewer_list", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("DefaultReviewer", "default_reviewer_list", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("travel:default_reviewer_list", f"/en/travel-plans/settings/default-reviewers/")


class TestDefaultReviewerCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.DefaultReviewerFactory()
        self.test_url = reverse_lazy('travel:default_reviewer_new')
        self.expected_template = 'travel/default_reviewer/default_reviewer_form.html'
        self.user = self.get_and_login_user(in_group="travel_adm_admin")

    @tag("DefaultReviewer", "default_reviewer_new", "view")
    def test_view_class(self):
        self.assert_inheritance(views.DefaultReviewerCreateView, CommonCreateView)

    @tag("DefaultReviewer", "default_reviewer_new", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("DefaultReviewer", "default_reviewer_new", "submit")
    def test_submit(self):
        data = FactoryFloor.DefaultReviewerFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("DefaultReviewer", "default_reviewer_new", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("travel:default_reviewer_new", f"/en/travel-plans/settings/default-reviewers/new/")


class TestDefaultReviewerUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.DefaultReviewerFactory()
        self.test_url = reverse_lazy('travel:default_reviewer_edit', args=[self.instance.pk, ])
        self.expected_template = 'travel/default_reviewer/default_reviewer_form.html'
        self.user = self.get_and_login_user(in_group="travel_adm_admin")

    @tag("DefaultReviewer", "default_reviewer_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.DefaultReviewerUpdateView, CommonUpdateView)

    @tag("DefaultReviewer", "default_reviewer_edit", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("DefaultReviewer", "default_reviewer_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.DefaultReviewerFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("DefaultReviewer", "default_reviewer_edit", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("travel:default_reviewer_edit", f"/en/travel-plans/settings/default-reviewers/{self.instance.pk}/edit/", [self.instance.pk])


class TestDefaultReviewerDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.DefaultReviewerFactory()
        self.test_url = reverse_lazy('travel:default_reviewer_delete', args=[self.instance.pk, ])
        self.expected_template = 'travel/default_reviewer/default_reviewer_confirm_delete.html'
        self.user = self.get_and_login_user(in_group="travel_adm_admin")

    @tag("DefaultReviewer", "default_reviewer_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(views.DefaultReviewerUpdateView, CommonUpdateView)

    @tag("DefaultReviewer", "default_reviewer_delete", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("DefaultReviewer", "default_reviewer_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.DefaultReviewerFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(models.DefaultReviewer.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("DefaultReviewer", "default_reviewer_delete", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("travel:default_reviewer_delete", f"/en/travel-plans/settings/default-reviewers/{self.instance.pk}/delete/", [self.instance.pk])


class TestReferenceMaterialListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ReferenceMaterialFactory()
        self.test_url = reverse_lazy('travel:ref_mat_list')
        self.expected_template = 'travel/list.html'
        self.user = self.get_and_login_user(in_group="travel_adm_admin")

    @tag("ReferenceMaterial", "ref_mat_list", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ReferenceMaterialListView, CommonListView)

    @tag("ReferenceMaterial", "ref_mat_list", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("ReferenceMaterial", "ref_mat_list", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("travel:ref_mat_list", f"/en/travel-plans/settings/reference-materials/")


class TestReferenceMaterialCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ReferenceMaterialFactory()
        self.test_url = reverse_lazy('travel:ref_mat_new')
        self.expected_template = 'travel/form.html'
        self.user = self.get_and_login_user(in_group="travel_adm_admin")

    @tag("ReferenceMaterial", "ref_mat_new", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ReferenceMaterialCreateView, CommonCreateView)

    @tag("ReferenceMaterial", "ref_mat_new", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("ReferenceMaterial", "ref_mat_new", "submit")
    def test_submit(self):
        data = FactoryFloor.ReferenceMaterialFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("ReferenceMaterial", "ref_mat_new", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("travel:ref_mat_new", f"/en/travel-plans/settings/reference-materials/new/")


class TestReferenceMaterialUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ReferenceMaterialFactory()
        self.test_url = reverse_lazy('travel:ref_mat_edit', args=[self.instance.pk, ])
        self.expected_template = 'travel/form.html'
        self.user = self.get_and_login_user(in_group="travel_adm_admin")

    @tag("ReferenceMaterial", "ref_mat_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ReferenceMaterialUpdateView, CommonUpdateView)

    @tag("ReferenceMaterial", "ref_mat_edit", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("ReferenceMaterial", "ref_mat_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.ReferenceMaterialFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("ReferenceMaterial", "ref_mat_edit", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("travel:ref_mat_edit", f"/en/travel-plans/settings/reference-materials/{self.instance.pk}/edit/", [self.instance.pk])


class TestReferenceMaterialDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ReferenceMaterialFactory()
        self.test_url = reverse_lazy('travel:ref_mat_delete', args=[self.instance.pk, ])
        self.expected_template = 'travel/confirm_delete.html'
        self.user = self.get_and_login_user(in_group="travel_adm_admin")

    @tag("ReferenceMaterial", "ref_mat_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ReferenceMaterialUpdateView, CommonUpdateView)

    @tag("ReferenceMaterial", "ref_mat_delete", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("ReferenceMaterial", "ref_mat_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.ReferenceMaterialFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(models.ReferenceMaterial.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("ReferenceMaterial", "ref_mat_delete", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("travel:ref_mat_delete", f"/en/travel-plans/settings/reference-materials/{self.instance.pk}/delete/", [self.instance.pk])


class TestUserListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.UserFactory()
        self.test_url1 = reverse_lazy('travel:user_list')
        self.test_url2 = reverse_lazy('travel:user_list') + "?travel_only=true"
        self.expected_template = 'travel/user_list.html'
        self.user = self.get_and_login_user(in_group="travel_adm_admin")

    @tag("User", "user_list", "view")
    def test_view_class(self):
        self.assert_inheritance(views.UserListView, CommonFilterView)

    @tag("User", "user_list", "access")
    def test_view(self):
        self.assert_good_response(self.test_url1)
        self.assert_good_response(self.test_url2)
        self.assert_non_public_view(test_url=self.test_url1, expected_template=self.expected_template, user=self.user)

    @tag("User", "user_list", "context")
    def test_context(self):
        context_vars = [
            "admin_group",
            "adm_admin_group",
        ]
        self.assert_presence_of_context_vars(self.test_url1, context_vars, user=self.user)

    @tag("User", "user_list", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("travel:user_list", f"/en/travel-plans/settings/users/")


class TestToggleUserView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = UserFactory()
        self.type1 = "admin"
        self.type2 = "adm_admin"
        self.test_url1 = reverse_lazy('travel:toggle_user', args=[self.instance.pk, self.type1])
        self.test_url2 = reverse_lazy('travel:toggle_user', args=[self.instance.pk, self.type2])
        self.user = self.get_and_login_user(in_group="travel_adm_admin")

    @tag("ToggleUser", "toggle_user", "access")
    def test_view(self):
        self.assert_good_response(self.test_url1)
        self.assert_good_response(self.test_url2)
        self.assert_non_public_view(test_url=self.test_url1, user=self.user, expected_code=302)
        self.assert_non_public_view(test_url=self.test_url2, user=self.user, expected_code=302)

    @tag("ToggleUser", "toggle_user", )
    def test_toggle(self):
        activate("en")
        self.get_and_login_user(user=self.user)
        # to start, user should not be in the admin group
        self.assertFalse(utils.in_travel_admin_group(self.instance))
        self.client.get(self.test_url1)
        self.assertTrue(utils.in_travel_admin_group(self.instance))
        self.assertFalse(utils.in_adm_admin_group(self.instance))
        self.client.get(self.test_url2)
        self.assertTrue(utils.in_adm_admin_group(self.instance))

    @tag("ToggleUser", "toggle_user", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("travel:toggle_user", f"/en/travel-plans/settings/users/{self.instance.pk}/toggle/{self.type1}/",
                                [self.instance.pk, self.type1])
        self.assert_correct_url("travel:toggle_user", f"/en/travel-plans/settings/users/{self.instance.pk}/toggle/{self.type2}/",
                                [self.instance.pk, self.type2])


class TestReportFormView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('travel:reports', args=[])
        self.expected_template = 'travel/reports.html'
        self.user = self.get_and_login_user(in_group="travel_admin")

    @tag("Report", "reports", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ReportFormView, CommonFormView)

    @tag("Report", "reports", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Report", "reports", "submit")
    def test_submit(self):
        data = dict(report=1)
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Report", "reports", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("travel:reports", f"/en/travel-plans/reports/search/")


class TestCFTSReportView(CommonTest):
    def setUp(self):
        super().setUp()
        self.trip_request = FactoryFloor.TripRequestFactory()
        self.trip = FactoryFloor.TripFactory()
        self.test_url1 = reverse_lazy('travel:export_cfts_list', args=[])
        self.test_url2 = reverse_lazy('travel:export_cfts_request', args=[self.trip_request.id])
        self.test_url3 = reverse_lazy('travel:export_cfts_trip', args=[self.trip.id])
        self.user = self.get_and_login_user(in_group="travel_admin")

    @tag("CFTSReport", "export_cfts_list", "access")
    def test_view(self):
        self.assert_good_response(self.test_url1)
        self.assert_good_response(self.test_url2)
        self.assert_good_response(self.test_url3)
        self.assert_non_public_view(test_url=self.test_url1, user=self.user)


class TestTripListReportView(CommonTest):
    def setUp(self):
        super().setUp()
        for i in range(0, 10):
            FactoryFloor.TripFactory()
        self.test_url1 = reverse_lazy('travel:export_trip_list', args=[])
        self.user = self.get_and_login_user(in_group="travel_admin")

    @tag("TripListReport", "export_trip_list", "access")
    def test_view(self):
        self.assert_good_response(self.test_url1)
        self.assert_non_public_view(test_url=self.test_url1, user=self.user)


class TestUpcomingTripsReportView(CommonTest):
    def setUp(self):
        super().setUp()
        for i in range(0, 10):
            FactoryFloor.TripFactory()
        self.test_url1 = reverse_lazy('travel:export_upcoming_trips', args=[])
        self.user = self.get_and_login_user(in_group="travel_admin")

    @tag("TripListReport", "export_upcoming_trips", "access")
    def test_view(self):
        self.assert_good_response(self.test_url1)
        self.assert_non_public_view(test_url=self.test_url1, user=self.user)


class TestIndexTemplateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('travel:index', args=[])
        self.expected_template = 'travel/index/main.html'
        self.user = self.get_and_login_user()

    @tag("Index", "index", "view")
    def test_view_class(self):
        self.assert_inheritance(views.IndexTemplateView, CommonTemplateView)

    @tag("Index", "index", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Index", "index", "context")
    def test_context(self):
        context_vars = [
            "processes",
            "information_sections",
            "faqs",
            "refs",
            "is_admin",
            "is_adm_admin",
            "can_see_all_requests",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    @tag("Index", "index", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("travel:index", f"/en/travel-plans/")


# REQUESTS

class TestTripRequestListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.TripRequestFactory()
        self.test_url = reverse_lazy('travel:request_list', args=[])
        self.expected_template = 'travel/request_list/main.html'
        self.user = self.get_and_login_user()

    @tag("TripRequest", "request_list", "view")
    def test_view_class(self):
        self.assert_inheritance(views.TripRequestListView, CommonTemplateView)

    @tag("TripRequest", "request_list", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("TripRequest", "request_list", "context")
    def test_context(self):
        context_vars = [
            "status_choices",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    @tag("TripRequest", "request_list", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("travel:request_list", f"/en/travel-plans/requests/")


class TestTripRequestCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.TripRequestFactory()
        self.test_url = reverse_lazy('travel:request_new', args=[])
        self.expected_template = 'travel/request_form.html'
        self.user = self.get_and_login_user()

    @tag("TripRequest", "request_new", "view")
    def test_view_class(self):
        self.assert_inheritance(views.TripRequestCreateView, CommonCreateView)

    @tag("TripRequest", "request_new", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("TripRequest", "request_new", "submit")
    def test_submit(self):
        data = FactoryFloor.TripRequestFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("TripRequest", "request_new", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("travel:request_new", f"/en/travel-plans/requests/new/")


class TestTripRequestDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.TripRequestFactory()
        self.test_url1 = reverse_lazy('travel:request_detail', args=[self.instance.pk])
        self.test_url2 = reverse_lazy('travel:request_detail_by_uuid', args=[self.instance.uuid])
        self.expected_template = 'travel/request_detail.html'
        self.user = self.get_and_login_user()

    @tag("TripRequest", "request_view", "view")
    def test_view_class(self):
        self.assert_inheritance(views.TripRequestDetailView, CommonDetailView)

    @tag("TripRequest", "request_view", "access")
    def test_view(self):
        self.assert_good_response(self.test_url1)
        self.assert_good_response(self.test_url2)
        self.assert_non_public_view(test_url=self.test_url1, expected_template=self.expected_template, user=self.user)

    @tag("TripRequest", "request_view", "context")
    def test_context(self):
        context_vars = [
            "trip_request",
        ]
        self.assert_presence_of_context_vars(self.test_url1, context_vars, user=self.user)

    @tag("TripRequest", "request_view", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("travel:request_detail", f"/en/travel-plans/requests/{self.instance.pk}/view/", [self.instance.pk])
        self.assert_correct_url("travel:request_detail_by_uuid", f"/en/travel-plans/requests/uuid/{self.instance.uuid}/", [self.instance.uuid])


class TestTripRequestUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.TripRequestFactory()
        self.test_url = reverse_lazy('travel:request_edit', args=[self.instance.pk])
        self.expected_template = 'travel/request_form.html'
        self.user = self.get_and_login_user(self.instance.created_by)

    @tag("TripRequest", "request_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.TripRequestUpdateView, CommonUpdateView)

    @tag("TripRequest", "request_edit", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("TripRequest", "request_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.TripRequestFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("TripRequest", "request_edit", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("travel:request_edit", f"/en/travel-plans/requests/{self.instance.pk}/edit/", [self.instance.pk])


class TestTripRequestDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.TripRequestFactory()
        self.test_url = reverse_lazy('travel:request_delete', args=[self.instance.pk])
        self.expected_template = 'travel/confirm_delete.html'
        self.user = self.get_and_login_user(self.instance.created_by)

    @tag("TripRequest", "request_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(views.TripRequestDeleteView, CommonDeleteView)

    @tag("TripRequest", "request_delete", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("TripRequest", "request_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.TripRequestFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(models.TripRequest.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("TripRequest", "request_delete", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("travel:request_delete", f"/en/travel-plans/requests/{self.instance.pk}/delete/", [self.instance.pk])


class TestTripRequestCloneUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.TripRequestFactory()
        self.test_url = reverse_lazy('travel:request_clone', args=[self.instance.pk])
        self.expected_template = 'travel/request_form.html'
        self.user = self.get_and_login_user()

    @tag("TripRequest", "request_clone", "view")
    def test_view_class(self):
        self.assert_inheritance(views.TripRequestCloneUpdateView, CommonUpdateView)
        self.assert_inheritance(views.TripRequestCloneUpdateView, views.TripRequestUpdateView)

    @tag("TripRequest", "request_clone", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("TripRequest", "request_clone", "context")
    def test_context(self):
        context_vars = [
            "cloned",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    @tag("TripRequest", "request_clone", "submit")
    def test_submit(self):
        data = FactoryFloor.TripRequestFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("TripRequest", "request_clone", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("travel:request_clone", f"/en/travel-plans/requests/{self.instance.pk}/clone/", [self.instance.pk])


class TestTripRequestCancelUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.TripRequestFactory()
        self.test_url = reverse_lazy('travel:request_cancel', args=[self.instance.pk])
        self.expected_template = 'travel/form.html'
        self.user1 = self.get_and_login_user(in_group="travel_adm_admin")
        self.user2 = self.get_and_login_user(in_group="travel_adm_admin")

    @tag("TripRequest", "request_cancel", "view")
    def test_view_class(self):
        self.assert_inheritance(views.TripRequestCancelUpdateView, CommonUpdateView)
        self.assert_inheritance(views.TripRequestCancelUpdateView, views.TravelAdminRequiredMixin)

    @tag("TripRequest", "request_cancel", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user1)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user2)

    @tag("TripRequest", "request_cancel", "submit")
    def test_submit(self):
        data = FactoryFloor.TripRequestFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user1)
        self.assert_success_url(self.test_url, data=data, user=self.user2)

    @tag("TripRequest", "request_cancel", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("travel:request_cancel", f"/en/travel-plans/requests/{self.instance.pk}/cancel/", [self.instance.pk])



# TRIPS

class TestTripListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.TripFactory()
        self.test_url = reverse_lazy('travel:trip_list', args=[])
        self.expected_template = 'travel/trip_list/main.html'
        self.user = self.get_and_login_user()

    @tag("Trip", "trip_list", "view")
    def test_view_class(self):
        self.assert_inheritance(views.TripListView, CommonTemplateView)

    @tag("Trip", "trip_list", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Trip", "trip_list", "context")
    def test_context(self):
        context_vars = [
            "status_choices",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    @tag("Trip", "trip_list", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("travel:trip_list", f"/en/travel-plans/trips/")


class TestTripCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.TripFactory()
        self.test_url1 = reverse_lazy('travel:trip_new', args=[])
        self.test_url2 = reverse_lazy('travel:trip_new', args=[]) + "?pop=true"
        self.expected_template = 'travel/trip_form.html'
        self.user = self.get_and_login_user()

    @tag("Trip", "trip_new", "view")
    def test_view_class(self):
        self.assert_inheritance(views.TripCreateView, CommonCreateView)

    @tag("Trip", "trip_new", "access")
    def test_view(self):
        self.assert_good_response(self.test_url1)
        self.assert_good_response(self.test_url2)
        self.assert_non_public_view(test_url=self.test_url1, expected_template=self.expected_template, user=self.user)

    @tag("Trip", "trip_new", "submit")
    def test_submit(self):
        data = FactoryFloor.TripFactory.get_valid_data()
        self.assert_success_url(self.test_url1, data=data, user=self.user)

    @tag("Trip", "trip_new", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("travel:trip_new", f"/en/travel-plans/trips/new/")


class TestTripDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.TripFactory()
        self.test_url = reverse_lazy('travel:trip_detail', args=[self.instance.pk])
        self.expected_template = 'travel/trip_detail.html'
        self.user = self.get_and_login_user()

    @tag("Trip", "trip_view", "view")
    def test_view_class(self):
        self.assert_inheritance(views.TripDetailView, CommonDetailView)

    @tag("Trip", "trip_view", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Trip", "trip_view", "context")
    def test_context(self):
        context_vars = [
            "trip",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    @tag("Trip", "trip_view", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("travel:trip_detail", f"/en/travel-plans/trips/{self.instance.pk}/view/", [self.instance.pk])


class TestTripUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance1 = FactoryFloor.TripFactory(is_adm_approval_required=True)
        self.instance2 = FactoryFloor.TripFactory(is_adm_approval_required=False)
        self.test_url1 = reverse_lazy('travel:trip_edit', args=[self.instance1.pk])
        self.test_url2 = reverse_lazy('travel:trip_edit', args=[self.instance2.pk])
        self.expected_template = 'travel/trip_form.html'
        self.regional_admin_user = self.get_and_login_user(in_group="travel_admin")
        self.ncr_admin_user = self.get_and_login_user(in_group="travel_adm_admin")

    @tag("Trip", "trip_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.TripUpdateView, CommonUpdateView)

    @tag("Trip", "trip_edit", "access")
    def test_view(self):
        self.assert_good_response(self.test_url1)
        # this is the adm trip
        self.assert_non_public_view(test_url=self.test_url1, expected_template=self.expected_template, user=self.ncr_admin_user, bad_user_list=[self.regional_admin_user])
        # this is the regional trip
        self.assert_non_public_view(test_url=self.test_url2, expected_template=self.expected_template, user=self.regional_admin_user)

    @tag("Trip", "trip_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.TripFactory.get_valid_data()
        self.assert_success_url(self.test_url1, data=data, user=self.ncr_admin_user)

    @tag("Trip", "trip_edit", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("travel:trip_edit", f"/en/travel-plans/trips/{self.instance1.pk}/edit/", [self.instance1.pk])


class TestTripDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance1 = FactoryFloor.TripFactory(is_adm_approval_required=True)
        self.instance2 = FactoryFloor.TripFactory(is_adm_approval_required=False)
        self.test_url1 = reverse_lazy('travel:trip_delete', args=[self.instance1.pk])
        self.test_url2 = reverse_lazy('travel:trip_delete', args=[self.instance2.pk])
        self.expected_template = 'travel/confirm_delete.html'
        self.regional_admin_user = self.get_and_login_user(in_group="travel_admin")
        self.ncr_admin_user = self.get_and_login_user(in_group="travel_adm_admin")

    @tag("Trip", "trip_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(views.TripDeleteView, CommonDeleteView)

    @tag("Trip", "trip_delete", "access")
    def test_view(self):
        self.assert_good_response(self.test_url1)
        # this is the adm trip
        self.assert_non_public_view(test_url=self.test_url1, expected_template=self.expected_template, user=self.ncr_admin_user,
                                    bad_user_list=[self.regional_admin_user])
        # this is the regional trip
        self.assert_non_public_view(test_url=self.test_url2, expected_template=self.expected_template, user=self.regional_admin_user)

    @tag("Trip", "trip_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.TripFactory.get_valid_data()
        self.assert_success_url(self.test_url1, data=data, user=self.ncr_admin_user)

        # for delete views...
        self.assertEqual(models.Trip.objects.filter(pk=self.instance1.pk).count(), 0)

    @tag("Trip", "trip_delete", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("travel:trip_delete", f"/en/travel-plans/trips/{self.instance1.pk}/delete/", [self.instance1.pk])


class TestTripCloneUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.TripFactory()
        self.test_url = reverse_lazy('travel:trip_clone', args=[self.instance.pk])
        self.expected_template = 'travel/trip_form.html'
        self.user = self.get_and_login_user()

    @tag("Trip", "trip_clone", "view")
    def test_view_class(self):
        self.assert_inheritance(views.TripCloneView, views.TripUpdateView)

    @tag("Trip", "trip_clone", "access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Trip", "trip_clone", "context")
    def test_context(self):
        context_vars = [
            "cloned",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    @tag("Trip", "trip_clone", "submit")
    def test_submit(self):
        data = FactoryFloor.TripFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Trip", "trip_clone", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("travel:trip_clone", f"/en/travel-plans/trips/{self.instance.pk}/clone/", [self.instance.pk])


class TestTripCancelUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance1 = FactoryFloor.TripFactory(is_adm_approval_required=True)
        self.instance2 = FactoryFloor.TripFactory(is_adm_approval_required=False)
        self.test_url1 = reverse_lazy('travel:trip_cancel', args=[self.instance1.pk])
        self.test_url2 = reverse_lazy('travel:trip_cancel', args=[self.instance2.pk])
        self.expected_template = 'travel/form.html'
        self.regional_admin_user = self.get_and_login_user(in_group="travel_admin")
        self.ncr_admin_user = self.get_and_login_user(in_group="travel_adm_admin")

    @tag("Trip", "trip_cancel", "view")
    def test_view_class(self):
        self.assert_inheritance(views.TripCancelUpdateView, CommonUpdateView)
        self.assert_inheritance(views.TripCancelUpdateView, views.TravelAdminRequiredMixin)

    @tag("Trip", "trip_cancel", "access")
    def test_view(self):
        self.assert_good_response(self.test_url1)
        # this is the adm trip
        self.assert_non_public_view(test_url=self.test_url1, expected_template=self.expected_template, user=self.ncr_admin_user,
                                    bad_user_list=[self.regional_admin_user])
        # this is the regional trip
        self.assert_non_public_view(test_url=self.test_url2, expected_template=self.expected_template, user=self.regional_admin_user)

    @tag("Trip", "trip_cancel", "submit")
    def test_submit(self):
        data = FactoryFloor.TripFactory.get_valid_data()
        self.assert_success_url(self.test_url1, data=data, user=self.ncr_admin_user)

    @tag("Trip", "trip_cancel", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("travel:trip_cancel", f"/en/travel-plans/trips/{self.instance1.pk}/cancel/", [self.instance1.pk])

class TestTripReviewProcessUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance1 = FactoryFloor.TripFactory(is_adm_approval_required=True)
        self.test_url1 = reverse_lazy('travel:trip_review_toggle', args=[self.instance1.pk])
        self.expected_template = 'travel/form.html'
        self.ncr_admin_user = self.get_and_login_user(in_group="travel_adm_admin")

    @tag("Trip", "trip_review_toggle", "view")
    def test_view_class(self):
        self.assert_inheritance(views.TripReviewProcessUpdateView, CommonUpdateView)
        self.assert_inheritance(views.TripReviewProcessUpdateView, views.TravelAdminRequiredMixin)

    @tag("Trip", "trip_review_toggle", "access")
    def test_view(self):
        self.assert_good_response(self.test_url1)
        # this is the adm trip
        self.assert_non_public_view(test_url=self.test_url1, expected_template=self.expected_template, user=self.ncr_admin_user)

    @tag("Trip", "trip_review_toggle", "submit")
    def test_submit(self):
        data = FactoryFloor.TripFactory.get_valid_data()
        self.assert_success_url(self.test_url1, data=data, user=self.ncr_admin_user)

    @tag("Trip", "trip_review_toggle", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("travel:trip_review_toggle", f"/en/travel-plans/trips/{self.instance1.pk}/review-process/", [self.instance1.pk])
