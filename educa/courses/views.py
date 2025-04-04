from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.core.cache import cache
from django.db.models import Count, Q
from django.forms.models import modelform_factory
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic.base import TemplateResponseMixin, View, TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from students.forms import CourseEnrollForm

from .forms import ModuleFormSet
from .models import Content, Course, Module, Subject, CompletedContent


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
    success_url = reverse_lazy('manage_course_list')


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    template_name = 'courses/manage/course/form.html'


class ManageCourseListView(OwnerCourseMixin, ListView):
    template_name = 'courses/manage/course/list.html'
    permission_required = 'courses.view_course'


class CourseCreateView(OwnerCourseEditMixin, CreateView):
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


class ContentCreateUpdateView(TemplateResponseMixin, View):
    module = None
    model = None
    obj = None
    template_name = 'courses/manage/content/form.html'

    def get_model(self, model_name):
        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(
                app_label='courses', model_name=model_name
            )
        return None

    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(
            model, exclude=['owner', 'order', 'created', 'updated']
        )
        return Form(*args, **kwargs)

    def dispatch(self, request, module_id, model_name, id=None):
        self.module = get_object_or_404(
            Module, id=module_id, course__owner=request.user
        )
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(
                self.model, id=id, owner=request.user
            )
        return super().dispatch(request, module_id, model_name, id)

    def get(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response(
            {'form': form, 'object': self.obj}
        )

    def post(self, request, module_id, model_name, id=None):
        form = self.get_form(
            self.model,
            instance=self.obj,
            data=request.POST,
            files=request.FILES,
        )
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                # new content
                Content.objects.create(module=self.module, item=obj)
            return redirect('module_content_list', self.module.id)
        return self.render_to_response(
            {'form': form, 'object': self.obj}
        )


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


class MarkLessonCompleteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        content_id = kwargs.get('lesson_id')
        content = Content.objects.get(id=content_id)
        # Ensure user is enrolled in the course
        if request.user in content.module.course.students.all():
            CompletedLesson.objects.get_or_create(user=request.user, content=content)
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error'}, status=403)


class ProgressDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'students/progress.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['completed_lessons'] = CompletedLesson.objects.filter(user=self.request.user)
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
