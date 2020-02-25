from django_filters import FilterSet

from . import models


class ContactFilter(FilterSet):
    class Meta:
        model = models.ConContact
        fields = ['last_name', 'first_name', 'contact_type']
