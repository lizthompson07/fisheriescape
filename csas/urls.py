from django.urls import path
from . import views

app_name = 'csas'

urlpatterns = [
    path('',              views.IndexTemplateView.as_view(),        name="index"),

    path('contacts/',     views.ContactsList.as_view(),  name="list_con"),
    path('contacts/new/', views.ContactsEntry.as_view(), name="create_con"),
    path('contacts/update/<int:pk>', views.ContactsUpdate.as_view(), name="update_con"),
    path('contacts/details/<int:pk>', views.ContactDetails.as_view(), name="details_con"),

    path('meetings/',     views.MeetingsTemplateView.as_view(),     name="meetings"),
    path('publications/', views.PublicationsTemplateView.as_view(), name="publications"),
    path('requests/',     views.RequestsTemplateView.as_view(),     name="requests"),
    path('others/',       views.OthersTemplateView.as_view(),       name="others"),
    path('close/',        views.CloserTemplateView.as_view(),       name="close_me"),
    # path('search/', views.SearchFormView.as_view(), name="sample_search"),
    # path('dataflow/', views.DataFlowTemplateView.as_view(), name ="dataflow" ),

    path('create/honorific/', views.HonorificView.as_view(), name="create_coh"),
    path('create/language/', views.LanguageView.as_view(), name="create_lan")
]
