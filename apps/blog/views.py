from django.views.generic import DetailView, ListView

from .models import Post


class PostListView(ListView):
    template_name = "blog/blog.html"
    context_object_name = "posts"
    paginate_by = 6

    def get_queryset(self):
        return Post.objects.filter(published=True)


class PostDetailView(DetailView):
    template_name = "blog/blog_details.html"
    context_object_name = "post"

    def get_queryset(self):
        return Post.objects.filter(published=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["recent_posts"] = Post.objects.filter(published=True).exclude(
            pk=self.object.pk
        )[:5]
        return ctx
