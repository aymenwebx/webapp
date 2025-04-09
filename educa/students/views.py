from courses.models import Course, CompletedContent, Content, Module
from accounts.forms import CustomUserCreationForm
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, FormView
from django.views.generic.list import ListView
from django.views.generic import TemplateView, UpdateView

from .forms import CourseEnrollForm, ProfileForm, ProfilePhotoForm
from accounts.models import Profile


class StudentEnrollCourseView(LoginRequiredMixin, FormView):
    course = None
    form_class = CourseEnrollForm

    def form_valid(self, form):
        self.course = form.cleaned_data['course']
        self.course.students.add(self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'student_course_detail', args=[self.course.id]
        )

    def render_to_response(self, context, **response_kwargs):
        return redirect(self.get_success_url())

class StudentCourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'students/course/list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(students__in=[self.request.user])


class StudentCourseDetailView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'students/course/detail.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(students__in=[self.request.user])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get course object
        course = self.get_object()
        completed_contents = set(
            CompletedContent.objects.filter(
                user=self.request.user,
                content__module__course=course
            ).values_list('content_id', flat=True)
        )

        context['completed_contents'] = completed_contents
        if 'module_id' in self.kwargs:
            # get current module
            context['module'] = course.modules.get(
                id=self.kwargs['module_id']
            )
        else:
            # get first module
            context['module'] = course.modules.all()[0]
        return context


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'students/student/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Safely get or create profile
        profile, created = Profile.objects.get_or_create(user=user)

        # Get enrolled courses only
        enrolled_courses = user.courses_joined.all()

        context.update({
            'profile': profile,
            'user': user,  # Needed for profile_card.html
            'enrolled_courses': enrolled_courses,
        })
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    form_class = ProfileForm
    template_name = 'students/student/profile_edit.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user.profile

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully')
        return super().form_valid(form)


class ProfilePhotoUpdateView(LoginRequiredMixin, UpdateView):
    form_class = ProfilePhotoForm
    template_name = 'includes/profile_photo_form.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user.profile

    def form_valid(self, form):
        messages.success(self.request, 'Profile photo updated successfully')
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        if 'remove' in request.POST:
            profile = self.get_object()
            profile.photo.delete(save=True)
            messages.success(request, 'Profile photo removed successfully')
            return redirect(self.success_url)
        return super().post(request, *args, **kwargs)


class CustomPasswordResetView(SuccessMessageMixin, PasswordResetView):
    template_name = 'courses/registration/password_reset.html'
    email_template_name = 'courses/registration/password_reset_email.html'
    subject_template_name = 'courses/registration/password_reset_subject.txt'
    form_class = PasswordResetForm
    success_url = reverse_lazy('password_reset_done')
    success_message = "We've emailed you instructions for setting your password."

    def form_valid(self, form):
        email = form.cleaned_data['email']
        associated_users = form.get_users(email)
        for user in associated_users:
            context = {
                'email': user.email,
                'domain': self.request.get_host(),
                'site_name': 'KnowledgeCurve',
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': default_token_generator.make_token(user),
                'protocol': 'https' if self.request.is_secure() else 'http',
            }
            subject = render_to_string(self.subject_template_name, context)
            email_content = render_to_string(self.email_template_name, context)
            send_mail(
                subject.strip(),
                email_content,
                # settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        return super().form_valid(form)


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'courses/registration/password_reset_done.html'


class CustomPasswordResetConfirmView(SuccessMessageMixin, PasswordResetConfirmView):
    template_name = 'courses/registration/password_reset_confirm.html'
    form_class = SetPasswordForm
    success_url = reverse_lazy('password_reset_complete')
    success_message = "Your password has been successfully reset."


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'students/registration/password_reset_complete.html'


class ProgressDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'students/progress.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['completed_lessons'] = CompletedContent.objects.filter(user=self.request.user)
        return context


class StudentCompleteContentView(LoginRequiredMixin, View):
    def post(self, request, content_id):
        try:
            content = Content.objects.get(id=content_id)
            # Check if user is enrolled in the course
            if not request.user.courses_joined.filter(id=content.module.course.id).exists():
                return JsonResponse({'status': 'error', 'message': 'Not enrolled'}, status=403)

            # Toggle completion status
            completed, created = CompletedContent.objects.get_or_create(
                user=request.user,
                content=content
            )
            if not created:
                completed.delete()
                return JsonResponse({'status': 'success', 'action': 'removed'})
            return JsonResponse({'status': 'success', 'action': 'added'})
        except Content.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Content not found'}, status=404)


class StudentCompleteModuleView(LoginRequiredMixin, View):
    def post(self, request, module_id):
        try:
            module = Module.objects.get(id=module_id)
            # Check enrollment
            if not request.user.courses_joined.filter(id=module.course.id).exists():
                return JsonResponse({'status': 'error', 'message': 'Not enrolled'}, status=403)

            # Mark all contents as complete
            contents = module.contents.all()
            for content in contents:
                CompletedContent.objects.get_or_create(
                    user=request.user,
                    content=content
                )
            return JsonResponse({'status': 'success'})
        except Module.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Module not found'}, status=404)