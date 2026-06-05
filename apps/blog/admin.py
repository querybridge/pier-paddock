from django.contrib import admin

from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "date", "published")
    list_filter = ("published",)
    prepopulated_fields = {"slug": ("title",)}
