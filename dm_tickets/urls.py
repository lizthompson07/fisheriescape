from django.urls import path
from . import views

app_name = 'tickets'

urlpatterns = [
    path('close/', views.CloserTemplateView.as_view(), name ="close_me" ),

    # Tickets #
    ###########
    path('', views.TicketListView.as_view() , name="list"),
    path('<int:pk>/view/', views.TicketDetailView.as_view() , name="detail"),
    path('<int:pk>/edit/', views.TicketUpdateView.as_view() , name="update"),
    path('<int:pk>/delete/', views.TicketDeleteView.as_view() , name="delete"),
    path('new/', views.TicketCreateView.as_view() , name="create"),
    path('<int:pk>/new-note/', views.TicketNoteUpdateView.as_view() , name="new_note"),

    # EMAIL #
    #########
    path('<int:ticket>/send-resolved-notification/', views.send_resolved_email, name ="send_resolved_email" ),

    # Service Desk Tickets #
    ########################
    path('sd-ticket/<pk>/view/', views.ServiceDeskDetailView.as_view() , name="sd_detail"),
    path('sd-ticket/<pk>/edit/', views.ServiceDeskUpdateView.as_view() , name="sd_edit"),
    path('sd-ticket/new/', views.ServiceDeskCreateView.as_view() , name="sd_create"),

    # Tags #
    ########
    path('tag/<pk>/view/', views.TagDetailView.as_view() , name="tag_detail"),
    path('tag/<pk>/edit/', views.TagUpdateView.as_view() , name="tag_edit"),
    path('<int:ticket>/tag/new/', views.TagCreateView.as_view() , name="tag_create"),
    path('<int:ticket>/tag/insert/', views.TagListView.as_view() , name="tag_insert"),
    path('<int:ticket>/tag/insert/<int:tag>', views.add_tag_to_ticket , name="add_tag"),

    # Files #
    #########
    path('<int:ticket>/file/new/', views.FileCreateView.as_view() , name="file_create"),
    path('<int:ticket>/file/<int:pk>/view', views.FileDetailView.as_view() , name="file_detail"),
    path('<int:ticket>/file/<int:pk>/edit', views.FileUpdateView.as_view() , name="file_update"),
    path('<int:ticket>/file/<int:pk>/delete', views.FileDeleteView.as_view() , name="file_delete"),

    # People #
    ##########
    path('person/<pk>/view/', views.PersonDetailView.as_view() , name="person_detail"),
    path('person/<pk>/edit/', views.PersonUpdateView.as_view() , name="person_edit"),
    path('<int:ticket>/person/new/', views.PersonCreateView.as_view() , name="ticket_person_create"),
    path('person/new/', views.PersonCreateView.as_view() , name="person_create"),
    path('<int:ticket>/person/insert/', views.PersonListView.as_view() , name="person_insert"),
    path('<int:ticket>/person/insert/<int:person>', views.add_person_to_ticket , name="add_person"),

    # Request Type #
    ################
    # path('request_type/<pk>/view/', views.RequestTypeDetailView.as_view() , name="request_type_detail"),
    # path('request_type/<pk>/edit/', views.RequestTypeUpdateView.as_view() , name="request_type_edit"),
    path('request_type/new/', views.RequestTypeCreateView.as_view() , name="request_type_create"),



]
