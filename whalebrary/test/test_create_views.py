from django.urls import reverse_lazy
from django.test import tag

from shared_models.views import CommonCreateView
from whalebrary import views
from whalebrary.test import FactoryFloor
from whalebrary.test.common_tests import CommonWhalebraryTest as CommonTest

class TestItemCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ItemFactory()
        self.test_url = reverse_lazy('whalebrary:item_new')
        self.expected_template = 'whalebrary/form.html'
        self.user = self.get_and_login_user(in_group="whalebrary_edit")



    @tag("Item", "item_new", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ItemCreateView, CommonCreateView)
        self.assert_inheritance(views.ItemCreateView, views.WhalebraryEditRequiredMixin)



    @tag("Item", "item_new", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)


    @tag("Item", "item_new", "submit")
    def test_submit(self):
        data = FactoryFloor.ItemFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)


#
# class IndividualTripRequestCreate(CommonTravelTest):
#
#     def setUp(self):
#         super().setUp()  # used to import fixutres
#         self.trip_request = FactoryFloor.IndividualTripRequestFactory()
#         self.test_url = reverse_lazy('travel:request_new')
#         self.expected_template = 'travel/trip_request_form.html'
#
#     @tag("trip_request", 'create', 'response')
#     def test_access(self):
#         # only logged in users can access the landing
#         self.assert_not_broken(self.test_url)
#         self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template)
#
#     # Test that the context contains the proper vars
#     @tag("trip_request", 'create', "context")
#     def test_context(self):
#         context_vars = [
#             "user_json",
#             "conf_json",
#             "help_text_dict",
#         ]
#         self.assert_presence_of_context_vars(self.test_url, context_vars)
#
#     @tag("trip_request", 'create', "submit")
#     def test_submit(self):
#         data = IndividualTripRequestFactory.get_valid_data()
#         self.assert_success_url(self.test_url, data=data)
#         # TODO: now we will want to make sense that the reviewers make sense... adm vs. non adm.. regional ppl etc
