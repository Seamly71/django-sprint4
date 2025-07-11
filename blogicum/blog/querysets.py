from django.db import models
from django.utils.timezone import now


class PostQuerySet(models.QuerySet):
    def join_related_all(self):
        return self.select_related(
            'author',
            'category',
            'location'
        )

    def filter_valid(self, *, access_to_hidden=False):
        if access_to_hidden:
            return self
        return self.filter(
            category__is_published=True,
            is_published=True,
            pub_date__lte=now()
        )

    def add_comment_count(self):
        return self.annotate(
            comment_count=models.Count('comments')
        ).order_by(
            *self.model._meta.ordering
        )
