from django.forms.models import inlineformset_factory
from django.conf import settings
from .models import Course, Module


User = settings.AUTH_USER_MODEL

ModuleFormSet = inlineformset_factory(
    Course,
    Module,
    fields=['title', 'description'],
    extra=2,
    can_delete=True,
)


