from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth import login
from .forms import CustomUserCreationForm

from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.contrib.auth import get_user_model

from accounts.models import Profile

User = get_user_model()


class UserRegistrationView(CreateView):
    template_name = 'registration.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        return redirect(self.get_success_url())

class CustomLoginView(LoginView):
    def form_valid(self, form):
        next_page = self.request.GET.get('home', None)  # Get the next page to redirect to
        response = super().form_valid(form)

        if next_page:
            return redirect(next_page)
        elif self.request.user.user_type == 'teacher':
            return redirect('manage_course_list')
        elif self.request.user.user_type == 'student':
            return redirect('course_list')
        else:
            return redirect('home')
