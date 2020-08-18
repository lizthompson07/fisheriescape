import django_tables2 as tables
from . import models

class OrganizationListTable(tables.Table):
    legal_name = tables.Column(accessor='legal_name', verbose_name='Name', order_by=('legal_name'), linkify=True)
    location = tables.Column(accessor='location_long', verbose_name='Location', order_by=('country', 'province', 'city'))
    class Meta:
        model = models.Organization
        fields = ('legal_name', 'phone_number', 'location', 'organization_type')
        attrs = {"class": 'table table-hover'}
        template_name = "engagements/table_organizations_list.html"