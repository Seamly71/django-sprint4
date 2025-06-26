from django.urls import path
from django.conf import settings

from . import views

app_name = 'pages'

urlpatterns = [
    path('about/', views.AboutView.as_view(), name='about'),
    path('rules/', views.RulesView.as_view(), name='rules')
]

if settings.DEBUG:
    urlpatterns += [
        path('404/', views.view_404),
        path('500/', views.view_500),
        path('bad_csrf/', views.view_csrf_failure),
    ]
