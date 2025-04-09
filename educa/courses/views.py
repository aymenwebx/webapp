from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from django.apps import apps
from ckeditor.widgets import CKEditorWidget
from django import forms
from bs4 import BeautifulSoup
from django.contrib import messages
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db.models import Count, Q
from django.forms.models import modelform_factory
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic.base import TemplateResponseMixin, View, TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from students.forms import CourseEnrollForm

from .forms import ModuleFormSet
from .models import Content, Course, Module, Subject, CompletedContent, Image, File, Video, Text


class TextForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget(config_name='default'))

    class Meta:
        model = apps.get_model('courses', 'text')
        fields = ['title', 'content']

    def clean_content(self):
        content = self.cleaned_data['content']
        return clean_html(content)  # We'll define this function


class TableForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget(config_name='table'))

    class Meta:
        model = apps.get_model('courses', 'table')
        fields = ['title', 'content']


class ImageForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['file']


class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['url']


class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['file']


def clean_html(content):
    """Sanitize HTML content"""
    allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'table', 'tr', 'td', 'th', 'span']
    allowed_attrs = {
        'span': ['style'],
        'table': ['border', 'cellpadding', 'cellspacing'],
        'td': ['colspan', 'rowspan']
    }

    soup = BeautifulSoup(content, 'html.parser')
    for tag in soup.find_all(True):
        if tag.name not in allowed_tags:
            tag.unwrap()
        else:
            tag.attrs = {k: v for k, v in tag.attrs.items()
                         if tag.name in allowed_attrs and k in allowed_attrs[tag.name]}
    return str(soup)


class OwnerMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerEditMixin:
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class OwnerCourseMixin(
    OwnerMixin, LoginRequiredMixin, PermissionRequiredMixin
):
    model = Course
    fields = ['subject', 'title', 'slug', 'overview']
    prepopulated_fields = {'slug': ('title',)}
    success_url = reverse_lazy('manage_course_list')


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    template_name = 'courses/manage/course/form.html'


class ManageCourseListView(OwnerCourseMixin, ListView):
    template_name = 'courses/manage/course/list.html'
    permission_required = 'courses.view_course'


class CourseCreateView(OwnerCourseEditMixin, CreateView):
    template_name = 'courses/course/create_course.html'
    permission_required = 'courses.add_course'



class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    permission_required = 'courses.change_course'


class CourseDeleteView(OwnerCourseMixin, DeleteView):
    template_name = 'courses/manage/course/delete.html'
    permission_required = 'courses.delete_course'


class CourseModuleUpdateView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/formset.html'
    course = None

    def get_formset(self, data=None):
        return ModuleFormSet(instance=self.course, data=data)

    def dispatch(self, request, pk):
        self.course = get_object_or_404(
            Course, id=pk, owner=request.user
        )
        return super().dispatch(request, pk)

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response(
            {'course': self.course, 'formset': formset}
        )

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('manage_course_list')
        return self.render_to_response(
            {'course': self.course, 'formset': formset}
        )


class ContentCreateView(View):
    def get(self, request, module_id):
        module = get_object_or_404(Module, id=module_id)
        return render(request, 'courses/manage/content/form.html', {'module': module})

    def post(self, request, module_id):
        module = get_object_or_404(Module, id=module_id, course__owner=request.user)
        content_types = request.POST.getlist('content_type[]')
        print("Received content types:", content_types)

        for index, content_type in enumerate(content_types):
            if content_type == 'text':
                title = request.POST.getlist('text_title[]')[index]
                content = request.POST.getlist('text_content[]')[index]
                item = Text.objects.create(owner=request.user, title=title, content=content)

            elif content_type == 'image':
                title = request.POST.getlist('image_title[]')[index]
                file = request.FILES.getlist('image_file[]')[index]
                item = Image.objects.create(owner=request.user, title=title, file=file)

            elif content_type == 'video':
                title = request.POST.getlist('video_title[]')[index]
                url = request.POST.getlist('video_url[]')[index]
                item = Video.objects.create(owner=request.user, title=title, url=url)

            elif content_type == 'file':
                title = request.POST.getlist('file_title[]')[index]
                file = request.FILES.getlist('file_file[]')[index]
                item = File.objects.create(owner=request.user, title=title, file=file)

            elif content_type == 'table':
                # If you have a Table model and JS table editor submitting serialized data
                pass  # We'll fill this part if you're ready

            else:
                continue  # Skip if content_type is invalid

            # Link the new item to the module through Content
            Content.objects.create(module=module, item=item)

        return redirect('module_content_list', module.id)


class ContentDeleteView(View):
    def post(self, request, id):
        content = get_object_or_404(
            Content, id=id, module__course__owner=request.user
        )
        module = content.module
        content.item.delete()
        content.delete()
        return redirect('module_content_list', module.id)


class ModuleContentListView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/content_list.html'

    def get(self, request, module_id):
        module = get_object_or_404(
            Module, id=module_id, course__owner=request.user
        )
        return self.render_to_response({'module': module})


class ModuleOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Module.objects.filter(
                id=id, course__owner=request.user
            ).update(order=order)
        return self.render_json_response({'saved': 'OK'})


class ContentOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Content.objects.filter(
                id=id, module__course__owner=request.user
            ).update(order=order)
        return self.render_json_response({'saved': 'OK'})


class CourseListView(TemplateResponseMixin, View):
    model = Course
    queryset = Course.objects.filter(published=True)
    template_name = 'courses/course/list.html'

    def get(self, request, subject=None):
        print(self.request.user.get_all_permissions())
        subjects = cache.get('all_subjects')
        if not subjects:
            subjects = Subject.objects.annotate(
                total_courses=Count('courses')
            )
            cache.set('all_subjects', subjects)
        all_courses = Course.objects.annotate(
            total_modules=Count('modules')
        )
        if subject:
            subject = get_object_or_404(Subject, slug=subject)
            key = f'subject_{subject.id}_courses'
            courses = cache.get(key)
            if not courses:
                courses = all_courses.filter(subject=subject)
                cache.set(key, courses)
        else:
            courses = cache.get('all_courses')
            if not courses:
                courses = all_courses
                cache.set('all_courses', courses)
        return self.render_to_response(
            {
                'subjects': subjects,
                'subject': subject,
                'courses': courses,
            }
        )


class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_enrolled'] = False
        context['enroll_form'] = CourseEnrollForm(
            initial={'course': self.object}
        )

        if self.request.user.is_authenticated:
            completed = CompletedContent.objects.filter(
                user=self.request.user,
                content__module__course=self.object
            ).values_list('content_id', flat=True)
            context['completed_contents'] = list(completed)
            context['is_enrolled'] = self.object.students.filter(
                id=self.request.user.id
            ).exists()

            # Add preview content for enrolled students
            if context['is_enrolled']:
                preview_module = self.object.modules.first()
                if preview_module:
                    context['preview_contents'] = preview_module.contents.all()[:2]

        return context

class CourseSearchView(ListView):
    model = Course
    template_name = 'courses/course/search_results.html'
    context_object_name = 'courses'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Course.objects.filter(
                Q(title__icontains=query) |
                Q(subject__title__icontains=query) |
                Q(overview__icontains=query),
                published=True
            ).distinct()
        return Course.objects.filter(published=True)


class ContentCompletionView(LoginRequiredMixin, View):
    def post(self, request, content_id):
        content = get_object_or_404(Content, id=content_id)

        # Verify user is enrolled in the course
        if request.user not in content.module.course.students.all():
            return JsonResponse({'status': 'error'}, status=403)

        completed, created = CompletedContent.objects.get_or_create(
            user=request.user,
            content=content
        )

        return JsonResponse({
            'status': 'success',
            'action': 'added' if created else 'exists',
            'completed_count': content.module.contents.count(),
            'user_completed': content.module.contents.filter(
                completedcontent__user=request.user
            ).count()
        })


class ProgressDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'students/progress.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['completed_lessons'] = CompletedContent.objects.filter(user=self.request.user)
        return context


class ContentCompleteView(LoginRequiredMixin, View):
    def post(self, request, content_id):
        content = get_object_or_404(Content, id=content_id)
        if request.user not in content.module.course.students.all():
            return JsonResponse({'status': 'error', 'message': 'Not enrolled'}, status=403)

        completed, created = CompletedContent.objects.get_or_create(
            user=request.user,
            content=content
        )

        if not created:
            completed.delete()
            action = 'removed'
        else:
            action = 'added'

        return JsonResponse({
            'status': 'success',
            'action': action,
            'completed': created
        })


class ModuleCompleteAllView(LoginRequiredMixin, View):
    def post(self, request, module_id):
        module = get_object_or_404(Module, id=module_id)
        if request.user not in module.course.students.all():
            return JsonResponse({'status': 'error', 'message': 'Not enrolled'}, status=403)

        contents = module.contents.all()
        existing = CompletedContent.objects.filter(
            user=request.user,
            content__in=contents
        ).values_list('content_id', flat=True)

        # Toggle: If all are completed, uncomplete all. Otherwise complete all.
        if set(existing) == set(contents.values_list('id', flat=True)):
            CompletedContent.objects.filter(
                user=request.user,
                content__in=contents
            ).delete()
            action = 'removed_all'
        else:
            for content in contents:
                CompletedContent.objects.get_or_create(
                    user=request.user,
                    content=content
                )
            action = 'added_all'

        return JsonResponse({
            'status': 'success',
            'action': action
        })


class ContentTypeSelectView(TemplateView):
    template_name = 'courses/manage/content/content_type_select.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        module_id = self.kwargs.get('module_id')
        module = get_object_or_404(Module, id=module_id, course__owner=self.request.user)
        context['module'] = module
        return context