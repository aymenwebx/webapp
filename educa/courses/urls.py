from django.urls import path

from . import views


urlpatterns = [
    path('', views.CourseListView.as_view(), name='course_list'),

    path(
        'mine/',
        views.ManageCourseListView.as_view(),
        name='manage_course_list',
    ),
    path(
        'create/',
        views.CourseCreateView.as_view(),
        name='course_create',
    ),
    path(
        '<pk>/edit/',
        views.CourseUpdateView.as_view(),
        name='course_edit',
    ),
    path(
        '<pk>/delete/',
        views.CourseDeleteView.as_view(),
        name='course_delete',
    ),
    path('lesson/complete/<int:lesson_id>/', views.ContentCompleteView.as_view(), name='mark_lesson_complete'),
    path('progress/', views.ProgressDashboardView.as_view(), name='progress_dashboard'),


    path(
        '<pk>/module/',
        views.CourseModuleUpdateView.as_view(),
        name='course_module_update',
    ),
    path('module/<int:module_id>/content/create/select/', views.ContentTypeSelectView.as_view(),
         name='module_content_select'),
    path('module/<int:module_id>/content/create/', views.ContentCreateView.as_view(),
         name='module_content_create'),
    path(
        'module/<int:module_id>/content/<model_name>/<id>/',
        views.ContentCreateView.as_view(),
        name='module_content_update',
    ),
    path('module/<int:module_id>/complete_all/', views.ModuleCompleteAllView.as_view(), name='module_complete_all'),
    path(
        'content/<int:id>/delete/',
        views.ContentDeleteView.as_view(),
        name='module_content_delete',
    ),
    path(
        'module/<int:module_id>/',
        views.ModuleContentListView.as_view(),
        name='module_content_list',
    ),
    path(
        'module/order/',
        views.ModuleOrderView.as_view(),
        name='module_order',
    ),
    path(
        'content/order/',
        views.ContentOrderView.as_view(),
        name='content_order',
    ),
    path('content/<int:content_id>/complete/', views.ContentCompleteView.as_view(), name='content_complete'),
    path(
        'subject/<slug:subject>/',
        views.CourseListView.as_view(),
        name='course_list_subject',
    ),
    path(
        '<slug:slug>/',
        views.CourseDetailView.as_view(),
        name='course_detail',
    ),
]
