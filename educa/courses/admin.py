from django.contrib import admin
from django.utils import timezone

from .models import Course, Module, Subject


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']
    prepopulated_fields = {'slug': ('title',)}


class ModuleInline(admin.StackedInline):
    model = Module


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'published', 'published_date']

    list_filter = ['published', 'published_date', 'subject']
    search_fields = ['title', 'overview']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ModuleInline]
    actions = ['publish_courses']

    def publish_courses(self, request, queryset):
        queryset.update(published=True, published_date=timezone.now())