from django.urls import path
from . import views

app_name = 'csas'

urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name="index"),
    # path('close/', views.CloserTemplateView.as_view(), name="close_me"),
    # path('search/', views.SearchFormView.as_view(), name="sample_search"),
    # path('dataflow/', views.DataFlowTemplateView.as_view(), name ="dataflow" ),
]
