from django.shortcuts import render
from django.views.generic import TemplateView


class AboutView(TemplateView):
    template_name = 'pages/about.html'


class RulesView(TemplateView):
    template_name = 'pages/rules.html'


def view_404(request, exception=None):
    return render(request, 'pages/404.html', status=404)


def view_500(request):
    return render(request, 'pages/500.html', status=500)


def view_csrf_failure(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)
