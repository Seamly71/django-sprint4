from django.contrib.auth import get_user_model
from django.db import models
from django.utils.timezone import now

from .querysets import PostQuerySet

MAX_TITLE_LENGTH = 30
MAX_DESCRIPTION_LENGTH = 40


User = get_user_model()


class CreatedAtIsPublishedFields(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )
    is_published = models.BooleanField(
        default=True,
        blank=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )

    class Meta:
        abstract = True


class Category(CreatedAtIsPublishedFields):
    title = models.CharField(
        max_length=256,
        verbose_name='Заголовок'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text=
            'Идентификатор страницы для URL; '
            'разрешены символы латиницы, цифры, дефис и подчёркивание.'
    )

    def __str__(self):
        return (
            f'{self.title[:MAX_TITLE_LENGTH]}'
            f' | {self.description[:MAX_DESCRIPTION_LENGTH]}'
        )

    class Meta:
        ordering = ('title',)

        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Location(CreatedAtIsPublishedFields):
    name = models.CharField(
        max_length=256,
        verbose_name='Название места'
    )

    def __str__(self):
        return f'{self.name[:MAX_TITLE_LENGTH]}'

    class Meta:
        ordering = ('name',)

        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'


class Post(CreatedAtIsPublishedFields):
    objects = PostQuerySet.as_manager()

    title = models.CharField(
        max_length=256,
        verbose_name='Заголовок'
    )
    text = models.TextField(
        verbose_name='Текст'
    )
    pub_date = models.DateTimeField(
        blank=True,
        default=now,
        verbose_name='Дата и время публикации',
        help_text=
            'Если установить дату и время в будущем — '
            'можно делать отложенные публикации.'
    )
    image = models.ImageField(
        null=True,
        blank=True,
        upload_to='post_images',
        verbose_name='Изображение поста'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория'
    )

    class Meta:
        ordering = ('-pub_date',)

        default_related_name = 'posts'
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'


class Comment(CreatedAtIsPublishedFields):
    text = models.TextField(
        verbose_name='Текст комментария'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Пост'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария'
    )

    class Meta:
        ordering = ('created_at',)

        default_related_name = 'comments'
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
