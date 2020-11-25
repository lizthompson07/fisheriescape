from django.test import tag

from django.urls import reverse_lazy, resolve
from django.test import TestCase
from django.utils.translation import activate

from .common_views import CommonCreateTest

from bio_diversity import views, forms, models


@tag('Inst', 'create')
class TestInstCreate(CommonCreateTest, TestCase):
    expected_view = views.CreateInst
    expected_form = forms.InstForm