from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView
)
from django.utils.timezone import now
from django.urls import reverse, reverse_lazy

from blog.models import Post, Comment, Category, User
from blog.forms import (
    PostForm,
    CommentForm,
    UserChangeInfoForm
)


MAX_POSTS_PER_PAGE = 10


class CheckAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        return self.get_object().author == self.request.user


# Классы комментариев
class CommentGeneralMixin:
    template_name = 'blog/comment.html'
    model = Comment
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            args=[self.kwargs['post_id']]
        )


class CommentFormMixin(CommentGeneralMixin):
    form_class = CommentForm


class CheckCommentChangeValidity(CheckAuthorMixin):

    def test_func(self):
        subject_comment = self.get_object()
        subject_post = get_object_or_404(
            Post,
            pk=self.kwargs['post_id']
        )
        return super().test_func() and subject_comment.post == subject_post


class CommentCreateView(CommentFormMixin, LoginRequiredMixin, CreateView):

    def form_valid(self, form):
        form.instance.post = get_object_or_404(
            Post.objects.all(),
            pk=self.kwargs['post_id']
        )
        form.instance.author = self.request.user
        return super().form_valid(form)


class CommentEditView(
    CommentFormMixin,
    CheckCommentChangeValidity,
    UpdateView
):
    pass


class CommentDeleteView(
    CommentGeneralMixin,
    CheckCommentChangeValidity,
    DeleteView
):
    pass


# Классы постов
class PostFormMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'


class PostSuccessRedirectToProfileMixin:

    def get_success_url(self):
        return reverse(
            'blog:profile',
            args=[self.request.user.username]
        )


class PostCreateView(
    PostFormMixin,
    PostSuccessRedirectToProfileMixin,
    LoginRequiredMixin,
    CreateView
):

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostEditView(PostFormMixin, CheckAuthorMixin, UpdateView):
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            args=[self.kwargs[self.pk_url_kwarg]]
        )

    def handle_no_permission(self):
        return redirect(
            'blog:post_detail',
            post_id=self.kwargs[self.pk_url_kwarg]
        )


class PostDeleteView(
    PostSuccessRedirectToProfileMixin,
    CheckAuthorMixin,
    DeleteView,
):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm()
        context['form'].instance = kwargs['object']
        return context


class PostDetailView(DetailView):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/detail.html'

    def get_object(self, posts=None):
        post = get_object_or_404(
            Post.objects.join_related_all(),
            pk=self.kwargs[self.pk_url_kwarg]
        )
        if (
            post.author != self.request.user and (
                not post.is_published
                or not post.category.is_published
                or post.pub_date > now()
            )
        ):
            raise Http404
        return post

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            form=CommentForm(),
            comments=kwargs['object'].comments.all()
        )


# Классы профилей
class ProfileEditView(LoginRequiredMixin, UpdateView):
    template_name = 'registration/registration_form.html'
    form_class = UserChangeInfoForm
    success_url = reverse_lazy('blog:index')

    def get_object(self, user_arg=None):
        return self.request.user


class ProfileView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = MAX_POSTS_PER_PAGE

    def get_subject_author(self):
        return get_object_or_404(
            User,
            username=self.kwargs['username']
        )

    def get_queryset(self):
        subject_author = self.get_subject_author()
        return subject_author.posts.join_related_all(
        ).filter_valid(
            access_to_hidden=self.request.user == subject_author
        ).add_comment_count()

    def get_context_data(self, *, object_list=None, **kwargs):
        return super().get_context_data(
            **kwargs,
            profile=self.get_subject_author()
        )


# Классы общего контента блога
class CategoryView(ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = MAX_POSTS_PER_PAGE

    def get_queryset(self):
        return get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        ).posts.join_related_all(
        ).filter_valid(
        ).add_comment_count()


class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = MAX_POSTS_PER_PAGE

    def get_queryset(self):
        return Post.objects.join_related_all(
        ).filter_valid(
        ).add_comment_count()
