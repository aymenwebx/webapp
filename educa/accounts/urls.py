from django.urls import path
from django.contrib.auth import views as auth_views
from .views import UserRegistrationView, CustomLoginView
from courses.views import CourseListView
urlpatterns = [

    path(
        'login/',
        CustomLoginView.as_view(), name='login'),
    path(
        'logout/',
        auth_views.LogoutView.as_view(),
        name='logout',
    ),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('courses/', CourseListView.as_view(), name='course_list'),
]