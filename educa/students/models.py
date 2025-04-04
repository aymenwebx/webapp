from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import URLValidator

class Profile(models.Model):
    user = models.OneToOneField(
        User,
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

    # Signal to create profile when user is created
    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    # Signal to save profile when user is saved
    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    @receiver(post_save, sender=User)
    def handle_user_profile(sender, instance, **kwargs):
        """Create or update user profile"""
        Profile.objects.get_or_create(user=instance)
        instance.profile.save()

        User.add_to_class('get_profile', lambda u: Profile.objects.get_or_create(user=u)[0])
