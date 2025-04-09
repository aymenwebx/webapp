from django.forms.models import inlineformset_factory
from django.conf import settings
from .models import Course, Module, File, Text, Video, Image, Table
from django import forms

User = settings.AUTH_USER_MODEL

ModuleFormSet = inlineformset_factory(
    Course,
    Module,
    fields=['title', 'description'],
    extra=2,
    can_delete=True,
)


def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.fields['slug'].widget = forms.HiddenInput()
    self.fields['overview'].widget.attrs.update({
        'rows': 6,  # Or 8, 10 etc. to make it taller
    })


class TextForm(forms.ModelForm):
    class Meta:
        model = Text
        fields = ['title', 'content']


class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ['title', 'data']  # Assuming `data` is the field for the table's data


class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['title', 'file']


class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'url']


class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['title', 'file']
