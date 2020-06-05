from django.urls import path
from . import views

app_name = 'csas'

urlpatterns = [
    # for home/index page
    path('',                                       views.IndexTemplateView.as_view(),  name="index"),
    path('index_meeting/',                         views.IndexMeetingView.as_view(),   name="index_met"),
    path('index_publication',                      views.IndexPublicationView.as_view(), name="index_pub"),

    # for Requests
    path('request/',                               views.RequestList.as_view(),        name="list_req"),
    path('request/new/',                           views.RequestEntry.as_view(),       name="create_req"),
    path('request/update/<int:pk>/',               views.RequestUpdate.as_view(),      name="update_req"),
    path('request/update/<int:pk>/<str:pop>/',     views.RequestUpdate.as_view(),      name="update_req"),
    path('request/details/<int:pk>/',              views.RequestDetails.as_view(),     name="details_req"),

    # for Meetings
    path('meeting/',                           views.MeetingList.as_view(),           name="list_met"),
    path('meeting_DFO_participants/',          views.MeetingListDFOPars.as_view(),    name="list_met_DFO_pars"),
    path('meeting_other_participants/',        views.MeetingListOtherPars.as_view(),  name="list_met_other_pars"),

    path('meeting/new/',                            views.MeetingEntry.as_view(),          name="create_met"),
    path('meeting_docs/new/',                       views.MeetingEntryDocs.as_view(),      name="create_met_doc"),
    path('meeting_DFO_participants/new/',           views.MeetingEntryDFOPars.as_view(),   name="create_met_DFO_pars"),
    path('meeting_other_participants/new/',         views.MeetingEntryOtherPars.as_view(), name="create_met_other_pars"),
    path('meeting_OM_costs/new/',                   views.MeetingEntryOMCosts.as_view(),   name="create_met_OM_costs"),
    path('meeting_media/new/',                      views.MeetingEntryMedia.as_view(),     name="create_met_media"),

    path('meeting/update/<int:pk>/<str:pop>/',      views.MeetingUpdate.as_view(),      name="update_met"),
    path('meeting/update/<int:pk>/',                views.MeetingUpdate.as_view(),      name="update_met"),

    path('meeting_docs/update/<int:pk>/<str:pop>/', views.MeetingUpdateDocs.as_view(),  name="update_met_doc"),
    path('meeting_docs/update/<int:pk>/',           views.MeetingUpdateDocs.as_view(),  name="update_met_doc"),

    path('meeting_DFO_participants/update/<int:pk>/<str:pop>/',   views.MeetingUpdateDFOPars.as_view(),   name="update_met_DFO_pars"),
    path('meeting_DFO_participants/update/<int:pk>/',             views.MeetingUpdateDFOPars.as_view(),   name="update_met_DFO_pars"),

    path('meeting_other_participants/update/<int:pk>/<str:pop>/', views.MeetingUpdateOtherPars.as_view(), name="update_met_other_pars"),
    path('meeting_other_participants/update/<int:pk>/',           views.MeetingUpdateOtherPars.as_view(), name="update_met_other_pars"),

    path('meeting_OM_costs/update/<int:pk>/<str:pop>/', views.MeetingUpdateOMCosts.as_view(), name="update_met_OM_costs"),
    path('meeting_OM_costs/update/<int:pk>/',           views.MeetingUpdateOMCosts.as_view(), name="update_met_OM_costs"),

    path('meeting_media/update/<int:pk>/<str:pop>/', views.MeetingUpdateMedia.as_view(), name="update_met_media"),
    path('meeting_media/update/<int:pk>/',           views.MeetingUpdateMedia.as_view(), name="update_met_media"),

    path('meeting/details/<int:pk>/',                    views.MeetingDetails.as_view(),          name="details_met"),
    path('meeting_docs/details/<int:pk>/',               views.MeetingDetailsDocs.as_view(),      name="details_met_docs"),
    path('meeting_DFO_participants/details/<int:pk>/',   views.MeetingDetailsDFOPars.as_view(),   name="details_met_DFO_pars"),
    path('meeting_other_participants/details/<int:pk>/', views.MeetingDetailsOtherPars.as_view(), name="details_met_other_pars"),
    path('meeting_OM_costs/details/<int:pk>/',           views.MeetingDetailsOMCosts.as_view(),   name="details_met_OM_costs"),
    path('meeting_media/details/<int:pk>/',              views.MeetingDetailsMedia.as_view(),     name="details_met_media"),

    # for Publications
    path('publication/',                           views.PublicationList.as_view(),    name="list_pub"),

    path('publication/new/',              views.PublicationEntry.as_view(),            name="create_pub"),
    path('publication_status/new/',       views.PublicationEntryStatus.as_view(),      name="create_pub_status"),
    path('publication_trans_info/new/',   views.PublicationEntryTransInfo.as_view(),   name="create_pub_trans_info"),
    path('publication_doc_location/new/', views.PublicationEntryDocLocation.as_view(), name="create_pub_doc_location"),
    path('publication_OM_costs/new/',     views.PublicationEntryOMCosts.as_view(),     name="create_pub_OM_costs"),
    path('publication_comm_results/new/', views.PublicationEntryComResults.as_view(),  name="create_pub_com_results"),

    path('publication/update/<int:pk>/<str:pop>/', views.PublicationUpdate.as_view(),  name="update_pub"),
    path('publication/update/<int:pk>/',           views.PublicationUpdate.as_view(),  name="update_pub"),

    path('publication/details/<int:pk>/',          views.PublicationDetails.as_view(), name="details_pub"),

    # for Contacts
    path('contacts/',                              views.ContactList.as_view(),        name="list_con"),
    path('contacts/new/',                          views.ContactEntry.as_view(),       name="create_con"),
    path('contacts/update/<int:pk>/<str:pop>/',    views.ContactUpdate.as_view(),      name="update_con"),
    path('contacts/update/<int:pk>/',              views.ContactUpdate.as_view(),      name="update_con"),
    path('contacts/details/<int:pk>/',             views.ContactDetails.as_view(),     name="details_con"),

    path('close/',                                 views.CloserTemplateView.as_view(), name="close_me"),
    path('create/honorific/',                      views.HonorificView.as_view(),      name="create_coh"),
    path('create/language/',                       views.LanguageView.as_view(),       name="create_lan")

    # path('search/', views.SearchFormView.as_view(), name="sample_search"),
    # path('dataflow/', views.DataFlowTemplateView.as_view(), name ="dataflow" ),
]
