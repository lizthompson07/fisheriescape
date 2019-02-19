# from accounts import models as account_models
from django.contrib.auth.models import User
from django import forms
from . import models
import django_filters


class ResourceFilter(django_filters.FilterSet):
    # generate a list of people from inventory.people
    person_list = []

    person_list = [p.user_id for p in models.Person.objects.all()]
    PEOPLE_CHOICES = []
    for u in User.objects.all().order_by("last_name", "first_name"):
        if u.id in person_list:
            PEOPLE_CHOICES.append((u.id, "{}, {}".format(u.last_name, u.first_name)))

    STATUS_CHOICES = [(s.id, str(s)) for s in models.Status.objects.all()]
    SECTION_CHOICES = [(s.id, str(s)) for s in models.Section.objects.all()]

    search_term = django_filters.CharFilter(field_name='search_term', label="Search term", lookup_expr='icontains',
                                            widget=forms.TextInput())
    region = django_filters.ChoiceFilter(field_name="section__region", label="Region", lookup_expr='exact',
                                          choices=models.Section.REGION_CHOICES)
    section = django_filters.ChoiceFilter(field_name="section", label="Section", lookup_expr='exact',
                                          choices=SECTION_CHOICES)
    person = django_filters.ChoiceFilter(field_name="people", label="Person", lookup_expr='exact',
                                         choices=PEOPLE_CHOICES)
    status = django_filters.ChoiceFilter(field_name="status", label="Status", lookup_expr='exact',
                                         choices=STATUS_CHOICES)


class PersonFilter(django_filters.FilterSet):
    class Meta:
        model = models.Person
        fields = {
            'full_name': ['icontains'],
        }


class KeywordFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(label="Keyword Search Term", lookup_expr='icontains')


class CitationFilter(django_filters.FilterSet):
    search_term = django_filters.CharFilter(label="Citation Search Term", lookup_expr='icontains')
