import django_filters
from . import models

class TicketFilter(django_filters.FilterSet):
    class Meta:
        model = models.Ticket
        fields = {
            'id': ['exact'],
            'title': ['icontains'],
            'status': ['exact'],
            'section': ['exact'],
            'people':['exact'],
            'tags':['exact']
        }

class PersonFilter(django_filters.FilterSet):
    class Meta:
        model = models.Person
        fields = {
            'first_name': ['icontains'],
            'last_name': ['icontains'],

        }

class TagFilter(django_filters.FilterSet):
    class Meta:
        model = models.Tag
        fields = {
            'tag': ['icontains'],
        }
