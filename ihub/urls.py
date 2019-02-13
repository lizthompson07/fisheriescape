from django.urls import path
from . import views

app_name = 'ihub'

urlpatterns = [
    path('close/', views.CloserTemplateView.as_view(), name="close_me"),
    path('', views.IndexTemplateView.as_view(), name="index"),

    # ORGANIZATION #
    ################
    path('organizations/', views.OrganizationListView.as_view(), name="org_list"),
    path('organization/new/', views.OrganizationCreateView.as_view(), name="org_new"),
    path('organization/<int:pk>/edit/', views.OrganizationUpdateView.as_view(), name="org_edit"),
    path('organization/<int:pk>/delete/', views.OrganizationDeleteView.as_view(), name="org_delete"),

    # # Entry #
    # #########
    path('entries/', views.EntryListView.as_view(), name="entry_list"),
    path('entry/new/', views.EntryCreateView.as_view(), name="entry_new"),
    path('entry/<int:pk>/view', views.EntryDetailView.as_view(), name="entry_detail"),
    path('entry/<int:pk>/edit', views.EntryUpdateView.as_view(), name="entry_edit"),
    path('entry/<int:pk>/delete', views.EntryDeleteView.as_view(), name="entry_delete"),

    # NOTES #
    #########
    path('entry/<int:entry>/note/new/', views.NoteCreateView.as_view(), name="note_new"),
    path('note/<int:pk>/edit/', views.NoteUpdateView.as_view(), name="note_edit"),
    path('note/<int:pk>/delete/', views.note_delete, name="note_delete"),

    # ENTRYPERSON #
    ###############
    path('entry/<int:entry>/person/new/', views.EntryPersonCreateView.as_view(), name="ep_new"),
    path('dfo-person/<int:pk>/edit/', views.EntryPersonUpdateView.as_view(), name="ep_edit"),
    path('dfo-person/<int:pk>/delete/', views.entry_person_delete, name="ep_delete"),

    # FILE #
    ########
    path('entry/<int:entry>/file/new/', views.FileCreateView.as_view(), name="file_new"),
    path('file/<int:pk>/edit/', views.FileUpdateView.as_view(), name="file_edit"),
    path('file/<int:pk>/delete/', views.file_delete, name="file_delete"),

    # Reports #
    ###########
    path('reports/search/', views.ReportSearchFormView.as_view(), name="report_search"),
    path('reports/capacity-report/fy/<str:fy>/orgs/<str:orgs>/', views.capacity_export_spreadsheet, name="capacity_xlsx"),
    path('reports/capacity-report/', views.capacity_export_spreadsheet, name="capacity_xlsx"),
    path('reports/capacity-report/fy/<str:fy>/', views.capacity_export_spreadsheet, name="capacity_xlsx"),
    path('reports/capacity-report/orgs/<str:orgs>/', views.capacity_export_spreadsheet, name="capacity_xlsx"),

    # path('reports/<str:species_list>/species-count/', views.report_species_count, name="species_report"),
    # path('reports/species-richness/', views.report_species_richness, name="species_richness"),
    # path('reports/species-richness/site/<int:site>/', views.report_species_richness, name="species_richness"),
    # path('reports/annual-watershed-report/site/<int:site>/year/<int:year>',
    #      views.AnnualWatershedReportTemplateView.as_view(), name="watershed_report"),
    # path('reports/fgp-csv-export/', views.fgp_export, name="watershed_csv"),

]
