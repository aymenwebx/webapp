from django.forms.models import inlineformset_factory
from django.contrib.auth import get_user_model
from .models import Course, Module


User = get_user_model()

ModuleFormSet = inlineformset_factory(
    Course,
    Module,
    fields=['title', 'description'],
    extra=2,
    can_delete=True,
)


