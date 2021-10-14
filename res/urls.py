from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name="index"),

    # reference tables
    path('settings/contexts/', views.ContextFormsetView.as_view(), name="manage_contexts"),
    path('settings/context/<int:pk>/delete/', views.ContextHardDeleteView.as_view(), name="delete_context"),

    path('settings/outcomes/', views.OutcomeFormsetView.as_view(), name="manage_outcomes"),
    path('settings/outcome/<int:pk>/delete/', views.OutcomeHardDeleteView.as_view(), name="delete_outcome"),

    path('settings/achievement-categories/', views.AchievementCategoryFormsetView.as_view(), name="manage_achievement_categories"),
    path('settings/achievement-category/<int:pk>/delete/', views.AchievementCategoryHardDeleteView.as_view(), name="delete_achievement_category"),

    path('settings/group-levels/', views.GroupLevelFormsetView.as_view(), name="manage_group_levels"),
    path('settings/group-level/<int:pk>/delete/', views.GroupLevelHardDeleteView.as_view(), name="delete_group_level"),

    path('settings/publication-types/', views.PublicationTypeFormsetView.as_view(), name="manage_publication_types"),
    path('settings/publication-type/<int:pk>/delete/', views.PublicationTypeHardDeleteView.as_view(), name="delete_publication_type"),

    # APPLICATIONS
    path('applications/', views.ApplicationListView.as_view(), name="application_list"),
    path('applications/new/', views.ApplicationCreateView.as_view(), name="application_new"),
    path('applications/<int:pk>/view/', views.ApplicationDetailView.as_view(), name="application_detail"),
    path('applications/<int:pk>/edit/', views.ApplicationUpdateView.as_view(), name="application_edit"),
    path('applications/<int:pk>/delete/', views.ApplicationDeleteView.as_view(), name="application_delete"),
    path('applications/<int:pk>/submit/', views.ApplicationSubmitView.as_view(), name="application_submit"),

    #
    #
    # # reports
    # path('reports/', views.ReportSearchFormView.as_view(), name="reports"),# tested
    # path('reports/dive-log/', views.dive_log_report, name="dive_log_report"),# tested

]

app_name = 'res'
