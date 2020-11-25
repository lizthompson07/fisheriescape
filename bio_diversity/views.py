from django.shortcuts import render
from django.views.generic import TemplateView
from shared_models.views import CommonCreateView

from . import models, forms
# Create your views here.


class IndexTemplateView(TemplateView):
    template_name = 'bio_diversity/index.html'


# CommonCreate Extends the UserPassesTestMixin used to determine if a user has
# has the correct privileges to interact with Creation Views
class CommonCreate(CommonCreateView):
    pass


class CreateInst(CommonCreate):
    form_class = forms.InstForm
    model = models.InstDetCode
    title = "Some title"
