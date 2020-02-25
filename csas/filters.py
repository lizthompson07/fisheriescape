from django_filters import FilterSet

from . import models


class ContactFilter(FilterSet):
    class Meta:
        model = models.ConContact
        fields = ['last_name', 'first_name', 'contact_type']


class MeetingFilter(FilterSet):
    class Meta:
        model = models.MetMeeting
        fields = ['quarter', 'title_en', 'title_fr']
