from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path(
        'posts/<int:post_id>/comment/',
        views.CommentCreateView.as_view(),
        name='add_comment'
    ),
    path(
        'posts/<int:post_id>/edit_comment/<int:pk>/',
        views.CommentEditView.as_view(),
        name='edit_comment'
    ),
    path(
        'posts/<int:post_id>/delete/<int:pk>',
        views.CommentDeleteView.as_view(),
        name='delete_comment'
    ),
    path(
        'posts/create/',
        views.PostCreateView.as_view(),
        name='create_post'
    ),
    path(
        'posts/<int:pk>/edit/',
        views.PostEditView.as_view(),
        name='edit_post'
    ),
    path(
        'posts/<int:pk>/delete/',
        views.PostDeleteView.as_view(),
        name='delete_post'
    ),
    path(
        'posts/<int:post_id>/',
        views.PostDetailView.as_view(),
        name='post_detail'
    ),
    path(
        'profile/edit/',
        views.ProfileEditView.as_view(),
        name='edit_profile'
    ),
    path(
        'profile/<slug:username>/',
        views.ProfileView.as_view(),
        name='profile'
    ),
    path(
        'category/<slug:category_slug>/',
        views.CategoryView.as_view(),
        name='category_posts'
    ),
    path(
        '',
        views.IndexView.as_view(),
        name='index'
    )
]
