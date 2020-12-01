from django.test import tag, RequestFactory
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from faker import Faker

from bio_diversity.test import BioFactoryFloor
# from cruises.test.common_tests import CommonCruisesTest as CommonTest
from shared_models.test.common_tests import CommonTest

# from bio_diversity.models import Cruise
# from shared_models.test.SharedModelsFactoryFloor import CruiseFactory
from bio_diversity.views import CommonCreate, CommonDetails, CommonList, CommonUpdate
from .. import views, models

faker = Faker()


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
class TestCommonCreate(CommonTest):

    def setUp(self):
        self.view = MockCommonCreate()

    def test_get_init(self):
        # test created_by field auto population
        req_faq = RequestFactory()
        request = req_faq.get(None)

        # create and login a user to be expected by the inital function
        user = self.get_and_login_user(in_group="bio_diversity_admin")
        request.user = user

        setup_view(self.view, request)

        init = self.view.get_initial()
        self.assertIsNotNone(init)
        self.assertEqual(init['created_by'], user.username)



@tag("Inst")
class TestInstCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = BioFactoryFloor.InstFactory()
        self.test_url = reverse_lazy('bio_diversity:create_inst')
        self.expected_template = 'shared_models/shared_entry_form.html'
        self.user = self.get_and_login_user(in_group="bio_diversity_admin")

    def test_view_class(self):
        self.assert_inheritance(views.InstCreate, CommonCreate)

    def test_view(self):
        self.assert_valid_url(self.test_url)
        # self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    def test_submit(self):
        data = BioFactoryFloor.InstFactory.build_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:create_inst", "/en/bio_diversity/create/inst/")


@tag("Inst")
class TestInstDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = BioFactoryFloor.InstFactory()
        self.test_url = reverse_lazy('bio_diversity:details_inst', args=[self.instance.pk, ])
        self.expected_template = 'bio_diversity/bio_details.html'
        self.user = self.get_and_login_user()

    def test_view_class(self):
        self.assert_inheritance(views.InstDetails, CommonDetails)

    def test_view(self):
        self.assert_valid_url(self.test_url)
        # self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    # not sure how to do this bit
    # @tag("Inst", "details_inst", "context")
    # def test_context(self):
    #     context_vars = [
    #         "instc",
    #         "serial_number",
    #         "comments",
    #         "created_by",
    #         "created_date",
    #     ]
    #     self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:details_inst", f"/en/bio_diversity/details/inst/{self.instance.pk}/", [self.instance.pk])


@tag("Inst")
class TestInstListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('bio_diversity:list_inst')
        self.expected_template = 'shared_models/shared_filter.html'
        self.user = self.get_and_login_user()

    def test_view_class(self):
        self.assert_inheritance(views.InstList, CommonList)

    def test_view(self):
        self.assert_valid_url(self.test_url)
        # self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:list_inst", f"/en/bio_diversity/list/inst/")


@tag("Inst")
class InstUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = BioFactoryFloor.InstFactory()
        self.test_url = reverse_lazy('bio_diversity:update_inst', args=[self.instance.pk, ])
        self.expected_template = 'shared_models/shared_models_update_form.html'
        self.user = self.get_and_login_user(in_group="bio_diversity_admin")

    def test_view_class(self):
        self.assert_inheritance(views.InstUpdate, CommonUpdate)

    def test_view(self):
        self.assert_valid_url(self.test_url)
        # self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    def test_submit(self):
        data = BioFactoryFloor.InstFactory.build_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:update_inst", f"/en/bio_diversity/update/inst/{self.instance.pk}/", \
                                [self.instance.pk])


@tag("Instc")
class TestInstcCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = BioFactoryFloor.InstcFactory()
        self.test_url = reverse_lazy('bio_diversity:create_instc')
        self.expected_template = 'shared_models/shared_entry_form.html'
        self.user = self.get_and_login_user(in_group="bio_diversity_admin")

    def test_view_class(self):
        self.assert_inheritance(views.InstcCreate, CommonCreate)

    def test_view(self):
        self.assert_valid_url(self.test_url)
        # self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    def test_submit(self):
        data = BioFactoryFloor.InstcFactory.build_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:create_instc", "/en/bio_diversity/create/instc/")


@tag("Instc")
class TestInstcDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = BioFactoryFloor.InstcFactory()
        self.test_url = reverse_lazy('bio_diversity:details_instc', args=[self.instance.pk, ])
        self.expected_template = 'bio_diversity/bio_details.html'
        self.user = self.get_and_login_user()

    def test_view_class(self):
        self.assert_inheritance(views.InstcDetails, CommonDetails)

    def test_view(self):
        self.assert_valid_url(self.test_url)
        # self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    # not sure how to do this bit
    # @tag("Inst", "details_inst", "context")
    # def test_context(self):
    #     context_vars = [
    #         "instc",
    #         "serial_number",
    #         "comments",
    #         "created_by",
    #         "created_date",
    #     ]
    #     self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:details_instc", f"/en/bio_diversity/details/instc/{self.instance.pk}/", [self.instance.pk])


@tag("Instc")
class TestInstcListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('bio_diversity:list_instc')
        self.expected_template = 'shared_models/shared_filter.html'
        self.user = self.get_and_login_user()

    def test_view_class(self):
        self.assert_inheritance(views.InstcList, CommonList)

    def test_view(self):
        self.assert_valid_url(self.test_url)
        # self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:list_instc", f"/en/bio_diversity/list/instc/")


@tag("Instc")
class InstcUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = BioFactoryFloor.InstcFactory()
        self.test_url = reverse_lazy('bio_diversity:update_instc', args=[self.instance.pk, ])
        self.expected_template = 'shared_models/shared_models_update_form.html'
        self.user = self.get_and_login_user(in_group="bio_diversity_admin")

    def test_view_class(self):
        self.assert_inheritance(views.InstcUpdate, CommonUpdate)

    def test_view(self):
        self.assert_valid_url(self.test_url)
        # self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    def test_submit(self):
        data = BioFactoryFloor.InstcFactory.build_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:update_instc", f"/en/bio_diversity/update/instc/{self.instance.pk}/", \
                                [self.instance.pk])


@tag("Instd")
class TestInstdCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = BioFactoryFloor.InstdFactory()
        self.test_url = reverse_lazy('bio_diversity:create_instd')
        self.expected_template = 'shared_models/shared_entry_form.html'
        self.user = self.get_and_login_user(in_group="bio_diversity_admin")

    def test_view_class(self):
        self.assert_inheritance(views.InstdCreate, CommonCreate)

    def test_view(self):
        self.assert_valid_url(self.test_url)
        # self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    def test_submit(self):
        data = BioFactoryFloor.InstdFactory.build_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:create_instd", "/en/bio_diversity/create/instd/")


@tag("Instd")
class TestInstdDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = BioFactoryFloor.InstdFactory()
        self.test_url = reverse_lazy('bio_diversity:details_instd', args=[self.instance.pk, ])
        self.expected_template = 'bio_diversity/bio_details.html'
        self.user = self.get_and_login_user()

    def test_view_class(self):
        self.assert_inheritance(views.InstdDetails, CommonDetails)

    def test_view(self):
        self.assert_valid_url(self.test_url)
        # self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    # not sure how to do this bit
    # @tag("Inst", "details_inst", "context")
    # def test_context(self):
    #     context_vars = [
    #         "instc",
    #         "serial_number",
    #         "comments",
    #         "created_by",
    #         "created_date",
    #     ]
    #     self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:details_instd", f"/en/bio_diversity/details/instd/{self.instance.pk}/", [self.instance.pk])


@tag("Instd")
class TestInstdListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('bio_diversity:list_instd')
        self.expected_template = 'shared_models/shared_filter.html'
        self.user = self.get_and_login_user()

    def test_view_class(self):
        self.assert_inheritance(views.InstdList, CommonList)

    def test_view(self):
        self.assert_valid_url(self.test_url)
        # self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:list_instd", f"/en/bio_diversity/list/instd/")


@tag("Instd")
class InstdUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = BioFactoryFloor.InstdFactory()
        self.test_url = reverse_lazy('bio_diversity:update_instd', args=[self.instance.pk, ])
        self.expected_template = 'shared_models/shared_models_update_form.html'
        self.user = self.get_and_login_user(in_group="bio_diversity_admin")

    def test_view_class(self):
        self.assert_inheritance(views.InstdUpdate, CommonUpdate)

    def test_view(self):
        self.assert_valid_url(self.test_url)
        # self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    def test_submit(self):
        data = BioFactoryFloor.InstdFactory.build_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:update_instd", f"/en/bio_diversity/update/instd/{self.instance.pk}/", \
                                [self.instance.pk])


@tag("Instdc")
class TestInstdcCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = BioFactoryFloor.InstdcFactory()
        self.test_url = reverse_lazy('bio_diversity:create_instdc')
        self.expected_template = 'shared_models/shared_entry_form.html'
        self.user = self.get_and_login_user(in_group="bio_diversity_admin")

    def test_view_class(self):
        self.assert_inheritance(views.InstdcCreate, CommonCreate)

    def test_view(self):
        self.assert_valid_url(self.test_url)
        # self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    def test_submit(self):
        data = BioFactoryFloor.InstdcFactory.build_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:create_instdc", "/en/bio_diversity/create/instdc/")


@tag("Instdc")
class TestInstdcDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = BioFactoryFloor.InstdcFactory()
        self.test_url = reverse_lazy('bio_diversity:details_instdc', args=[self.instance.pk, ])
        self.expected_template = 'bio_diversity/bio_details.html'
        self.user = self.get_and_login_user()

    def test_view_class(self):
        self.assert_inheritance(views.InstdcDetails, CommonDetails)

    def test_view(self):
        self.assert_valid_url(self.test_url)
        # self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    # not sure how to do this bit
    # @tag("Inst", "details_inst", "context")
    # def test_context(self):
    #     context_vars = [
    #         "instc",
    #         "serial_number",
    #         "comments",
    #         "created_by",
    #         "created_date",
    #     ]
    #     self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:details_instdc", f"/en/bio_diversity/details/instdc/{self.instance.pk}/", [self.instance.pk])


@tag("Instdc")
class TestInstdcListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('bio_diversity:list_instdc')
        self.expected_template = 'shared_models/shared_filter.html'
        self.user = self.get_and_login_user()

    def test_view_class(self):
        # view
        self.assert_inheritance(views.InstcList, CommonList)

    def test_view(self):
        # access
        self.assert_valid_url(self.test_url)
        # self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    def test_correct_url(self):
        # correct url
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:list_instdc", f"/en/bio_diversity/list/instdc/")


@tag("Instdc")
class InstdcUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = BioFactoryFloor.InstdcFactory()
        self.test_url = reverse_lazy('bio_diversity:update_instdc', args=[self.instance.pk, ])
        self.expected_template = 'shared_models/shared_models_update_form.html'
        self.user = self.get_and_login_user(in_group="bio_diversity_admin")

    def test_view_class(self):
        self.assert_inheritance(views.InstcUpdate, CommonUpdate)

    def test_view(self):
        self.assert_valid_url(self.test_url)
        # self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    def test_submit(self):
        data = BioFactoryFloor.InstdcFactory.build_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:update_instdc", f"/en/bio_diversity/update/instdc/{self.instance.pk}/", \
                                [self.instance.pk])






@tag("Orga")
class TestOrgaCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = BioFactoryFloor.OrgaFactory()
        self.test_url = reverse_lazy('bio_diversity:create_orga')
        self.expected_template = 'shared_models/shared_entry_form.html'
        self.user = self.get_and_login_user(in_group="bio_diversity_admin")

    def test_view_class(self):
        self.assert_inheritance(views.OrgaCreate, CommonCreate)

    def test_view(self):
        self.assert_valid_url(self.test_url)
        # self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    def test_submit(self):
        data = BioFactoryFloor.OrgaFactory.build_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:create_orga", "/en/bio_diversity/create/orga/")


@tag("Orga")
class TestOrgaDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = BioFactoryFloor.OrgaFactory()
        self.test_url = reverse_lazy('bio_diversity:details_orga', args=[self.instance.pk, ])
        self.expected_template = 'bio_diversity/bio_details.html'
        self.user = self.get_and_login_user()

    def test_view_class(self):
        self.assert_inheritance(views.OrgaDetails, CommonDetails)

    def test_view(self):
        self.assert_valid_url(self.test_url)
        # self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    # not sure how to do this bit
    # @tag("Inst", "details_inst", "context")
    # def test_context(self):
    #     context_vars = [
    #         "instc",
    #         "serial_number",
    #         "comments",
    #         "created_by",
    #         "created_date",
    #     ]
    #     self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:details_orga", f"/en/bio_diversity/details/orga/{self.instance.pk}/", [self.instance.pk])


@tag("Orga")
class TestOrgaListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('bio_diversity:list_orga')
        self.expected_template = 'shared_models/shared_filter.html'
        self.user = self.get_and_login_user()

    def test_view_class(self):
        # view
        self.assert_inheritance(views.InstcList, CommonList)

    def test_view(self):
        # access
        self.assert_valid_url(self.test_url)
        # self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    def test_correct_url(self):
        # correct url
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:list_orga", f"/en/bio_diversity/list/orga/")


@tag("Orga")
class OrgaUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = BioFactoryFloor.OrgaFactory()
        self.test_url = reverse_lazy('bio_diversity:update_orga', args=[self.instance.pk, ])
        self.expected_template = 'shared_models/shared_models_update_form.html'
        self.user = self.get_and_login_user(in_group="bio_diversity_admin")

    def test_view_class(self):
        self.assert_inheritance(views.InstcUpdate, CommonUpdate)

    def test_view(self):
        self.assert_valid_url(self.test_url)
        # self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    def test_submit(self):
        data = BioFactoryFloor.OrgaFactory.build_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:update_orga", f"/en/bio_diversity/update/orga/{self.instance.pk}/", \
                                [self.instance.pk])



@tag("Proga")
class TestProgaCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = BioFactoryFloor.ProgaFactory()
        self.test_url = reverse_lazy('bio_diversity:create_proga')
        self.expected_template = 'shared_models/shared_entry_form.html'
        self.user = self.get_and_login_user(in_group="bio_diversity_admin")

    def test_view_class(self):
        self.assert_inheritance(views.ProgaCreate, CommonCreate)

    def test_view(self):
        self.assert_valid_url(self.test_url)
        # self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    def test_submit(self):
        data = BioFactoryFloor.ProgaFactory.build_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:create_proga", "/en/bio_diversity/create/proga/")


@tag("Proga")
class TestProgaDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = BioFactoryFloor.ProgaFactory()
        self.test_url = reverse_lazy('bio_diversity:details_proga', args=[self.instance.pk, ])
        self.expected_template = 'bio_diversity/bio_details.html'
        self.user = self.get_and_login_user()

    def test_view_class(self):
        self.assert_inheritance(views.ProgaDetails, CommonDetails)

    def test_view(self):
        self.assert_valid_url(self.test_url)
        # self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    # not sure how to do this bit
    # @tag("Inst", "details_inst", "context")
    # def test_context(self):
    #     context_vars = [
    #         "instc",
    #         "serial_number",
    #         "comments",
    #         "created_by",
    #         "created_date",
    #     ]
    #     self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:details_proga", f"/en/bio_diversity/details/proga/{self.instance.pk}/", [self.instance.pk])


@tag("Proga")
class TestProgaListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('bio_diversity:list_proga')
        self.expected_template = 'shared_models/shared_filter.html'
        self.user = self.get_and_login_user()

    def test_view_class(self):
        # view
        self.assert_inheritance(views.InstcList, CommonList)

    def test_view(self):
        # access
        self.assert_valid_url(self.test_url)
        # self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    def test_correct_url(self):
        # correct url
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:list_proga", f"/en/bio_diversity/list/proga/")


@tag("Proga")
class ProgaUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = BioFactoryFloor.ProgaFactory()
        self.test_url = reverse_lazy('bio_diversity:update_proga', args=[self.instance.pk, ])
        self.expected_template = 'shared_models/shared_models_update_form.html'
        self.user = self.get_and_login_user(in_group="bio_diversity_admin")

    def test_view_class(self):
        self.assert_inheritance(views.InstcUpdate, CommonUpdate)

    def test_view(self):
        self.assert_valid_url(self.test_url)
        # self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    def test_submit(self):
        data = BioFactoryFloor.ProgaFactory.build_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:update_proga", f"/en/bio_diversity/update/proga/{self.instance.pk}/", \
                                [self.instance.pk])




@tag("Protc")
class TestProtcCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = BioFactoryFloor.ProtcFactory()
        self.test_url = reverse_lazy('bio_diversity:create_protc')
        self.expected_template = 'shared_models/shared_entry_form.html'
        self.user = self.get_and_login_user(in_group="bio_diversity_admin")

    def test_view_class(self):
        self.assert_inheritance(views.ProtcCreate, CommonCreate)

    def test_view(self):
        self.assert_valid_url(self.test_url)
        # self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    def test_submit(self):
        data = BioFactoryFloor.ProtcFactory.build_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:create_protc", "/en/bio_diversity/create/protc/")


@tag("Protc")
class TestProtcDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = BioFactoryFloor.ProtcFactory()
        self.test_url = reverse_lazy('bio_diversity:details_protc', args=[self.instance.pk, ])
        self.expected_template = 'bio_diversity/bio_details.html'
        self.user = self.get_and_login_user()

    def test_view_class(self):
        self.assert_inheritance(views.ProtcDetails, CommonDetails)

    def test_view(self):
        self.assert_valid_url(self.test_url)
        # self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    # not sure how to do this bit
    # @tag("Inst", "details_inst", "context")
    # def test_context(self):
    #     context_vars = [
    #         "instc",
    #         "serial_number",
    #         "comments",
    #         "created_by",
    #         "created_date",
    #     ]
    #     self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:details_protc", f"/en/bio_diversity/details/protc/{self.instance.pk}/", [self.instance.pk])


@tag("Protc")
class TestProtcListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('bio_diversity:list_protc')
        self.expected_template = 'shared_models/shared_filter.html'
        self.user = self.get_and_login_user()

    def test_view_class(self):
        # view
        self.assert_inheritance(views.InstcList, CommonList)

    def test_view(self):
        # access
        self.assert_valid_url(self.test_url)
        # self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    def test_correct_url(self):
        # correct url
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:list_protc", f"/en/bio_diversity/list/protc/")


@tag("Protc")
class ProtcUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = BioFactoryFloor.ProtcFactory()
        self.test_url = reverse_lazy('bio_diversity:update_protc', args=[self.instance.pk, ])
        self.expected_template = 'shared_models/shared_models_update_form.html'
        self.user = self.get_and_login_user(in_group="bio_diversity_admin")

    def test_view_class(self):
        self.assert_inheritance(views.InstcUpdate, CommonUpdate)

    def test_view(self):
        self.assert_valid_url(self.test_url)
        # self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    def test_submit(self):
        data = BioFactoryFloor.ProtcFactory.build_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:update_protc", f"/en/bio_diversity/update/protc/{self.instance.pk}/", \
                                [self.instance.pk])




@tag("Protf")
class TestProtfCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = BioFactoryFloor.ProtfFactory()
        self.test_url = reverse_lazy('bio_diversity:create_protf')
        self.expected_template = 'shared_models/shared_entry_form.html'
        self.user = self.get_and_login_user(in_group="bio_diversity_admin")

    def test_view_class(self):
        self.assert_inheritance(views.ProtfCreate, CommonCreate)

    def test_view(self):
        self.assert_valid_url(self.test_url)
        # self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    def test_submit(self):
        data = BioFactoryFloor.ProtfFactory.build_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:create_protf", "/en/bio_diversity/create/protf/")


@tag("Protf")
class TestProtfDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = BioFactoryFloor.ProtfFactory()
        self.test_url = reverse_lazy('bio_diversity:details_protf', args=[self.instance.pk, ])
        self.expected_template = 'bio_diversity/bio_details.html'
        self.user = self.get_and_login_user()

    def test_view_class(self):
        self.assert_inheritance(views.ProtfDetails, CommonDetails)

    def test_view(self):
        self.assert_valid_url(self.test_url)
        # self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    # not sure how to do this bit
    # @tag("Inst", "details_inst", "context")
    # def test_context(self):
    #     context_vars = [
    #         "instc",
    #         "serial_number",
    #         "comments",
    #         "created_by",
    #         "created_date",
    #     ]
    #     self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)

    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:details_protf", f"/en/bio_diversity/details/protf/{self.instance.pk}/", [self.instance.pk])


@tag("Protf")
class TestProtfListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('bio_diversity:list_protf')
        self.expected_template = 'shared_models/shared_filter.html'
        self.user = self.get_and_login_user()

    def test_view_class(self):
        # view
        self.assert_inheritance(views.InstcList, CommonList)

    def test_view(self):
        # access
        self.assert_valid_url(self.test_url)
        # self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    def test_correct_url(self):
        # correct url
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:list_protf", f"/en/bio_diversity/list/protf/")


@tag("Protf")
class ProtfUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = BioFactoryFloor.ProtfFactory()
        self.test_url = reverse_lazy('bio_diversity:update_protf', args=[self.instance.pk, ])
        self.expected_template = 'shared_models/shared_models_update_form.html'
        self.user = self.get_and_login_user(in_group="bio_diversity_admin")

    def test_view_class(self):
        self.assert_inheritance(views.InstcUpdate, CommonUpdate)

    def test_view(self):
        self.assert_valid_url(self.test_url)
        # self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    def test_submit(self):
        data = BioFactoryFloor.ProtfFactory.build_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:update_protf", f"/en/bio_diversity/update/protf/{self.instance.pk}/", \
                                [self.instance.pk])

