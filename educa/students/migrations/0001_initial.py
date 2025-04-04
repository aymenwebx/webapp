# Generated by Django 5.0.13 on 2025-03-27 18:32

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ImageField(blank=True, null=True, upload_to='users/%Y/%m/%d/', verbose_name='Profile photo')),
                ('bio', models.TextField(blank=True, max_length=500, null=True, verbose_name='Biography')),
                ('twitter', models.CharField(blank=True, max_length=100, null=True, validators=[django.core.validators.URLValidator()], verbose_name='Twitter profile')),
                ('linkedin', models.CharField(blank=True, max_length=100, null=True, validators=[django.core.validators.URLValidator()], verbose_name='LinkedIn profile')),
                ('website', models.CharField(blank=True, max_length=100, null=True, validators=[django.core.validators.URLValidator()], verbose_name='Personal website')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Profile',
                'verbose_name_plural': 'Profiles',
                'ordering': ['-created'],
            },
        ),
    ]
