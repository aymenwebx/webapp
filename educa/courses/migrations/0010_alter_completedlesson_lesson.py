# Generated by Django 5.0.13 on 2025-04-03 12:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0009_completedlesson'),
    ]

    operations = [
        migrations.AlterField(
            model_name='completedlesson',
            name='lesson',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.content'),
        ),
    ]
