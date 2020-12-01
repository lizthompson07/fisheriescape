from django.test import tag

from django.urls import reverse_lazy
from django.test import TestCase, RequestFactory
from django.utils.translation import activate

from .common_views import CommonCreateTest, CommonTest

from bio_diversity import views, forms, models

from . import BioFactoryFloor


# This is used to simulate calling the as_veiw() function normally called in the urls.py
# this will return a view that can then have it's internal methods tested
def setup_view(view, request, *args, **kwargs):

    view.request = request
    view.args = args
    view.kwargs = kwargs
    return view


class MockCommonCreate(views.CommonCreate):
    pass


@tag('CreateCommon')
class TestCommonCreate(CommonTest, TestCase):

    def setUp(self):
        self.view = MockCommonCreate()

    def test_get_init(self):

        req_faq = RequestFactory()
        request = req_faq.get(None)

        # create and login a user to be expected by the inital function
        user = self.login_bio_user()
        request.user = user

        setup_view(self.view, request)

        init = self.view.get_initial()
        self.assertIsNotNone(init)
        self.assertEqual(init['created_by'], user.username)


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


@tag('Instd', 'create')
class TestInstdCreate(CommonCreateTest, TestCase):

    def setUp(self):
        super().setUp()

        self.data = BioFactoryFloor.InstdFactory.build_valid_data()
        self.test_url = reverse_lazy('bio_diversity:create_instd')

        # Since this is intended to be used as a pop-out form, the html file should start with an underscore
        self.test_expected_template = 'shared_models/shared_entry_form.html'

        # successful create returns user to list view
        self.expected_success_url = reverse_lazy('bio_diversity:list_instd')

        self.expected_view = views.InstdCreate
        self.expected_form = forms.InstdForm


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



