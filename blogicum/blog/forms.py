from django.forms import ModelForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Post, Comment


User = get_user_model()


class CommentForm(ModelForm):

    class Meta:
        model = Comment
        fields = (
            'text',
        )


class PostForm(ModelForm):

    class Meta:
        model = Post
        fields = (
            'title',
            'text',
            'image',
            'pub_date',
            'category',
            'location'
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


class UserRegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = (
            'email',
            'first_name',
            'last_name'
        )
