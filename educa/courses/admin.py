from django.contrib import admin
from django.utils import timezone
from django import forms
from .models import Course, Module, Subject, Text, File, Image, Video, Table, Content
from ckeditor.widgets import CKEditorWidget  # If using CKEditor

# If you're using CKEditor for rich text
class TextAdminForm(forms.ModelForm):
    class Meta:
        model = Text
        fields = '__all__'
        widgets = {
            'content': CKEditorWidget(),
        }

# If you're using CKEditor for tables
class TableAdminForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = '__all__'
        widgets = {
            'content': CKEditorWidget(config_name='table'),
        }

class ContentInline(admin.StackedInline):
    model = Content
    extra = 0
    ct_field = 'content_type'
    ct_fk_field = 'object_id'
    fields = ['order', 'content_type', 'object_id']

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']
    prepopulated_fields = {'slug': ('title',)}

class ModuleInline(admin.StackedInline):
    model = Module
    extra = 0
    show_change_link = True
    inlines = [ContentInline]  # Nest ContentInline within ModuleInline

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'published', 'published_date', 'owner']
    list_filter = ['published', 'published_date', 'subject']
    search_fields = ['title', 'overview']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ModuleInline]
    actions = ['publish_courses']
    raw_id_fields = ['owner']

    def publish_courses(self, request, queryset):
        updated = queryset.update(published=True, published_date=timezone.now())
        self.message_user(request, f'{updated} courses published.')


@admin.register(Text)
class TextAdmin(admin.ModelAdmin):
    form = TextAdminForm  # Only if using CKEditor
    list_display = ['title', 'owner', 'created', 'updated']
    list_filter = ['created', 'updated']
    search_fields = ['title', 'content']
    raw_id_fields = ['owner']

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'created', 'updated']
    list_filter = ['created', 'updated']
    search_fields = ['title']
    raw_id_fields = ['owner']

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'created', 'updated']
    list_filter = ['created', 'updated']
    search_fields = ['title']
    raw_id_fields = ['owner']

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'created', 'updated']
    list_filter = ['created', 'updated']
    search_fields = ['title', 'url']
    raw_id_fields = ['owner']

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    form = TableAdminForm  # Only if using CKEditor
    list_display = ['title', 'owner', 'created', 'updated']
    list_filter = ['created', 'updated']
    search_fields = ['title', 'content']
    raw_id_fields = ['owner']


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ['module', 'content_type', 'object_id', 'order']
    list_filter = ['content_type']
    search_fields = ['module__title']