from django.contrib.auth import get_user_model
from django.db import models
from django.utils.timezone import now

from .querysets import PostQuerySet

User = get_user_model()


class MetaFields(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        null=False,
        blank=False,
        verbose_name='Добавлено'
    )
    is_published = models.BooleanField(
        default=True,
        null=False,
        blank=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )

    class Meta:
        abstract = True


class TitleField(models.Model):
    title = models.CharField(
        max_length=256,
        null=False,
        blank=False,
        verbose_name='Заголовок'
    )

    class Meta:
        abstract = True


class Category(MetaFields, TitleField):
    description = models.TextField(
        null=False,
        blank=False,
        verbose_name='Описание'
    )
    slug = models.SlugField(
        unique=True,
        null=False,
        blank=False,
        verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL; '
        'разрешены символы латиницы, цифры, дефис и подчёркивание.'
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Location(MetaFields):
    name = models.CharField(
        max_length=256,
        null=False,
        blank=False,
        verbose_name='Название места'
    )


    def __str__(self):
        return self.name


    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'


class Post(MetaFields, TitleField):
    objects = models.Manager()
    posts = PostQuerySet.as_manager()

    text = models.TextField(
        null=False,
        blank=False,
        verbose_name='Текст'
    )
    pub_date = models.DateTimeField(
        null=False,
        blank=True,
        default=now,
        verbose_name='Дата и время публикации',
        help_text='Если установить дату и время в будущем — '
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
        null=False,
        blank=False,
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
        # ON DELETE SET NULL требует отсутствия NOT NULL на поле
        # требование на обязательность заполнения обеспечим через blank
        # осознавая, что оно затронет только формы, а не поле БД
        null=True,
        blank=False,
        verbose_name='Категория'
    )

    class Meta:
        ordering = ('-pub_date',)
        default_manager_name = 'objects'

        default_related_name = 'posts'
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'


class Comment(MetaFields):
    text = models.TextField(
        null=False,
        blank=False,
        verbose_name='Текст комментария'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        verbose_name='Пост',
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        verbose_name='Автор'
    )

    class Meta:
        ordering = ('created_at',)

        default_related_name = 'comments'
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'