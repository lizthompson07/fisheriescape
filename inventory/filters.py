# from accounts import models as account_models
from django.contrib.auth.models import User
from django import forms
from . import models
import django_filters

class ResourceFilter(django_filters.FilterSet):
    # generate a list of people from inventory.people
    person_list = []
    for p in models.Person.objects.all():
        person_list.append(p.user_id)

    PEOPLE_CHOICES = []
    for u in User.objects.all().order_by("last_name","first_name"):
        if u.id in person_list:
            PEOPLE_CHOICES.append((u.id,"{}, {}".format(u.last_name,u.first_name)))

    person = django_filters.ChoiceFilter(field_name="people", label = "Person", lookup_expr='exact', choices=PEOPLE_CHOICES)

    class Meta:
        model = models.Resource
        fields = {
            'title_eng':['icontains'],
            'status':['exact'],
            'section':['exact'],
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["title_eng__icontains"].label = "Title (English)"

        self.filters["status"].widget= forms.Select(attrs={'style':"width: 10em"})


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
