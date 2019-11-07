from django.db import IntegrityError

from . import models
from . import emails


def get_reviewers(trip):
    # if in gulf region, add Amelie as a reviewer
    if trip.region_id == 1:
        try:
            models.Reviewer.objects.create(trip=trip, user_id=385, role_id=1, )
        except IntegrityError:
            print("not adding amelie")

    # assuming there is a section, assign section management
    if trip.section:
        # try adding section head, division manager and rds
        try:
            models.Reviewer.objects.create(trip=trip, user=trip.section.head, role_id=2, )
        except (IntegrityError, AttributeError):
            print("not adding section head")
        try:
            models.Reviewer.objects.create(trip=trip, user=trip.section.division.head, role_id=2, )
        except (IntegrityError, AttributeError):
            print("not adding division manager")
        try:
            models.Reviewer.objects.create(trip=trip, user=trip.section.division.branch.head, role_id=2, )
        except (IntegrityError, AttributeError):
            print("not adding RDS")

    # should the ADMs office be invovled?
    if trip.is_international or trip.is_conference:
        # add the ADMs office staff
        try:
            models.Reviewer.objects.create(trip=trip, user_id=749, role_id=3, ) # Kim Cotton
        except IntegrityError:
            print("not adding NCR reviewer")
        try:
            models.Reviewer.objects.create(trip=trip, user_id=736, role_id=4, ) # Andy White
        except IntegrityError:
            print("not adding NCR recommender")
        try:
            models.Reviewer.objects.create(trip=trip, user_id=754, role_id=4, ) # Stephen Birc
        except IntegrityError:
            print("not adding NCR recommender")
        try:
            models.Reviewer.objects.create(trip=trip, user_id=740, role_id=4, )  # Wayne Moore
        except IntegrityError:
            print("not adding NCR recommender")
        try:
            models.Reviewer.objects.create(trip=trip, user_id=626, role_id=5, )  # Arran McPherson
        except IntegrityError:
            print("not adding NCR ADM")

    # finally, we always need to add the RDG
    try:
        models.Reviewer.objects.create(trip=trip, user=trip.section.division.branch.region.head, role_id=6, )
    except (IntegrityError, AttributeError):
        print("not adding RDG")


def start_review_process(trip):
    """this should be used when a project is submitted. It will change over all reviewers' statuses to Pending"""
    # focus only on reviewers that are status = Not Submitted
    for reviewer in trip.reviewers.all():
        reviewer.status_id = 1
        reviewer.save()


def end_review_process(trip):
    """this should be used when a project is submitted. It will change over all reviewers' statuses to Pending"""
    # focus only on reviewers that are status = Not Submitted
    for reviewer in trip.reviewers.all():
        reviewer.status_id = 4
        reviewer.save()


# def approval_seeker(trip):
#     """ This method if meant to seek approvals via email, set waiting_ons and set project status"""
#
#     # if someone denied it at any point, the trip is 'denied'
#
#
#         if trip.recommender_1_approval_status_id == 3 or \
#                 trip.recommender_2_approval_status_id == 3 or \
#                 trip.recommender_3_approval_status_id == 3 or \
#                 trip.adm_approval_status_id == 3 or \
#                 trip.rdg_approval_status_id == 3:
#             trip.status_id = 10  # DENIED
#             # The statuses of recommenders and approvers are handled by the form_valid method of the ApprovalUpdateView
#
#         # otherwise, if the project is submitted
#         elif trip.submitted:
#             # make sure the statuses are changed from 4 to 1
#             if trip.recommender_1_approval_status_id == 4:
#                 trip.recommender_1_approval_status_id = 1
#             if trip.recommender_2_approval_status_id == 4:
#                 trip.recommender_2_approval_status_id = 1
#             if trip.recommender_3_approval_status_id == 4:
#                 trip.recommender_3_approval_status_id = 1
#             if trip.adm_approval_status_id == 4:
#                 trip.adm_approval_status_id = 1
#             if trip.rdg_approval_status_id == 4:
#                 trip.rdg_approval_status_id = 1
#
#             # check to see if recommender 1 has reviewed the trip
#             my_email = None
#
#             if trip.recommender_1 and not trip.recommender_1_approval_date:
#                 # we need to get approval and need to set recommender 1 as who we are waiting on
#                 trip.waiting_on = trip.recommender_1
#                 # project status will be "pending recommendation"
#                 trip.status_id = 12
#                 # build email to recommender 1
#                 my_email = emails.ApprovalAwaitingEmail(trip, "recommender_1")
#             elif trip.recommender_2 and not trip.recommender_2_approval_date:
#                 # we need to get approval and need to set recommender 2 as who we are waiting on
#                 trip.waiting_on = trip.recommender_2
#                 # project status will be "pending recommendation"
#                 trip.status_id = 12
#                 # build email to recommender 2
#                 my_email = emails.ApprovalAwaitingEmail(trip, "recommender_2")
#
#             elif trip.recommender_3 and not trip.recommender_3_approval_date:
#                 # we need to get approval and need to set recommender 3 as who we are waiting on
#                 trip.waiting_on = trip.recommender_3
#                 # project status will be "pending recommendation"
#                 trip.status_id = 12
#                 # build email to recommender 3
#                 my_email = emails.ApprovalAwaitingEmail(trip, "recommender_3")
#             elif trip.adm and not trip.adm_approval_date:
#                 # we need to get approval and need to set approver as who we are waiting on
#                 trip.waiting_on = trip.adm
#                 # project status will be "pending adm approval"
#                 trip.status_id = 14
#                 # send email to TMS admin
#                 my_email = emails.AdminApprovalAwaitingEmail(trip, "adm")
#             elif trip.rdg and not trip.rdg_approval_date:
#                 # we need to get approval and need to set approver as who we are waiting on
#                 trip.waiting_on = trip.rdg
#                 # project status will be "pending rdg approval"
#                 trip.status_id = 15
#                 # send email to TMS admin
#                 my_email = emails.AdminApprovalAwaitingEmail(trip, "rdg")
#             else:
#                 # project has been fully approved?
#                 trip.status_id = 11
#                 trip.waiting_on = None
#
#             if my_email:
#                 # send the email object
#                 if settings.PRODUCTION_SERVER:
#                     send_mail(message='', subject=my_email.subject, html_message=my_email.message, from_email=my_email.from_email,
#                               recipient_list=my_email.to_list, fail_silently=False, )
#                 else:
#                     print(my_email)
#         else:
#             trip.recommender_1_approval_status_id = 4
#             trip.recommender_2_approval_status_id = 4
#             trip.recommender_3_approval_status_id = 4
#             trip.rdg_approval_status_id = 4
#             trip.adm_approval_status_id = 4
#             trip.recommender_1_approval_date = None
#             trip.recommender_2_approval_date = None
#             trip.recommender_3_approval_date = None
#             trip.rdg_approval_date = None
#             trip.adm_approval_date = None
#             trip.waiting_on = None
#             trip.status_id = 8
