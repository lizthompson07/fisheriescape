from django.urls import path
from . import views

app_name = 'scifi'

urlpatterns = [
    path('close/', views.CloserTemplateView.as_view(), name="close_me"),
    path('', views.IndexTemplateView.as_view(), name="index"),

    # ALLOTMENT CODE #
    ##################
    path('allotment-codes/', views.AllotmentCodeListView.as_view(), name="allotment_list"),
    path('allotment-code/new/', views.AllotmentCodeCreateView.as_view(), name="allotment_new"),
    path('allotment-code/<int:pk>/edit/', views.AllotmentCodeUpdateView.as_view(), name="allotment_edit"),
    path('allotment-code/<int:pk>/delete/', views.AllotmentCodeDeleteView.as_view(), name="allotment_delete"),

    # BUSINESS LINE #
    #################
    path('business-lines/', views.BusinessLineListView.as_view(), name="business_list"),
    path('business-line/new/', views.BusinessLineCreateView.as_view(), name="business_new"),
    path('business-line/<int:pk>/edit/', views.BusinessLineUpdateView.as_view(), name="business_edit"),
    path('business-line/<int:pk>/delete/', views.BusinessLineDeleteView.as_view(), name="business_delete"),

    # LINE OBJECT #
    ###############
    path('line-objects/', views.LineObjectListView.as_view(), name="lo_list"),
    path('line-object/new/', views.LineObjectCreateView.as_view(), name="lo_new"),
    path('line-object/<int:pk>/edit/', views.LineObjectUpdateView.as_view(), name="lo_edit"),
    path('line-object/<int:pk>/delete/', views.LineObjectDeleteView.as_view(), name="lo_delete"),

    # RC #
    ######
    path('responsibility-centres/', views.ResponsibilityCentreListView.as_view(), name="rc_list"),
    path('responsibility-centre/new/', views.ResponsibilityCentreCreateView.as_view(), name="rc_new"),
    path('responsibility-centre/<int:pk>/edit/', views.ResponsibilityCentreUpdateView.as_view(), name="rc_edit"),
    path('responsibility-centre/<int:pk>/delete/', views.ResponsibilityCentreDeleteView.as_view(), name="rc_delete"),

    # # # Entry #
    # # #########
    # path('entries/', views.EntryListView.as_view(), name="entry_list"),
    # path('entry/new/', views.EntryCreateView.as_view(), name="entry_new"),
    # path('entry/<int:pk>/view', views.EntryDetailView.as_view(), name="entry_detail"),
    # path('entry/<int:pk>/edit', views.EntryUpdateView.as_view(), name="entry_edit"),
    # path('entry/<int:pk>/delete', views.EntryDeleteView.as_view(), name="entry_delete"),
    #
    # # NOTES #
    # #########
    # path('entry/<int:entry>/note/new/', views.NoteCreateView.as_view(), name="note_new"),
    # path('note/<int:pk>/edit/', views.NoteUpdateView.as_view(), name="note_edit"),
    # path('note/<int:pk>/delete/', views.note_delete, name="note_delete"),
]
