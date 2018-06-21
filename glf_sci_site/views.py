from django.views.generic import TemplateView

class HomePage(TemplateView):
    template_name='index.html'

class Contact(TemplateView):
    template_name='contact.html'

class Oceanography(TemplateView):
    template_name='oceanography.html'
