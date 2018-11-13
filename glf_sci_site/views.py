from django.views.generic import TemplateView

class IndexView(TemplateView):
    template_name='index.html'

# class Contact(TemplateView):
#     template_name='contact.html'
#
# class Apps(TemplateView):
#     template_name='apps.html'
