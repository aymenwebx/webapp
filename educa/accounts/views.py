from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth import login
from .forms import UserRegistrationForm

class UserRegistrationView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'account/register.html'
    success_url = reverse_lazy('course_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response