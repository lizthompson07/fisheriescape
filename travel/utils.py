from django.conf import settings
from django.core.mail import send_mail
from django.db import IntegrityError
from django.utils import timezone

from . import models
from . import emails


def get_reviewers(trip):
    # assuming there is a section, assign amelie and section management
    if trip.section:
        # if in gulf region, add Amelie as a reviewer
        if trip.section.division.branch.region_id == 1:
            try:
                models.Reviewer.objects.create(trip=trip, user_id=385, role_id=1, )
            except IntegrityError:
                print("not adding amelie")

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
    if trip.conference:
        if trip.conference.is_adm_approval_required:
            # add the ADMs office staff
            # try:
            #     models.Reviewer.objects.create(trip=trip, user_id=749, role_id=3, )  # Kim Cotton
            # except IntegrityError:
            #     print("not adding NCR reviewer")
            # try:
            #     models.Reviewer.objects.create(trip=trip, user_id=736, role_id=4, )  # Andy White
            # except IntegrityError:
            #     print("not adding NCR recommender")
            # try:
            #     models.Reviewer.objects.create(trip=trip, user_id=758, role_id=4, )  # Stephen Virc
            # except IntegrityError:
            #     print("not adding NCR recommender")
            # try:
            #     models.Reviewer.objects.create(trip=trip, user_id=740, role_id=4, )  # Wayne Moore
            # except IntegrityError:
            #     print("not adding NCR recommender")
            try:
                models.Reviewer.objects.create(trip=trip, user_id=626, role_id=5, )  # Arran McPherson
            except IntegrityError:
                print("not adding NCR ADM")

    # finally, we always need to add the RDG
    try:
        models.Reviewer.objects.create(trip=trip, user=trip.section.division.branch.region.head, role_id=6, )
    except (IntegrityError, AttributeError):
        print("not adding RDG")

    trip.save()


def start_review_process(trip):
    """this should be used when a project is submitted. It will change over all reviewers' statuses to Pending"""
    # focus only on reviewers that are status = Not Submitted
    for reviewer in trip.reviewers.all():
        # set everyone to being queued
        reviewer.status_id = 20
        reviewer.status_date = timezone.now()
        reviewer.save()


def end_review_process(trip):
    """this should be used when a project is unsubmitted. It will change over all reviewers' statuses to Pending"""
    # focus only on reviewers that are status = Not Submitted
    for reviewer in trip.reviewers.all():
        reviewer.status_id = 4
        reviewer.status_date = timezone.now()
        reviewer.comments = None
        reviewer.save()


def set_trip_status(trip):
    """
    IF POSSIBLE, THIS SHOULD ONLY BE CALLED BY THE approval_seeker() function.
    This will look at the reviewers and decide on  what the project status should be. Will return False if trip is denied or if trip is not submitted
    """

    # first order of business, if the trip is status "changes requested' do not continue
    if trip.status_id == 16:
        return False

    # Next: if the trip is unsubmitted, it is in 'draft' status
    elif not trip.submitted:
        trip.status_id = 8
        # don't stick around any longer. save the trip and leave exit the function
        trip.save()
        return False

    else:
        # if someone denied it at any point, the trip is 'denied' and all subsequent reviewers are set to "cancelled"
        is_denied = False
        for reviewer in trip.reviewers.all():
            # if reviewer status is denied, set the is_denied var to true
            if reviewer.status_id == 3:
                is_denied = True
            # if is_denied, all subsequent reviewer statuses should be set to "cancelled"
            if is_denied:
                reviewer.status_id = 5
                reviewer.save()
        if is_denied:
            trip.status_id = 10
            trip.save()
            # send an email to the trip owner
            my_email = emails.StatusUpdateEmail(trip)
            # # send the email object
            if settings.PRODUCTION_SERVER:
                send_mail(message='', subject=my_email.subject, html_message=my_email.message, from_email=my_email.from_email,
                          recipient_list=my_email.to_list, fail_silently=False, )
            else:
                print(my_email)

            # don't stick around any longer. save the trip and leave exit the function
            return False

        # The trip should be approved if everyone has approved it. HOWEVER, some reviewers might have been skipped
        # The total number of reviewers should equal the number of reviewer who approved [id=2] and / or were skipped [id=21].
        elif trip.reviewers.all().count() == trip.reviewers.filter(status_id__in=[2, 21]).count():
            trip.status_id = 11
            trip.save()
            # send an email to the trip owner
            my_email = emails.StatusUpdateEmail(trip)
            # # send the email object
            if settings.PRODUCTION_SERVER:
                send_mail(message='', subject=my_email.subject, html_message=my_email.message, from_email=my_email.from_email,
                          recipient_list=my_email.to_list, fail_silently=False, )
            else:
                print(my_email)
            # don't stick around any longer. save the trip and leave exit the function
            return False
        else:
            for reviewer in trip.reviewers.all():
                # if a reviewer's status is 'pending', we are waiting on them and the project status should be set accordingly.
                if reviewer.status_id == 1:
                    # if role is 'reviewer'
                    if reviewer.role_id == 1:
                        trip.status_id = 17
                    # if role is 'recommender'
                    elif reviewer.role_id == 2:
                        trip.status_id = 12
                    # if role is 'ncr reviewer'
                    elif reviewer.role_id == 3:
                        trip.status_id = 18
                    # if role is 'ncr recommender'
                    elif reviewer.role_id == 4:
                        trip.status_id = 19
                    # if role is 'adm'
                    elif reviewer.role_id == 5:
                        trip.status_id = 14
                    # if role is 'rdg'
                    elif reviewer.role_id == 6:
                        trip.status_id = 15

    trip.save()
    return True


def approval_seeker(trip):
    """
    This method is meant to seek approvals via email + set reveiwer statuses.
    It will also set the trip status vis a vis set_trip_status()

    """

    # start by setting the trip status... if the trip is "denied" OR "draft" or "approved", do not continue
    if set_trip_status(trip):
        next_reviewer = None
        my_email = None
        for reviewer in trip.reviewers.all():
            # if the reviewer's status is set to 'queued', they will be our next selection
            # we should then exit the loop and set the next_reviewer var

            # if this is a resubmission, there might still be a reviewer whose status is 'pending'. This should be the reviewer
            if reviewer.status_id == 20 or reviewer.status_id == 1:
                next_reviewer = reviewer
                break

        # if there is a next reviewer, set their status to pending
        if next_reviewer:
            next_reviewer.status_id = 1
            next_reviewer.save()

            # now, depending on the role of this reviewer, perhaps we want to send an email.
            # if they are a recommender, rev...
            if next_reviewer.role_id in [1, 2, 3, 4, ]:  # essentially, just not the RDG or ADM
                my_email = emails.ReviewAwaitingEmail(trip, next_reviewer)

            elif next_reviewer.role_id in [5, 6]:  # if we are going for RDG signature...
                my_email = emails.AdminApprovalAwaitingEmail(trip)

            if my_email:
                # send the email object
                if settings.PRODUCTION_SERVER:
                    send_mail(message='', subject=my_email.subject, html_message=my_email.message, from_email=my_email.from_email,
                              recipient_list=my_email.to_list, fail_silently=False, )
                else:
                    print(my_email)

            # Then, lets set the trip status again to account for the fact that something happened
            set_trip_status(trip)
