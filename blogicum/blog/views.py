from django.views.generic import (
ListView, CreateView, UpdateView, DeleteView)
from django.views.generic.edit import ModelFormMixin
from django.urls import reverse, reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect


from .models import Post, Comment, Category
from .forms import PostForm, CommentForm, UserChangeInfoForm


MAX_POSTS_PER_PAGE = 10
User = get_user_model()


# Классы комментариев
class CommentFormMixin:
    template_name = 'blog/comment.html'
    model = Comment
    form_class = CommentForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['post_id'] = self.kwargs.get('post_id')
        return kwargs

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs.get('post_id')}
        )


class CommentAuthorizeAuthorMixin:

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        comment_author = Comment.objects.get(
            pk=kwargs.get('pk')
        ).author
        if comment_author != request.user:
            return redirect('blog:post_detail', post_id = kwargs.get('post_id'))
        return super().get(request, *args, **kwargs)


class CommentCreateView(CommentFormMixin, LoginRequiredMixin, CreateView):
    pass


class CommentEditView(CommentFormMixin, CommentAuthorizeAuthorMixin ,LoginRequiredMixin, UpdateView):
    pass


class CommentDeleteView(CommentFormMixin, CommentAuthorizeAuthorMixin ,LoginRequiredMixin, ModelFormMixin, DeleteView):
    # Тут мне я немного запутался
    # Тут я подмешиваю ModelFormMixin, чтобы заполнять form.instance в шаблоне
    # Метод post он не переопределяет
    # Но если post вот так эксплицитно не определить (а это определение я взял из DeletionMixin)
    # То при нажатии кнопки DeleteView.delete() не будет вызван вообще
    def post(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)


# Классы постов
class PostMixin:
    model = Post


class PostFormMixin(PostMixin):
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class PostSuccessRedirectToProfileMixin:
    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user.username})


class PostCreateView(PostFormMixin, PostSuccessRedirectToProfileMixin, LoginRequiredMixin, CreateView):
    pass


class PostEditView(PostFormMixin, LoginRequiredMixin, UpdateView):

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        post_author = Post.objects.get(
            pk=kwargs.get('pk')
        ).author
        if post_author != request.user:
            return redirect('blog:post_detail', post_id=kwargs.get('pk'))
        return super().get(request, *args, **kwargs)


    def get_success_url(self):
        kwargs = self.get_form_kwargs()
        return reverse('blog:post_detail', kwargs={'pk': self.kwargs.get('pk')})


class PostDeleteView(PostFormMixin, PostSuccessRedirectToProfileMixin, ModelFormMixin, LoginRequiredMixin, DeleteView):
    # Тут мне я немного запутался
    # Тут я подмешиваю ModelFormMixin, чтобы заполнять form.instance в шаблоне
    # Метод post он не переопределяет
    # Но если post вот так эксплицитно не определить (а это определение я взял из DeletionMixin)
    # То при нажатии кнопки DeleteView.delete() не будет вызван вообще
    def post(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)


class PostDetailView(CommentFormMixin, CreateView):
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['post'] = get_object_or_404(
            Post.posts.join_related_all(
            ).filter_valid(),
            pk=self.kwargs.get('post_id')
        )
        context['comments'] = Comment.objects.filter(
            post=self.kwargs.get('post_id')
        )
        return context


# Классы профилей
class ProfileEditView(LoginRequiredMixin, UpdateView):
    template_name = 'registration/registration_form.html'
    form_class = UserChangeInfoForm
    success_url = reverse_lazy('blog:index')

    def get_object(self, queryset=None):
        obj = User.objects.get(
            username=self.request.user.username
        )
        return obj


class ProfileView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    ordering = '-pub_date'
    paginate_by = MAX_POSTS_PER_PAGE

    def get_queryset(self):
        subject_username = self.kwargs.get('username')
        subject_user = get_object_or_404(
            User.objects.all(),
            username=subject_username
        )
        order = self.get_ordering()
        queryset = Post.posts.join_related_all(
        ).filter(
            author__username=subject_username
        ).add_comment_count(
        ).order_by(order)
        if self.request.user != subject_user:
            queryset = queryset.filter_valid()
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        subject_username = self.kwargs.get('username')
        subject_user = get_object_or_404(
            User.objects.all(),
            username=subject_username
        )
        context['profile'] = subject_user
        return context


# Классы общего контента блога
class CategoryView(ListView):
    model = Post
    template_name = 'blog/category.html'
    ordering = '-pub_date'
    paginate_by = MAX_POSTS_PER_PAGE

    def get_queryset(self):
        order = self.get_ordering()
        category_slug = self.kwargs.get('category_slug')
        queryset = Post.posts.join_related_all(
        ).filter_valid(
        ).filter(
            category__slug=category_slug
        ).add_comment_count(
        ).order_by(order)
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['category'] = get_object_or_404(
            Category.objects.values(
                'title',
                'description'
            ).filter(
                is_published=True
            ),
            slug=self.kwargs.get('category_slug')
        )
        return context


class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    ordering = '-pub_date'
    paginate_by = MAX_POSTS_PER_PAGE

    def get_queryset(self):
        order = self.get_ordering()
        queryset = Post.posts.join_related_all(
        ).filter_valid(
        ).add_comment_count(
        ).order_by(order)
        return queryset