from django.urls import path
from django.views.decorators.cache import cache_page
from django.contrib.auth import views as auth_views
from . import views
from .views import (
    ProfileView,
    ProfileUpdateView,
    ProfilePhotoUpdateView,
)

urlpatterns = [
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt'
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),
    path(
        'enroll-course/',
        views.StudentEnrollCourseView.as_view(),
        name='student_enroll_course',
    ),
    path(
        'courses/',
        views.StudentCourseListView.as_view(),
        name='student_course_list',
    ),
    path(
        'profile/', ProfileView.as_view(), name='profile'),
    path(
        'profile/edit/', ProfileUpdateView.as_view(), name='profile_edit'),
    path('progress/', views.ProgressDashboardView.as_view(), name='progress_dashboard'),
    path(
        'profile/photo/', ProfilePhotoUpdateView.as_view(), name='profile_photo_upload'),
    path(
        'course/<pk>/',
        views.StudentCourseDetailView.as_view(),
        name='student_course_detail'
    ),
    path(
        'course/<pk>/<module_id>/',
        views.StudentCourseDetailView.as_view(),
        name='student_course_detail_module'
    ),
    path(
        'course/<pk>/',
        cache_page(60 * 15)(views.StudentCourseDetailView.as_view()),
        name='student_course_detail',
    ),
    path(
        'course/<pk>/<module_id>/',
        cache_page(60 * 15)(views.StudentCourseDetailView.as_view()),
        name='student_course_detail_module',
    ),
]
