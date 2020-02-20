from django.urls import path
from . import views

app_name = 'csas'

urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name="index"),
    path('contacts/', views.ContactsTemplateView.as_view(), name="contacts"),
    path('close/', views.CloserTemplateView.as_view(), name="close_me"),
    # path('search/', views.SearchFormView.as_view(), name="sample_search"),
    # path('dataflow/', views.DataFlowTemplateView.as_view(), name ="dataflow" ),

    path('create/honorific/', views.HonorificView.as_view(), name="create_coh"),
    path('create/language/', views.LanguageView.as_view(), name="create_lan")
]
