from django.urls import reverse_lazy
from django.test import tag

from shared_models.views import CommonDeleteView
from .. import models
from .. import views
from whalebrary import views
from whalebrary.test import FactoryFloor
from whalebrary.test.common_tests import CommonWhalebraryTest as CommonTest

class TestItemDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ItemFactory()
        self.test_url = reverse_lazy('whalebrary:item_delete', args=[self.instance.pk, ])
        self.expected_template = 'whalebrary/confirm_delete.html'
        self.user = self.get_and_login_user(in_group="whalebrary_edit")

 

    @tag("Item", "item_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ItemDeleteView, CommonDeleteView)
        self.assert_inheritance(views.ItemDeleteView, views.WhalebraryEditRequiredMixin)

 

    @tag("Item", "item_delete", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)


    @tag("Item", "item_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.ItemFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)
        
        # for delete views...
        self.assertEqual(models.Item.objects.filter(pk=self.instance.pk).count(), 0)
#
# class IndividualTripRequestDelete(CommonTravelTest):
#     def setUp(self):
#         super().setUp()
#         self.tr = IndividualTripRequestFactory()
#         self.test_url = reverse_lazy('travel:request_delete', kwargs={"pk": self.tr.pk})
#         self.expected_template = 'travel/trip_request_confirm_delete.html'
#
#     @tag("trip_request", 'delete', "view")
#     def test_view_class(self):
#         # make sure the view is inheriting from CanModify Mixin
#         self.assert_inheritance(views.TripRequestDeleteView, views.CanModifyMixin)
#
#     @tag("trip_request", 'delete', "access")
#     def test_view(self):
#         self.assert_not_broken(self.test_url)
#         # create an admin user (who should always be able to delete) and check to see there is a 200 response
#         admin_user = self.get_and_login_user(in_group="travel_admin")
#         self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=admin_user)
#
#     @tag("trip_request", 'delete', "submit")
#     def test_submit(self):
#         # use an admin user because they should always be able to delete
#         admin_user = self.get_and_login_user(in_group="travel_admin")
#         self.assert_success_url(self.test_url, user=admin_user)
#         # ensure the user is deleted
#         self.assertEqual(models.TripRequest.objects.filter(pk=self.tr.pk).count(), 0)
