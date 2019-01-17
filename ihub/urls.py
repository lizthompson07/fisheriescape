from django.urls import path
from . import views

app_name = 'ihub'

urlpatterns = [
    path('close/', views.CloserTemplateView.as_view(), name="close_me"),
    path('', views.IndexTemplateView.as_view(), name="index"),

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

    # # Collaborator #
    # ################
    # path('project/<int:project>/collaborator/new/', views.CollaboratorCreateView.as_view(), name="collab_new"),
    # path('collaborator/<int:pk>/edit/', views.CollaboratorUpdateView.as_view(), name="collab_edit"),
    # path('collaborator/<int:pk>/delete/', views.collaborator_delete, name="collab_delete"),

    # # Collaborative Agreements #
    # ############################
    # path('project/<int:project>/agreement/new/', views.AgreementCreateView.as_view(), name="agreement_new"),
    # path('agreement/<int:pk>/edit/', views.AgreementUpdateView.as_view(), name="agreement_edit"),
    # path('agreement/<int:pk>/delete/', views.agreement_delete, name="agreement_delete"),

    # # O&M COST #
    # ############
    # path('project/<int:project>/om-cost/new/', views.OMCostCreateView.as_view(), name="om_new"),
    # path('om-cost/<int:pk>/edit/', views.OMCostUpdateView.as_view(), name="om_edit"),
    # path('om-cost/<int:pk>/delete/', views.om_cost_delete, name="om_delete"),

    # # CAPITAL COST #
    # ################
    # path('project/<int:project>/capital-cost/new/', views.CapitalCostCreateView.as_view(), name="capital_new"),
    # path('capital-cost/<int:pk>/edit/', views.CapitalCostUpdateView.as_view(), name="capital_edit"),
    # path('capital-cost/<int:pk>/delete/', views.capital_cost_delete, name="capital_delete"),

    # # G&C COST #
    # ############
    # path('project/<int:project>/gc-cost/new/', views.GCCostCreateView.as_view(), name="gc_new"),
    # path('gc-cost/<int:pk>/edit/', views.GCCostUpdateView.as_view(), name="gc_edit"),
    # path('gc-cost/<int:pk>/delete/', views.gc_cost_delete, name="gc_delete"),

]
