from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.views.generic.edit import ModelFormMixin
from django.urls import reverse, reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect

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
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        post_id = self.kwargs['post_id']
        subject_post = get_object_or_404(
            Post.objects.join_related_all(),
            pk=post_id
        )
        if subject_post.author != self.request.user:
            subject_post = get_object_or_404(
                Post.objects.join_related_all().filter_valid(),
                pk=post_id
            )
        context['post'] = subject_post
        context['comments'] = Comment.objects.filter(
            post=post_id
        )
        return context

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
    pk_url_kwarg = 'comment_id'


class CommentDeleteView(
    CommentGeneralMixin,
    CheckCommentChangeValidity,
    DeleteView
):
    pk_url_kwarg = 'comment_id'


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
    PostFormMixin,
    PostSuccessRedirectToProfileMixin,
    CheckAuthorMixin,
    DeleteView,
    ModelFormMixin,
):
    pk_url_kwarg = 'post_id'

    # Тут я немного запутался
    # Тут я подмешиваю ModelFormMixin, чтобы заполнять form.instance в шаблоне
    # Метод post он не переопределяет
    # Но если post вот так эксплицитно не определить
    # (а это определение я взял из DeletionMixin)
    # То при нажатии кнопки DeleteView.delete() не будет вызван вообще
    def post(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)


# Классы профилей
class ProfileCreateView(CreateView):
    template_name = 'registration/registration_form.html',
    form_class = UserCreationForm,
    success_url = reverse_lazy('blog:index')


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

    def __init__(self):
        super().__init__()
        self.subject_author = None

    def get_queryset(self):
        self.subject_author = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        author_posts = self.subject_author.posts.join_related_all(
        ).add_comment_count()
        if self.request.user != self.subject_author:
            author_posts = self.subject_author.posts.join_related_all(
            ).filter_valid(
            ).add_comment_count()
        return author_posts

    def get_context_data(self, *, object_list=None, **kwargs):
        return super().get_context_data(**kwargs, profile=self.subject_author)


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

    def get_context_data(self, *, object_list=None, **kwargs):
        return super().get_context_data(
            **kwargs,
            category=get_object_or_404(
                Category,
                slug=self.kwargs['category_slug']
            )
        )


class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = MAX_POSTS_PER_PAGE

    def get_queryset(self):
        return Post.objects.join_related_all(
        ).filter_valid(
        ).add_comment_count()
