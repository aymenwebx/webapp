from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('parent', 'Parent'),
    )
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='student'
    )
    student_id = models.CharField(max_length=20, blank=True, null=True)
    teacher_subject = models.CharField(max_length=100, blank=True, null=True)
    parent_phone = models.CharField(max_length=20, blank=True, null=True)
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='accounts_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='accounts_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    photo = models.ImageField(
        upload_to='users/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name='Profile photo'
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='Biography'
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    def __str__(self):
        return f'Profile of {self.user.username}'

    @property
    def full_name(self):
        return f'{self.user.first_name} {self.user.last_name}'

    @property
    def username(self):
        return self.user.username
