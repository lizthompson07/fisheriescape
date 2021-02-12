from azure.storage.blob import BlockBlobService
from decouple import config
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext as _
from msrestazure.azure_active_directory import MSIAuthentication

from dm_apps.utils import custom_send_mail
from shared_models import models as shared_models
from . import emails
from . import models


def in_travel_admin_group(user):
    if user.id:
        return user.groups.filter(name='travel_admin').count() != 0


def in_adm_admin_group(user):
    if user.id:
        return user.groups.filter(name='travel_adm_admin').count() != 0


def is_admin(user):
    return in_adm_admin_group(user) or in_travel_admin_group(user)


def is_approver(user, trip_request):
    if trip_request.current_reviewer and user == trip_request.current_reviewer.user:
        return True


def is_trip_approver(user, trip):
    if trip.current_reviewer and user == trip.current_reviewer.user:
        return True


def can_modify_request(user, trip_request_id, trip_request_unsubmit=False):
    """
    returns True if user has permissions to delete or modify a request

    The answer of this question will depend on whether the trip is submitted.
    owners cannot edit a submitted trip

    :param user:
    :param trip_request_id:
    :param trip_request_submit: If true, it means this function is being used to answer the question about whether a user can unsubmit a trip
    :return:
    """
    if user.id:
        my_request = models.TripRequest1.objects.get(pk=trip_request_id)

        # check to see if a travel_admin or ADM admin
        if is_admin(user):
            return True

        # check to see if they are the active reviewer
        # determine if this is a child trip or not.
        if get_related_request_reviewers(user).filter(request_id=trip_request_id).exists():
            return True

        # if the project is unsubmitted, the project lead is also able to edit the project... obviously
        # check to see if they are either the owner OR a traveller
        # SPECIAL CASE: sometimes we complete requests on behalf of somebody else.
        if not my_request.submitted and my_request in get_related_requests(user):
            return True

        if trip_request_unsubmit and user == my_request.user:
            return True


def get_section_choices(all=False, full_name=True):
    if full_name:
        my_attr = "full_name"
    else:
        my_attr = _("name")

    if not all:
        return [(s.id, getattr(s, my_attr)) for s in
                shared_models.Section.objects.filter(trip_requests__isnull=False).order_by(
                    "division__branch__region",
                    "division__branch",
                    "division",
                    "name"
                )]
    else:
        return [(s.id, getattr(s, my_attr)) for s in
                shared_models.Section.objects.all()]


def get_division_choices(all=False):
    if all:
        return [(d.id, str(d)) for d in shared_models.Division.objects.all()]
    else:
        return [(d.id, str(d)) for d in
                shared_models.Division.objects.filter(sections__in=shared_models.Section.objects.filter(trip_requests__isnull=False)).distinct()]


def get_region_choices(all=False):
    if all:
        return [(r.id, str(r)) for r in shared_models.Region.objects.all()]
    else:
        # return [(d.id, str(d)) for d in shared_models.Region.objects.all()]
        return [(r.id, str(r)) for r in
                shared_models.Region.objects.filter(branches__divisions__sections__in=shared_models.Section.objects.filter(
                    trip_requests__isnull=False)).distinct()]


def get_trip_reviewers(trip):
    """add reviewers to a trip is adm approval is required. If it isn't, it will remove all reviewers from the trip (if present)"""
    # This section only matters for ADM trips

    if trip.is_adm_approval_required:

        # NCR travel coordinator
        try:
            # add each default NCR coordinator to the queue
            for default_reviewer in models.ReviewerRole.objects.get(pk=3).travel_default_reviewers.order_by("id"):
                models.TripReviewer.objects.get_or_create(trip=trip, user=default_reviewer.user, role=3)
        except (IntegrityError, KeyError):
            pass

        # ADM Approver
        try:
            # add each default ADM approver to the queue
            for default_reviewer in models.ReviewerRole.objects.get(pk=4).travel_default_reviewers.order_by("id"):
                models.TripReviewer.objects.get_or_create(trip=trip, user=default_reviewer.user, role=4)
        except (IntegrityError, KeyError):
            pass

        # ADM Approver
        try:
            # add ADM to the queue
            for default_reviewer in models.ReviewerRole.objects.get(pk=5).travel_default_reviewers.all():
                models.TripReviewer.objects.get_or_create(trip=trip, user=default_reviewer.user, role=5)
        except (IntegrityError, KeyError):
            pass
    else:
        trip.reviewers.all().delete()
    trip.save()


def get_tr_reviewers(trip_request):
    if trip_request.section:
        # section level reviewer
        try:
            # add each default reviewer to the queue
            for default_reviewer in trip_request.section.travel_default_reviewers.all():
                models.Reviewer.objects.get_or_create(request=trip_request, user=default_reviewer.user, role=1)
        except (IntegrityError, KeyError):
            pass

        travellers = trip_request.travellers.filter(user__isnull=False)

        # section level recommender  - only applies if the section head is not a traveller
        try:
            # if the division head is the one creating the request, the section head should be skipped as a recommender AND
            # if the section head is the one creating the request, they should be skipped as a recommender
            if trip_request.section.head not in [t.user for t in travellers] and trip_request.section.division.head not in [t.user for t in travellers]:
                models.Reviewer.objects.get_or_create(request=trip_request, user=trip_request.section.head, role=2, )
        except (IntegrityError, AttributeError):
            pass

        # division level recommender  - only applies if the division head is not a traveller
        try:
            # if the division head is the one creating the request, they should be skipped as a recommender
            if trip_request.section.division.head not in [t.user for t in travellers]:
                models.Reviewer.objects.get_or_create(request=trip_request, user=trip_request.section.division.head, role=2, )
        except (IntegrityError, AttributeError):
            pass

        # branch level reviewer  - only applies if the branch head is not a traveller
        try:
            if trip_request.section.division.branch.head not in [t.user for t in travellers]:
                # add each default reviewer to the queue
                for default_reviewer in trip_request.section.division.branch.travel_default_reviewers.all():
                    models.Reviewer.objects.get_or_create(request=trip_request, user=default_reviewer.user, role=1)

        except (IntegrityError, AttributeError, User.DoesNotExist):
            pass

        # Branch level recommender  - only applies if this is not the RDS
        try:
            if trip_request.section.division.branch.head not in [t.user for t in travellers]:
                models.Reviewer.objects.get_or_create(request=trip_request, user=trip_request.section.division.branch.head, role=2, )
        except (IntegrityError, AttributeError, User.DoesNotExist):
            pass

    # should the ADMs office be involved?
    if trip_request.trip.is_adm_approval_required:
        try:
            adm = User.objects.get(email__icontains="arran.mcpherson@dfo-mpo.gc.ca")
            models.Reviewer.objects.get_or_create(request=trip_request, user=adm, role=5, )  # Arran McPherson
        except (IntegrityError, AttributeError, User.DoesNotExist):
            pass

    # finally, we always need to add the RDG
    try:
        models.Reviewer.objects.get_or_create(request=trip_request, user=trip_request.section.division.branch.region.head, role=6, )
    except (IntegrityError, AttributeError, User.DoesNotExist):
        pass

    trip_request.save()


def start_review_process(trip_request):
    """this should be used when a trip is submitted. It will change over all reviewers' statuses to Pending"""
    # focus only on reviewers that are status = Not Submitted
    for reviewer in trip_request.reviewers.all():
        # set everyone to being queued
        reviewer.status = 20
        reviewer.status_date = None
        reviewer.save()


def end_review_process(trip_request):
    """this should be used when a project is unsubmitted. It will change over all reviewers' statuses to Pending"""
    # focus only on reviewers that are status = Not Submitted
    for reviewer in trip_request.reviewers.all():
        reviewer.status = 4
        reviewer.status_date = None
        reviewer.comments = None
        reviewer.save()


def start_trip_review_process(trip, reset=False):
    """this should be used when a project is submitted. It will change over all reviewers' statuses to Pending
        set the `reset` arg to True is this is being used in the context of restarting a review process
    """
    # focus only on reviewers that are status = Not Submitted
    if not reset:
        trip.review_start_date = timezone.now()
        trip.status = 31
        trip.save()

    for reviewer in trip.reviewers.all():
        # set everyone to being queued
        reviewer.status = 24
        if not reset:
            reviewer.status_date = None
        reviewer.save()


def end_trip_review_process(trip, reset=False):
    """this should be used when a project is unsubmitted. It will change over all reviewers' statuses to Pending
    set the `reset` arg to True is this is being used in the context of restarting a review process
    """
    # focus only on reviewers that are status = Not Submitted
    if not reset:
        # trip.review_start_date = None NEVER reset the review start date!
        trip.status = 41
    else:
        trip.status = 31
    trip.save()

    for reviewer in trip.reviewers.all():
        if not reset:
            reviewer.status = 23
            reviewer.status_date = None
            reviewer.comments = None
        else:
            reviewer.status = 24
        reviewer.save()


def reset_trip_review_process(trip):
    """To be used if a trip reviewer finds modifications that are required and wants to restart the review process. COMMENTS ARE SAVED"""
    # focus only on reviewers that are status = Not Submitted
    end_trip_review_process(trip, reset=True)
    start_trip_review_process(trip, reset=True)


def __set_request_status__(trip_request, request):
    """
    IF POSSIBLE, THIS SHOULD ONLY BE CALLED BY THE approval_seeker() function.
    This will look at the reviewers and decide on  what the project status should be. Will return False if trip_request is denied or if trip_request is not submitted
    """

    # first order of business, if the trip_request is status "changes requested' do not continue
    if trip_request.status == 16:
        return False

    # Next: if the trip_request is unsubmitted, it is in 'draft' status
    elif not trip_request.submitted:
        trip_request.status = 8
        # don't stick around any longer. save the trip_request and leave exit the function
        trip_request.save()
        return False

    else:
        # if someone denied it at any point, the trip_request is 'denied' and all subsequent reviewers are set to "cancelled"
        is_denied = False
        for reviewer in trip_request.reviewers.all():
            # if is_denied, all subsequent reviewer statuses should be set to "cancelled"
            if is_denied:
                reviewer.status = 5
                reviewer.save()

            # if reviewer status is denied, set the is_denied var to true
            if reviewer.status == 3:
                is_denied = True

        if is_denied:
            trip_request.status = 10
            trip_request.save()
            # send an email to the trip_request owner
            email = emails.StatusUpdateEmail(trip_request, request)
            # # send the email object
            custom_send_mail(
                subject=email.subject,
                html_message=email.message,
                from_email=email.from_email,
                recipient_list=email.to_list
            )

            # don't stick around any longer. save the trip_request and leave exit the function
            return False

        # The trip_request should be approved if everyone has approved it. HOWEVER, some reviewers might have been skipped
        # The total number of reviewers should equal the number of reviewer who approved [id=2] and / or were skipped [id=21].
        elif trip_request.reviewers.all().count() == trip_request.reviewers.filter(status__in=[2, 21]).count():
            trip_request.status = 11
            trip_request.save()
            # send an email to the trip_request owner
            email = emails.StatusUpdateEmail(trip_request, request)
            # # send the email object
            custom_send_mail(
                subject=email.subject,
                html_message=email.message,
                from_email=email.from_email,
                recipient_list=email.to_list
            )
            # don't stick around any longer. save the trip_request and leave exit the function
            return False
        else:
            for reviewer in trip_request.reviewers.all():
                # if a reviewer's status is 'pending', we are waiting on them and the project status should be set accordingly.
                if reviewer.status == 1:
                    # if role is 'reviewer'
                    if reviewer.role == 1:
                        trip_request.status = 17
                    # if role is 'recommender'
                    elif reviewer.role == 2:
                        trip_request.status = 12
                    # if role is 'ncr reviewer'
                    elif reviewer.role == 3:
                        trip_request.status = 17
                    # if role is 'ncr recommender'
                    elif reviewer.role == 4:
                        trip_request.status = 12
                    # if role is 'adm'
                    elif reviewer.role == 5:
                        trip_request.status = 14
                    # if role is 'rdg'
                    elif reviewer.role == 6:
                        trip_request.status = 15

    trip_request.save()
    return True


def approval_seeker(trip_request, suppress_email=False, request=None):
    """
    This method is meant to seek approvals via email + set reveiwer statuses.
    It will also set the trip_request status vis a vis __set_request_status__()

    """

    # start by setting the trip_request status... if the trip_request is "denied" OR "draft" or "approved", do not continue
    if __set_request_status__(trip_request, request):
        next_reviewer = None
        email = None
        for reviewer in trip_request.reviewers.all():
            # if the reviewer's status is set to 'queued', they will be our next selection
            # we should then exit the loop and set the next_reviewer var

            # if this is a resubmission, there might still be a reviewer whose status is 'pending'. This should be the reviewer
            if reviewer.status == 20 or reviewer.status == 1:
                next_reviewer = reviewer
                break

        # if there is a next reviewer, set their status to pending
        if next_reviewer:
            next_reviewer.status = 1
            next_reviewer.status_date = timezone.now()
            next_reviewer.save()

            # now, depending on the role of this reviewer, perhaps we want to send an email.
            # if they are a recommender, rev...
            if next_reviewer.role in [1, 2, 3, 4, ] and request:  # essentially, just not the RDG or ADM
                email = emails.ReviewAwaitingEmail(trip_request, next_reviewer, request)

            elif next_reviewer.role in [6, ] and request:  # if we are going for RDG signature...
                email = emails.AdminApprovalAwaitingEmail(trip_request, next_reviewer.role, request)

            if email and not suppress_email:
                # send the email object
                custom_send_mail(
                    subject=email.subject,
                    html_message=email.message,
                    from_email=email.from_email,
                    recipient_list=email.to_list
                )

            # Then, lets set the trip_request status again to account for the fact that something happened
            __set_request_status__(trip_request, request)


def populate_trip_request_costs(request, trip_request):
    # determine if we are dealing with a child trip request - used to prepopulate number of days
    if trip_request.parent_request:
        trip = trip_request.parent_request.trip
    else:
        trip = trip_request.trip

    for obj in models.Cost.objects.all():
        new_item, created = models.TripRequestCost.objects.get_or_create(
            trip_request=trip_request,
            cost=obj,
            # number_of_days=trip.number_of_days,
        )
        if created:
            # breakfast
            if new_item.cost_id == 9:
                try:
                    new_item.rate_cad = models.NJCRates.objects.get(pk=1).amount
                    new_item.save()
                except models.NJCRates.DoesNotExist:
                    messages.warning(request,
                                     _("NJC rates for breakfast missing from database. Please let your system administrator know."))
            # lunch
            elif new_item.cost_id == 10:
                try:
                    new_item.rate_cad = models.NJCRates.objects.get(pk=2).amount
                    new_item.save()
                except models.NJCRates.DoesNotExist:
                    messages.warning(request, _("NJC rates for lunch missing from database. Please let your system administrator know."))
            # supper
            elif new_item.cost_id == 11:
                try:
                    new_item.rate_cad = models.NJCRates.objects.get(pk=3).amount
                    new_item.save()
                except models.NJCRates.DoesNotExist:
                    messages.warning(request, _("NJC rates for supper missing from database. Please let your system administrator know."))
            # incidentals
            elif new_item.cost_id == 12:
                try:
                    new_item.rate_cad = models.NJCRates.objects.get(pk=4).amount
                    new_item.save()
                except models.NJCRates.DoesNotExist:
                    messages.warning(request,
                                     _("NJC rates for incidentals missing from database. Please let your system administrator know."))

    # messages.success(request, _("All costs have been added to this project."))


def clear_empty_trip_request_costs(trip_request):
    for obj in models.Cost.objects.all():
        for cost in models.TripRequestCost.objects.filter(trip_request=trip_request, cost=obj):
            if (cost.amount_cad is None or cost.amount_cad == 0):
                cost.delete()


def manage_trip_warning(trip, request):
    """
    This function will decide if sending an email to NCR is necessary based on
    1) the total costs accrued for a trip
    2) whether or not a warning has already been sent

    :param trip: an instance of Trip
    :return: NoneObject
    """

    # first make sure we are not receiving a NoneObject
    try:
        trip.non_res_total_cost
    except AttributeError:
        pass
    else:

        # If the trip cost is below 10k, make sure the warning field is null and an then do nothing more :)
        if trip.non_res_total_cost < 10000:
            if trip.cost_warning_sent:
                trip.cost_warning_sent = None
                trip.save()

        # if the trip is >= 10K, we simply need to send an email to NCR
        else:
            if not trip.cost_warning_sent:
                email = emails.TripCostWarningEmail(trip, request)
                # # send the email object
                custom_send_mail(
                    subject=email.subject,
                    html_message=email.message,
                    from_email=email.from_email,
                    recipient_list=email.to_list
                )
                trip.cost_warning_sent = timezone.now()
                trip.save()


def __set_trip_status__(trip):
    """
    IF POSSIBLE, THIS SHOULD ONLY BE CALLED BY THE approval_seeker() function.
    This will look at the reviewers and decide on  what the project status should be. Will return False if trip_request is denied or if trip_request is not submitted
    Will return False if there are no reviewers left to seek
    """
    pass


def trip_approval_seeker(trip, request):
    """
    This method is meant to seek approvals via email + set reviewer statuses.
    """

    # start by setting the trip status... if the trip_request is "denied" OR "draft" or "approved", do not continue
    # Next: if the trip_request is un submitted, it is in 'draft' status

    # only look for a next reviewer if we are still in a review [id=31]
    if trip.status == 31:

        next_reviewer = None
        email = None

        # look through all the reviewers... see if we can decide on who the next reviewer should be...
        for reviewer in trip.reviewers.all():
            # if the reviewer's status is set to 'queued', they will be our next selection
            # we should then exit the loop and set the next_reviewer var
            # CAVEAT: if this is a resubmission, there might still be a reviewer whose status is 'pending'. This should be the reviewer
            if reviewer.status == 24 or reviewer.status == 25:
                next_reviewer = reviewer
                break

        # if there is a next reviewer, set their status to pending and send them an email
        if next_reviewer:
            next_reviewer.status = 25
            next_reviewer.status_date = timezone.now()
            next_reviewer.save()

            email = emails.TripReviewAwaitingEmail(trip, next_reviewer, request)

            # send the email object
            custom_send_mail(
                subject=email.subject,
                html_message=email.message,
                from_email=email.from_email,
                recipient_list=email.to_list
            )


        # if no next reviewer was found, the trip's review is complete...
        else:
            # THIS IS PROBABLY NOT NECESSARY.

            # The trip review is complete if all the reviewers' status are set to complete [id=26]
            # HOWEVER, some reviewers might have been skipped
            # The total number of reviewers should equal the number of reviewer who completed [id=26] and / or were skipped [id=42].
            if trip.reviewers.all().count() == trip.reviewers.filter(status__in=[26, 42]).count():
                trip.status = 32
                trip.save()


# DELETE!!
def get_related_trips(user):
    """give me a user and I'll send back a queryset with all related trips, i.e.
     they are the request.user | they are the request.created_by | they are a traveller on a child trip"""

    # all individual or group requests where user =user (this should include parent requests)
    tr_ids = [tr.id for tr in models.TripRequest.objects.filter(parent_request__isnull=True, user=user)]
    # all trips that were created by user
    tr_ids.extend([tr.id for tr in models.TripRequest.objects.filter(parent_request__isnull=True, created_by=user)])
    # all trips where the user is a traveller on a group trip
    tr_ids.extend([tr.parent_request.id for tr in models.TripRequest.objects.filter(parent_request__isnull=False, user=user)])
    return models.TripRequest.objects.filter(id__in=tr_ids)


def get_related_requests(user):
    """give me a user and I'll send back a queryset with all related trip requests, i.e.
     they are a traveller || they are the request.created_by"""
    qs = models.TripRequest1.objects.filter(Q(created_by=user) | Q(travellers__user=user)).distinct()
    return qs


def get_related_request_reviewers(user):
    """give me a user and I'll send back a queryset with all related trips request reviews that are actionable (pending)
     (excluding drafts (8), ADM approval (14) and when changes have already been requested (16)"""
    qs = models.Reviewer.objects.filter(status=1).filter(~Q(request__status__in=[16, 14, 8]), user=user).distinct()
    return qs


def get_trip_reviews(user):
    """give me a user and I'll send back a queryset with all related trips reviews that are actionable (pending = 25)"""
    qs = models.TripReviewer.objects.filter(status=25, user=user)
    return qs


def get_adm_eligible_trips():
    """returns a qs of trips that are ready for adm review"""
    # start with trips that need adm approval that have not already been reviewed or those that have been cancelled
    trips = models.Conference.objects.filter(is_adm_approval_required=True).filter(~Q(status__in=[32, 43, 31]))

    t_ids = list()
    for t in trips:
        # only get trips that have attached requests
        if t.get_connected_active_requests().count():
            # only get trips that are within three months from the closest date
            if t.date_eligible_for_adm_review and t.date_eligible_for_adm_review <= timezone.now():
                t_ids.append(t.id)
    return models.Conference.objects.filter(id__in=t_ids)


user_attr_list = [
    "shared_models_regions",
    "shared_models_admin_regions",
    "shared_models_branches",
    "shared_models_admin_branches",
    "shared_models_divisions",
    "shared_models_admin_divisions",
    "shared_models_sections",
    "shared_models_admin_sections",
]


def is_manager_or_assistant_or_admin(user):
    # start high and go low
    if is_admin(user):
        return True

    for attr in user_attr_list:
        if getattr(user, attr).exists():
            return True


def get_requests_with_managerial_access(user):
    queryset = models.TripRequest1.objects.all()
    if in_travel_admin_group(user) or in_adm_admin_group(user):
        return queryset
    else:
        return queryset.filter(Q(section__admin=user) | Q(section__head=user)
                               | Q(section__division__admin=user) | Q(section__division__head=user)
                               | Q(section__division__branch__admin=user) | Q(section__division__branch__head=user)
                               | Q(section__division__branch__region__admin=user) | Q(section__division__branch__region__head=user))


def upload_to_azure_blob(target_file_path, target_file):
    AZURE_STORAGE_ACCOUNT_NAME = settings.AZURE_STORAGE_ACCOUNT_NAME
    AZURE_MSI_CLIENT_ID = config("AZURE_MSI_CLIENT_ID", cast=str, default="")
    account_key = config("AZURE_STORAGE_SECRET_KEY", default=None)
    try:
        token_credential = MSIAuthentication(resource=f'https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net', client_id=AZURE_MSI_CLIENT_ID)
    except Exception as E:
        print(E)
        token_credential = None
    blobService = BlockBlobService(account_name=AZURE_STORAGE_ACCOUNT_NAME, token_credential=token_credential, account_key=account_key)
    blobService.create_blob_from_path('media', target_file, target_file_path)


def get_request_field_list(tr=None, user=None):
    my_list = [
        'fiscal_year',
        'created_by',
        'trip',
        'traveller_count|{}'.format(_("number of travellers (this request)")),
        'status_string|{}'.format(_("Request status")),
        'section',
        'objective_of_event',
        'benefit_to_dfo',
        'bta_attendees',
        'total_request_cost|{}'.format(_("Total costs")),
        'total_non_dfo_funding|{}'.format(_("Total amount of non-DFO funding (CAD)")),
        'total_dfo_funding|{}'.format(_("Total amount of DFO funding (CAD)")),
        'total_non_dfo_funding_sources|{}'.format(_("Non-DFO funding sources")),
        'funding_source',
        'original_submission_date',
        'processing_time|{}'.format(_("Processing time")),
        'notes',
        'late_justification' if not tr or (tr and tr.is_late_request) else None,
    ]

    while None in my_list: my_list.remove(None)
    return my_list

def get_traveller_field_list():
    my_list = [
        'is_public_servant',
        'is_research_scientist|{}'.format(_("Is research scientist?")),
        'dates|{}'.format(_("dates of travel")),
        'departure_location',
        'role',
        'role_of_participant',
        'learning_plan',
        'cost_breakdown_html|{}'.format(_("cost breakdown:")),
    ]
    while None in my_list: my_list.remove(None)
    return my_list
