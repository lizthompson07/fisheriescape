from django.test import tag

from django.urls import reverse_lazy
from django.test import TestCase
from django.utils.translation import activate

from .common_views import CommonCreateTest

from bio_diversity import views, forms, models

from . import BioFactoryFloor


@tag('Inst', 'create')
class TestInstCreate(CommonCreateTest, TestCase):

    def setUp(self):
        super().setUp()

        self.data = BioFactoryFloor.InstFactory.build_valid_data()
        self.test_url = reverse_lazy('bio_diversity:create_inst')

        # Since this is intended to be used as a pop-out form, the html file should start with an underscore
        self.test_expected_template = 'shared_models/shared_entry_form.html'
        # successful create returns user to list view
        self.expected_success_url = reverse_lazy('bio_diversity:list_inst')

        self.expected_view = views.InstCreate
        self.expected_form = forms.InstForm


@tag('Instc', 'create')
class TestInstcCreate(CommonCreateTest, TestCase):

    def setUp(self):
        super().setUp()

        self.data = BioFactoryFloor.InstcFactory.build_valid_data()
        self.test_url = reverse_lazy('bio_diversity:create_instc')

        # Since this is intended to be used as a pop-out form, the html file should start with an underscore
        self.test_expected_template = 'shared_models/shared_entry_form.html'

        # successful create returns user to list view
        self.expected_success_url = reverse_lazy('bio_diversity:list_instc')

        self.expected_view = views.InstcCreate
        self.expected_form = forms.InstcForm


@tag('Instdc', 'create')
class TestInstdcCreate(CommonCreateTest, TestCase):

    def setUp(self):
        super().setUp()

        self.data = BioFactoryFloor.InstdcFactory.build_valid_data()
        self.test_url = reverse_lazy('bio_diversity:create_instdc')

        # Since this is intended to be used as a pop-out form, the html file should start with an underscore
        self.test_expected_template = 'shared_models/shared_entry_form.html'

        # successful create returns user to list view
        self.expected_success_url = reverse_lazy('bio_diversity:list_instdc')

        self.expected_view = views.InstdcCreate
        self.expected_form = forms.InstdcForm



