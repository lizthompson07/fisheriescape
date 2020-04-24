from django.urls import reverse_lazy
from django.test import tag
from django.views.generic import CreateView

from travel.test import FactoryFloor
from travel.test.common_tests import CommonTravelTest as CommonTest
from .. import views
from .. import models

class IndividualTripRequestCreate(CommonTest):

    def setUp(self):
        super().setUp()  # used to import fixutres
        self.trip_request = FactoryFloor.IndividualTripRequestFactory()
        self.test_url = reverse_lazy('travel:request_new')
        self.expected_template = 'travel/trip_request_form.html'

    @tag("trip_request", 'create', 'response')
    def test_access(self):
        # only logged in users can access the landing
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template)

    # Test that the context contains the proper vars
    @tag("trip_request", 'create', "context")
    def test_context(self):
        context_vars = [
            "user_json",
            "conf_json",
            "help_text_dict",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars)

    @tag("trip_request", 'create', "submit")
    def test_submit(self):
        data = FactoryFloor.IndividualTripRequestFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data)
        # TODO: now we will want to make sense that the reviewers make sense... adm vs. non adm.. regional ppl etc


class TestTripCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('travel:trip_new')
        self.expected_template = 'travel/trip_new.html'

    @tag("travel", 'create', "view")
    def test_view_class(self):
        self.assert_inheritance(views.TripCreateView, CreateView)

    @tag("travel", 'create', "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template)

    @tag("travel", 'create', "context")
    def test_context(self):
        context_vars = [
            "help_text_dict",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars)
    
    @tag("travel", 'create', "submit")
    def test_submit(self):
        data = FactoryFloor.TripFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data)


class TestTripCreateViewPopup(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('travel:trip_new', kwargs={"pop": 1})
        self.expected_template = 'travel/trip_form_popout.html'

    @tag("travel", 'create', "view")
    def test_view_class(self):
        self.assert_inheritance(views.TripCreateView, CreateView)

    @tag("travel", 'create', "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template)

    @tag("travel", 'create', "context")
    def test_context(self):
        context_vars = [
            "help_text_dict",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars)

    @tag("travel", 'create', "submit")
    def test_submit(self):
        data = FactoryFloor.TripFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data)

