from django.urls import reverse_lazy
from django.test import tag
from django.views.generic import CreateView, UpdateView, FormView

from travel.test import FactoryFloor
from travel.test.common_tests import CommonTravelTest as CommonTest
from .. import views
from .. import models


class TestTripRequestUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.IndividualTripRequestFactory()
        self.test_url = reverse_lazy('travel:request_edit', kwargs={"pk": self.instance.pk})
        self.expected_template = 'travel/trip_request_form.html'

    @tag("travel", 'update', "view")
    def test_view_class(self):
        self.assert_inheritance(views.TripRequestUpdateView, UpdateView)
        self.assert_inheritance(views.TripRequestUpdateView, views.CanModifyMixin)

    @tag("travel", 'update', "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.instance.user)

    @tag("travel", 'update', "context")
    def test_context(self):
        context_vars = [
            "cost_field_list",
            "user_json",
            "conf_json",
            "help_text_dict",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.instance.user)

    @tag("travel", 'update', "submit")
    def test_submit(self):
        data = FactoryFloor.IndividualTripRequestFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.instance.user)


class TestTripRequestUpdateViewPopup(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.IndividualTripRequestFactory()
        self.test_url = reverse_lazy('travel:request_edit', kwargs={"pk": self.instance.pk, "pop": 1})
        self.expected_template = 'travel/trip_request_form_popout.html'

    @tag("travel", 'update', "view")
    def test_view_class(self):
        self.assert_inheritance(views.TripRequestUpdateView, UpdateView)
        self.assert_inheritance(views.TripRequestUpdateView, views.CanModifyMixin)

    @tag("travel", 'update', "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.instance.user)

    @tag("travel", 'update', "context")
    def test_context(self):
        context_vars = [
            "cost_field_list",
            "user_json",
            "conf_json",
            "help_text_dict",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.instance.user)

    @tag("travel", 'update', "submit")
    def test_submit(self):
        data = FactoryFloor.IndividualTripRequestFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.instance.user)


class TestTripUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.TripFactory()
        self.test_url = reverse_lazy('travel:trip_edit', kwargs={"pk": self.instance.pk})
        self.expected_template = 'travel/trip_form.html'
        self.admin_user = self.get_and_login_user(in_group="travel_admin")
    @tag("travel", 'update', "view")
    def test_view_class(self):
        self.assert_inheritance(views.TripUpdateView, UpdateView)

    @tag("travel", 'update', "access")
    def test_view(self):

        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.admin_user)

    @tag("travel", 'update', "context")
    def test_context(self):
        context_vars = [
            "help_text_dict",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.admin_user)

    @tag("travel", 'update', "submit")
    def test_submit(self):
        data = FactoryFloor.TripFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.admin_user)


class TestTripUpdateViewPopout(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.TripFactory()
        self.test_url = reverse_lazy('travel:trip_edit', kwargs={"pk": self.instance.pk, "pop": 1})
        self.expected_template = 'travel/trip_form_popout.html'
        self.admin_user = self.get_and_login_user(in_group="travel_admin")

    @tag("travel", 'update', "view")
    def test_view_class(self):
        self.assert_inheritance(views.TripUpdateView, UpdateView)

    @tag("travel", 'update', "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.admin_user)

    @tag("travel", 'update', "context")
    def test_context(self):
        context_vars = [
            "help_text_dict",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.admin_user)

    @tag("travel", 'update', "submit")
    def test_submit(self):
        data = FactoryFloor.TripFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.admin_user)


class TestTripVerifyUpdateViewPopout(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.TripFactory()
        self.test_url = reverse_lazy('travel:trip_verify', kwargs={"pk": self.instance.pk, "region": 0, "adm": 0})
        self.expected_template = 'travel/trip_verification_form.html'
        self.admin_user = self.get_and_login_user(in_group="travel_admin")

    @tag("travel", 'update', "view")
    def test_view_class(self):
        self.assert_inheritance(views.TripVerifyUpdateView, FormView)
        self.assert_inheritance(views.TripVerifyUpdateView, views.TravelAdminRequiredMixin)

    @tag("travel", 'update', "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.admin_user)

    @tag("travel", 'update', "context")
    def test_context(self):
        context_vars = [
            "object",
            "conf_field_list",
            "same_day_trips",
            "same_location_trips",
            "same_name_trips",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.admin_user)

    @tag("travel", 'update', "submit")
    def test_submit(self):
        data = FactoryFloor.TripFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.admin_user)
