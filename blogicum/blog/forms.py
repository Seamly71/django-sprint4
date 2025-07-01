from django.forms import ModelForm

from .models import Post, Comment, User


class CommentForm(ModelForm):

    class Meta:
        model = Comment
        fields = (
            'text',
        )


class PostForm(ModelForm):

    class Meta:
        model = Post
        exclude = (
            'author',
        )


class UserChangeInfoForm(ModelForm):

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name'
        )
