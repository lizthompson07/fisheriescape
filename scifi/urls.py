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
    path('allotment-code/<int:pk>/view/', views.AllotmentCodeDetailView.as_view(), name="allotment_detail"),

    # BUSINESS LINE #
    #################
    path('business-lines/', views.BusinessLineListView.as_view(), name="business_list"),
    path('business-line/new/', views.BusinessLineCreateView.as_view(), name="business_new"),
    path('business-line/<int:pk>/edit/', views.BusinessLineUpdateView.as_view(), name="business_edit"),
    path('business-line/<int:pk>/delete/', views.BusinessLineDeleteView.as_view(), name="business_delete"),
    path('business-line/<int:pk>/view/', views.BusinessLineDetailView.as_view(), name="business_detail"),

    # LINE OBJECT #
    ###############
    path('line-objects/', views.LineObjectListView.as_view(), name="lo_list"),
    path('line-object/new/', views.LineObjectCreateView.as_view(), name="lo_new"),
    path('line-object/<int:pk>/edit/', views.LineObjectUpdateView.as_view(), name="lo_edit"),
    path('line-object/<int:pk>/delete/', views.LineObjectDeleteView.as_view(), name="lo_delete"),
    path('line-object/<int:pk>/view/', views.LineObjectDetailView.as_view(), name="lo_detail"),

    # RC #
    ######
    path('responsibility-centres/', views.ResponsibilityCentreListView.as_view(), name="rc_list"),
    path('responsibility-centre/new/', views.ResponsibilityCentreCreateView.as_view(), name="rc_new"),
    path('responsibility-centre/<int:pk>/edit/', views.ResponsibilityCentreUpdateView.as_view(), name="rc_edit"),
    path('responsibility-centre/<int:pk>/delete/', views.ResponsibilityCentreDeleteView.as_view(), name="rc_delete"),
    path('responsibility-centre/<int:pk>/view/', views.ResponsibilityCentreDetailView.as_view(), name="rc_detail"),

    # PROJECTS #
    ############
    path('projects/', views.ProjectListView.as_view(), name="project_list"),
    path('project/new/', views.ProjectCreateView.as_view(), name="project_new"),
    path('project/<int:pk>/edit/', views.ProjectUpdateView.as_view(), name="project_edit"),
    path('project/<int:pk>/delete/', views.ProjectDeleteView.as_view(), name="project_delete"),
    path('project/<int:pk>/view/', views.ProjectDetailView.as_view(), name="project_detail"),

    # TRANSACTION #
    ###############
    path('transactions/', views.TransactionListView.as_view(), name="trans_list"),
    path('transaction/new/', views.TransactionCreateView.as_view(), name="trans_new"),
    path('transaction/<int:pk>/view/', views.TransactionDetailView.as_view(), name="trans_detail"),
    path('transaction/<int:pk>/edit/', views.TransactionUpdateView.as_view(), name="trans_edit"),
    path('transaction/<int:pk>/delete/', views.TransactionDeleteView.as_view(), name="trans_delete"),

    # Reports #
    ###########
    path('reports/search/', views.ReportSearchFormView.as_view(), name="report_search"),
    path('report/branch-summary/fiscal/<str:fiscal_year>/', views.BranchSummaryTemplateView.as_view(), name="report_branch"),
    path('report/account-summary/fiscal/<str:fiscal_year>/rc/<int:rc>/', views.AccountSummaryTemplateView.as_view(), name="report_rc"),
    path('report/project-summary/fiscal/<str:fiscal_year>/rc/<int:rc>/project/<int:project>/', views.ProjectSummaryListView.as_view(), name="report_project"),
    path('reports/master-spreadsheet/fiscal-year/<str:fiscal_year>/', views.master_spreadsheet, name="report_master"),


]
