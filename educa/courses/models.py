from django.urls import reverse
from django.utils.text import slugify
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string


from .fields import OrderField
from django.conf import settings


class Subject(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class Course(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
        related_name='courses_created',
        on_delete=models.CASCADE
    )
    subject = models.ForeignKey(
        Subject,
        related_name='courses',
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, unique=True, db_index=True)
    overview = models.TextField()
    published = models.BooleanField(default=False)
    published_date = models.DateTimeField(null=True, blank=True)
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='courses_joined',
        blank=True
    )

    def save(self, *args, **kwargs):
        if not self.slug:  # Auto-generate only if empty
            self.slug = slugify(self.title)
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while Course.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('course_detail', args=[self.slug])
    class Meta:
        ordering = ['-published_date']

    def __str__(self):
        return self.title


class Module(models.Model):
    course = models.ForeignKey(
        Course,
        related_name='modules',
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = OrderField(blank=True, for_fields=['course'])

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.order}. {self.title}'

    def user_progress(self, user):
        total = self.contents.count()
        if total == 0:
            return {'completed': 0, 'total': 0, 'percentage': 0}

        completed = CompletedContent.objects.filter(
            user=user,
            content__module=self
        ).count()

        return {
            'completed': completed,
            'total': total,
            'percentage': int((completed / total) * 100)
        }

class Content(models.Model):
    module = models.ForeignKey(
        Module,
        related_name='contents',
        on_delete=models.CASCADE
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={
            'model__in': ('text', 'video', 'image', 'file')
        },
    )
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    order = OrderField(blank=True, for_fields=['module'])

    class Meta:
        ordering = ['order']

    @property
    def completed_by_user(self):
        return self.completedcontent_set.filter(user=self._request.user).exists()


class ItemBase(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='%(class)s_related',
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    def render(self):
        return render_to_string(
            f'courses/content/{self._meta.model_name}.html',
            {'item': self},
        )


class Text(ItemBase):
    content = models.TextField()


class File(ItemBase):
    file = models.FileField(upload_to='files')


class Image(ItemBase):
    file = models.FileField(upload_to='images')


class Video(ItemBase):
    url = models.URLField()


class CompletedContent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.ForeignKey('Content', on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'content')

    def __str__(self):
        return f"{self.user.username} completed {self.content.item.title}"