import django_filters
from . import models

class BugFilter(django_filters.FilterSet):
    class Meta:
        model = models.Bug
        fields = {
            'application': ['exact'],
            'subject': ['icontains'],
            'importance': ['exact'],
            'resolved':['exact'],
        }

    
