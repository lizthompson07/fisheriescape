import django_tables2 as tables

from .models import Organization, Individual

class OrganizationListTable(tables.Table):
    legal_name = tables.Column(accessor='legal_name', verbose_name='Name', order_by=('legal_name'), linkify=True)
    location = tables.Column(accessor='location_long', verbose_name='Location', order_by=('country', 'province', 'city'))
    class Meta:
        model = Organization
        fields = ('legal_name', 'phone_number', 'location', 'stakeholder_type')
        attrs = {"class": 'table table-hover'}
        template_name = "engagements/table_object_list.html"

class IndividualListTable(tables.Table):
    full_name = tables.Column(accessor='full_name', verbose_name='Name', order_by=('last_name', 'first_name'),
                              linkify=True)
    class Meta:
        model = Individual
        fields = ('full_name', 'organization', 'title', 'email_address', 'phone_number',)
        attrs = {'class': 'table table-hover'}
        template_name = "engagements/table_object_list.html"