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


