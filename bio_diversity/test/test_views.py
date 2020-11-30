from django.test import tag
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


class TestInstDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = BioFactoryFloor.InstFactory()
        self.test_url = reverse_lazy('bio_diversity:details_inst', args=[self.instance.pk, ])
        self.expected_template = 'bio_diversity/bio_details.html'
        self.user = self.get_and_login_user()

    @tag("Inst", "details_inst", "view")
    def test_view_class(self):
        self.assert_inheritance(views.InstDetails, CommonDetails)

    @tag("Inst", "details_inst", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
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

    @tag("Inst", "details_inst", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:details_inst", f"/en/bio_diversity/details/inst/{self.instance.pk}/", [self.instance.pk])


class TestInstListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('bio_diversity:list_inst')
        self.expected_template = 'shared_models/shared_filter.html'
        self.user = self.get_and_login_user()

    @tag("Inst", "list_inst", "view")
    def test_view_class(self):
        self.assert_inheritance(views.InstList, CommonList)

    @tag("Inst", "list_inst", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        # self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Inst", "list_inst",  "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:list_inst", f"/en/bio_diversity/list/inst/")


class InstUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = BioFactoryFloor.InstFactory()
        self.test_url = reverse_lazy('bio_diversity:update_inst', args=[self.instance.pk, ])
        self.expected_template = 'shared_models/shared_models_update_form.html'
        self.user = self.get_and_login_user(in_group="bio_diversity_admin")

    @tag("Inst", "update_inst", "view")
    def test_view_class(self):
        self.assert_inheritance(views.InstUpdate, CommonUpdate)

    @tag("Inst", "update_inst", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        # self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Inst", "update_inst", "submit")
    def test_submit(self):
        data = BioFactoryFloor.InstFactory.build_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Inst", "update_inst", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:update_inst", f"/en/bio_diversity/update/inst/{self.instance.pk}/", \
                                [self.instance.pk])


class TestInstcDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = BioFactoryFloor.InstcFactory()
        self.test_url = reverse_lazy('bio_diversity:details_instc', args=[self.instance.pk, ])
        self.expected_template = 'bio_diversity/bio_details.html'
        self.user = self.get_and_login_user()

    @tag("Instc", "details_instc", "view")
    def test_view_class(self):
        self.assert_inheritance(views.InstcDetails, CommonDetails)

    @tag("Instc", "details_instc", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
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

    @tag("Instc", "details_instc", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:details_instc", f"/en/bio_diversity/details/instc/{self.instance.pk}/", [self.instance.pk])


class TestInstcListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('bio_diversity:list_instc')
        self.expected_template = 'shared_models/shared_filter.html'
        self.user = self.get_and_login_user()

    @tag("Instc", "list_instc", "view")
    def test_view_class(self):
        self.assert_inheritance(views.InstcList, CommonList)

    @tag("Instc", "list_instc", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        # self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Instc", "list_instc",  "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:list_instc", f"/en/bio_diversity/list/instc/")


class InstcUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = BioFactoryFloor.InstcFactory()
        self.test_url = reverse_lazy('bio_diversity:update_instc', args=[self.instance.pk, ])
        self.expected_template = 'shared_models/shared_models_update_form.html'
        self.user = self.get_and_login_user(in_group="bio_diversity_admin")

    @tag("Instc", "update_instc", "view")
    def test_view_class(self):
        self.assert_inheritance(views.InstcUpdate, CommonUpdate)

    @tag("Instc", "update_instc", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        # self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Instc", "update_instc", "submit")
    def test_submit(self):
        data = BioFactoryFloor.InstcFactory.build_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Instc", "update_instc", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:update_instc", f"/en/bio_diversity/update/instc/{self.instance.pk}/", \
                                [self.instance.pk])


class TestInstdDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = BioFactoryFloor.InstdFactory()
        self.test_url = reverse_lazy('bio_diversity:details_instd', args=[self.instance.pk, ])
        self.expected_template = 'bio_diversity/bio_details.html'
        self.user = self.get_and_login_user()

    @tag("Instd", "details_instd", "view")
    def test_view_class(self):
        self.assert_inheritance(views.InstdDetails, CommonDetails)

    @tag("Instd", "details_instd", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
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

    @tag("Instd", "details_instd", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:details_instd", f"/en/bio_diversity/details/instd/{self.instance.pk}/", [self.instance.pk])


class TestInstdListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('bio_diversity:list_instd')
        self.expected_template = 'shared_models/shared_filter.html'
        self.user = self.get_and_login_user()

    @tag("Instd", "list_instd", "view")
    def test_view_class(self):
        self.assert_inheritance(views.InstdList, CommonList)

    @tag("Instd", "list_instd", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        # self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Instd", "list_instd",  "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:list_instd", f"/en/bio_diversity/list/instd/")


class InstdUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = BioFactoryFloor.InstdFactory()
        self.test_url = reverse_lazy('bio_diversity:update_instd', args=[self.instance.pk, ])
        self.expected_template = 'shared_models/shared_models_update_form.html'
        self.user = self.get_and_login_user(in_group="bio_diversity_admin")

    @tag("Instd", "update_instd", "view")
    def test_view_class(self):
        self.assert_inheritance(views.InstdUpdate, CommonUpdate)

    @tag("Instd", "update_instd", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        # self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Instd", "update_instd", "submit")
    def test_submit(self):
        data = BioFactoryFloor.InstdFactory.build_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Instd", "update_instd", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:update_instd", f"/en/bio_diversity/update/instd/{self.instance.pk}/", \
                                [self.instance.pk])


class TestInstdcDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = BioFactoryFloor.InstdcFactory()
        self.test_url = reverse_lazy('bio_diversity:details_instdc', args=[self.instance.pk, ])
        self.expected_template = 'bio_diversity/bio_details.html'
        self.user = self.get_and_login_user()

    @tag("Instdc", "details_instdc", "view")
    def test_view_class(self):
        self.assert_inheritance(views.InstdcDetails, CommonDetails)

    @tag("Instdc", "details_instdc", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
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

    @tag("Instdc", "details_instdc", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:details_instdc", f"/en/bio_diversity/details/instdc/{self.instance.pk}/", [self.instance.pk])


class TestInstdcListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('bio_diversity:list_instdc')
        self.expected_template = 'shared_models/shared_filter.html'
        self.user = self.get_and_login_user()

    @tag("Instdc", "list_instdc", "view")
    def test_view_class(self):
        self.assert_inheritance(views.InstcList, CommonList)

    @tag("Instdc", "list_instdc", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        # self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Instdc", "list_instdc",  "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:list_instdc", f"/en/bio_diversity/list/instdc/")


class InstdcUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = BioFactoryFloor.InstdcFactory()
        self.test_url = reverse_lazy('bio_diversity:update_instdc', args=[self.instance.pk, ])
        self.expected_template = 'shared_models/shared_models_update_form.html'
        self.user = self.get_and_login_user(in_group="bio_diversity_admin")

    @tag("Instdc", "update_instdc", "view")
    def test_view_class(self):
        self.assert_inheritance(views.InstcUpdate, CommonUpdate)

    @tag("Instdc", "update_instdc", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        # self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Instdc", "update_instdc", "submit")
    def test_submit(self):
        data = BioFactoryFloor.InstdcFactory.build_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Instdc", "update_instdc", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("bio_diversity:update_instdc", f"/en/bio_diversity/update/instdc/{self.instance.pk}/", \
                                [self.instance.pk])

