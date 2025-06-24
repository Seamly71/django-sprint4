from django.forms import ModelForm, HiddenInput
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404

from .models import Post, Comment


User = get_user_model()


class AuthorSpoofingSafeguardMixin:

    def clean_author(self):
        """Author spoofing safeguard."""

        if self.user != self.cleaned_data['author']:
            raise PermissionDenied
        return self.user


class CommentForm(AuthorSpoofingSafeguardMixin, ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('user')
        self.post = get_object_or_404(
            Post.objects.all(),
            pk=kwargs.get('post_id')
        )
        kwargs.pop('user')
        kwargs.pop('post_id')
        super().__init__(*args, **kwargs)
        self.fields['author'].initial = self.user
        self.fields['post'].initial = self.post

    def clean_post(self):
        """
        Checking if the post is the same that is displayed on the page.

        Necessary measure as this form could allow to comment on hidden posts.
        """
        if self.post != self.cleaned_data['post']:
            raise PermissionDenied
        return self.post

    class Meta:
        model = Comment
        fields = (
            'text',
            'author',
            'post'
        )
        widgets = {
            'author': HiddenInput(),
            'post': HiddenInput()
        }


class PostForm(AuthorSpoofingSafeguardMixin, ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('user')
        kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['author'].initial = self.user

    class Meta:
        model = Post
        fields = (
            'title',
            'text',
            'image',
            'pub_date',
            'category',
            'location',
            'author'
        )
        widgets = {
            'author': HiddenInput()
        }


class UserChangeInfoForm(ModelForm):

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name'
        )


class UserRegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = (
            'email',
            'first_name',
            'last_name'
        )