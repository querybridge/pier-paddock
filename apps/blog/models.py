from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Post(models.Model):
    """A simple blog post — title, image, body, date.

    Deliberately lightweight (per the demo spec) rather than a full CMS.
    """

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    author = models.CharField(max_length=120, default="The Editors")
    excerpt = models.TextField(blank=True)
    body = models.TextField()
    image = models.ImageField(upload_to="blog/", blank=True, null=True)
    date = models.DateField()
    published = models.BooleanField(default=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:220]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:detail", args=[self.slug])
