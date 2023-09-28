from django.views.generic import TemplateView


class StartView(TemplateView):
    template_name = 'massage_clients/index.html'


class Err404View(TemplateView):
    template_name = 'massage_clients/404.html'
