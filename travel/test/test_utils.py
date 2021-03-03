from django.test import tag
from django.utils import timezone
from django.utils.translation import activate

from shared_models.models import Region
from shared_models.test.SharedModelsFactoryFloor import SectionFactory, UserFactory
from travel.test import FactoryFloor
from travel.test.common_tests import CommonTravelTest as CommonTest
from travel.views import can_modify_request
from .. import utils, models


class UtilsTest(CommonTest):

    def setUp(self):
        super().setUp()  # used to import fixutres

    @tag("utils", )
    def test_in_admin_group(self):
        user = self.get_and_login_user()
        admin = self.get_and_login_user(in_group='travel_admin')
        adm_admin = self.get_and_login_user(in_group='travel_adm_admin')
        self.assertFalse(utils.in_travel_admin_group(user))
        self.assertFalse(utils.in_travel_admin_group(adm_admin))
        self.assertTrue(utils.in_travel_admin_group(admin))

    @tag("utils", )
    def test_in_adm_admin_group(self):
        user = self.get_and_login_user()
        admin = self.get_and_login_user(in_group='travel_admin')
        adm_admin = self.get_and_login_user(in_group='travel_adm_admin')
        self.assertFalse(utils.in_adm_admin_group(user))
        self.assertFalse(utils.in_adm_admin_group(admin))
        self.assertTrue(utils.in_adm_admin_group(adm_admin))

    @tag("utils", )
    def test_as_admin(self):
        user = self.get_and_login_user()
        admin = self.get_and_login_user(in_group='travel_admin')
        adm_admin = self.get_and_login_user(in_group='travel_adm_admin')
        self.assertFalse(utils.is_admin(user))
        self.assertTrue(utils.is_admin(admin))
        self.assertTrue(utils.is_admin(adm_admin))

    @tag("utils", )
    def test_is_approver(self):
        user = self.get_and_login_user()
        trip_request = FactoryFloor.TripRequestFactory(status=17)
        self.assertFalse(utils.is_approver(user, trip_request))
        FactoryFloor.ReviewerFactory(user=user, request=trip_request, status=1)
        self.assertTrue(utils.is_approver(user, trip_request))

    @tag("utils", )
    def test_is_trip_approver(self):
        user = self.get_and_login_user()
        trip = FactoryFloor.TripFactory(status=31)
        self.assertFalse(utils.is_trip_approver(user, trip))
        FactoryFloor.TripReviewerFactory(user=user, trip=trip, status=25)
        self.assertTrue(utils.is_trip_approver(user, trip))

    @tag("utils", )
    def test_is_adm(self):
        # scenario #1
        user = self.get_and_login_user()
        self.assertFalse(utils.is_adm(user))
        national_branch, created = Region.objects.get_or_create(name="national")
        national_branch.head = user
        national_branch.save()
        self.assertTrue(utils.is_adm(user))
        # scenario #2
        user = self.get_and_login_user()
        self.assertFalse(utils.is_adm(user))
        models.DefaultReviewer.objects.get_or_create(user=user, special_role=5)
        national_branch.head = user
        national_branch.save()
        self.assertTrue(utils.is_adm(user))

    @tag("utils", )
    def test_get_request_reviewers(self):
        section = SectionFactory(head=UserFactory(), admin=UserFactory())
        division = section.division(head=UserFactory(), admin=UserFactory())
        branch = division.branch(head=UserFactory(), admin=UserFactory())
        region = branch.region(head=UserFactory(), admin=UserFactory())

        trip_request = FactoryFloor.TripRequestFactory(status=17)
        self.assertEqual(trip_request.reviewers.count(), 0)
        utils.get_request_reviewers(trip_request)





    @tag("utils", 'can_modify')
    def test_can_modify_rules(self):
        activate('en')

        # actors
        trip_request = FactoryFloor.TripRequestFactory()
        traveller = FactoryFloor.TravellerFactory(request=trip_request)
        reg_user = self.get_and_login_user()
        admin_user = self.get_and_login_user(in_group="travel_admin")
        adm_admin_user = self.get_and_login_user(in_group="travel_adm_admin")

        # RULE 1: travel admin = True
        self.assertEqual(can_modify_request(admin_user, trip_request.id), True)
        self.assertEqual(can_modify_request(adm_admin_user, trip_request.id), True)

        # RULE 2: a current reviewer; they must be able to edit a child trip and the parent trip
        # a)
        my_reviewer = FactoryFloor.ReviewerFactory(request=trip_request, status=1)
        trip_request.status = 17
        trip_request.save()
        self.assertTrue(can_modify_request(my_reviewer.user, trip_request.id))

        # RULE 3: when a trip is unsubmitted, randos cannot edit
        self.assertFalse(can_modify_request(reg_user, trip_request.id))

        # RULE 4: when a trip is unsubmitted, owners can edit
        self.assertTrue(can_modify_request(trip_request.created_by, trip_request.id))

        # RULE 5: when a trip is unsubmitted, travellers can edit
        self.assertTrue(can_modify_request(traveller.user, trip_request.id))

        # RULE 6: owners are always able to unsubmit a trip
        trip_request.submitted = timezone.now()
        trip_request.save()
        self.assertTrue(can_modify_request(trip_request.created_by, trip_request.id, True))
        trip_request.status = 22
        trip_request.save()
        self.assertTrue(can_modify_request(trip_request.created_by, trip_request.id, True))

    # @tag("utils", 'get_related_trips')
    # def test_get_related_trips(self):
    #     activate('en')
    #
    #     # actors
    #     ind_request = FactoryFloor.IndividualTripRequestFactory()
    #     child_request = FactoryFloor.ChildTripRequestFactory()
    #     child_request1 = FactoryFloor.ChildTripRequestFactory()
    #     parent_request = child_request.parent_request
    #     random_request = FactoryFloor.IndividualTripRequestFactory()
    #
    #     reg_user = self.get_and_login_user()
    #
    #     # to start, this user should have 0 trips
    #     self.assertEqual(utils.get_related_trips(reg_user).count(), 0)
    #
    #     # setting the individual request to user should result in 1 trip
    #     ind_request.user = reg_user
    #     ind_request.save()
    #     self.assertIn(ind_request, utils.get_related_trips(reg_user))
    #     self.assertEqual(utils.get_related_trips(reg_user).count(), 1)
    #
    #     # setting parent of group trip to user should increase by 1...
    #     parent_request.user = reg_user
    #     parent_request.save()
    #     self.assertIn(parent_request, utils.get_related_trips(reg_user))
    #     self.assertEqual(utils.get_related_trips(reg_user).count(), 2)
    #
    #     # setting parent of child trip to user should NOT increase by 1, since this is the same trip as the parent trip...
    #     child_request.user = reg_user
    #     child_request.save()
    #     self.assertNotIn(child_request, utils.get_related_trips(reg_user))
    #     self.assertEqual(utils.get_related_trips(reg_user).count(), 2)
    #
    #     # setting parent of child trip to user should increase by 1...
    #     child_request1.user = reg_user
    #     child_request1.save()
    #     self.assertIn(child_request1.parent_request, utils.get_related_trips(reg_user))
    #     self.assertEqual(utils.get_related_trips(reg_user).count(), 3)
    #
    #     # setting created_by of random trip to user should increase by 1...
    #     random_request.created_by = reg_user
    #     random_request.save()
    #     self.assertIn(random_request, utils.get_related_trips(reg_user))
    #     self.assertEqual(utils.get_related_trips(reg_user).count(), 4)
    #
    # @tag("utils", 'trip_review_process')
    # def test_trip_review_process(self):
    #     activate('en')
    #
    #     # actors
    #     trip = FactoryFloor.TripFactory(status=41)  # unreviewed, verified
    #     reviewer1 = FactoryFloor.TripReviewerFactory(trip=trip, order=1)
    #     reviewer2 = FactoryFloor.TripReviewerFactory(trip=trip, order=2)
    #     reviewer3 = FactoryFloor.TripReviewerFactory(trip=trip, order=3)
    #
    #     self.assertIsNone(trip.review_start_date)
    #     utils.start_trip_review_process(trip)
    #     self.assertEqual(trip.status, 31)
    #     self.assertIsNotNone(trip.review_start_date)
    #     for reviewer in trip.reviewers.all():
    #         self.assertEqual(reviewer.status, 24)
    #         self.assertIsNone(reviewer.status_date)
    #
    #     # now let's end the review process
    #     utils.end_trip_review_process(trip)
    #     self.assertEqual(trip.status, 41)
    #     # the timestamp should not be undone
    #     self.assertIsNotNone(trip.review_start_date)
    #     for reviewer in trip.reviewers.all():
    #         self.assertEqual(reviewer.status, 23)
    #         self.assertIsNone(reviewer.status_date)
    #
    # @tag("utils", 'tr_review_process')
    # def test_tr_review_process(self):
    #     activate('en')
    #
    #     # actors
    #     tr = FactoryFloor.IndividualTripRequestFactory(status=8)  # draft
    #     reviewer1 = FactoryFloor.ReviewerFactory(trip_request=tr, order=1)
    #     reviewer2 = FactoryFloor.ReviewerFactory(trip_request=tr, order=2)
    #     reviewer3 = FactoryFloor.ReviewerFactory(trip_request=tr, order=3)
    #
    #     utils.start_request_review_process(tr)
    #     for reviewer in tr.reviewers.all():
    #         self.assertEqual(reviewer.status, 20)
    #         self.assertIsNone(reviewer.status_date)
    #
    #     # now let's end the review process
    #     utils.end_request_review_process(tr)
    #     for reviewer in tr.reviewers.all():
    #         self.assertEqual(reviewer.status, 4)
    #         self.assertIsNone(reviewer.status_date)

# TODO: trip approval seeker
# TODO: trip request approval seeker
