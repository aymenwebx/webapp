# Generated by Django 5.0.13 on 2025-04-09 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_user_user_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='student_id',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='user_type',
            field=models.CharField(choices=[('student', 'Student'), ('teacher', 'Teacher'), ('parent', 'Parent')], default='student', max_length=10),
        ),
    ]
