"""
URL configuration for educa project.

The `urlpatterns` list routes URLs to views. For more information
please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include,
        path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from courses.views import CourseSearchView
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
urlpatterns = [
    path(
        'admin/', admin.site.urls
    ),

    path('accounts/', include('accounts.urls')),
    path('teachers/', include('teachers.urls')),
    path('courses/', include('courses.urls')),
    path('students/', include('students.urls')),
    path('search/', CourseSearchView.as_view(), name='course_search'),

    # path('__debug__/', include('debug_toolbar.urls')),
    path('', TemplateView.as_view(template_name='landing_page.html'), name='home'),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
