from django.urls import path
from django.views.decorators.cache import cache_page
from django.contrib.auth import views as auth_views
from . import views
from courses.views import ManageCourseListView



urlpatterns = [


path(
        'mine/',
        ManageCourseListView.as_view(),
        name='manage_course_list',
    ),
]