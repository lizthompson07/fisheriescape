from django.test import tag
from django.urls import reverse_lazy

from . import SharedModelsFactoryFloor as FactoryFloor
from .common_tests import CommonTest
from .. import models
from .. import views
from ..views import CommonListView, CommonFilterView, CommonUpdateView, CommonDeleteView, CommonCreateView, CommonPopoutFormView


class TestBranchCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('shared_models:branch_new')
        self.expected_template = 'shared_models/generic_form.html'
        self.admin_user = self.get_and_login_user(in_group="travel_admin")

    @tag("branch_new", 'update', "view")
    def test_view_class(self):
        self.assert_inheritance(views.BranchCreateView, CommonCreateView)
        self.assert_inheritance(views.BranchCreateView, views.AdminRequiredMixin)

    @tag("branch_new", 'update', "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.admin_user)

    @tag("branch_new", 'update', "submit")
    def test_submit(self):
        data = FactoryFloor.BranchFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.admin_user)


class TestBranchDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.BranchFactory()
        self.test_url = reverse_lazy('shared_models:branch_delete', kwargs={"pk": self.instance.pk})
        self.expected_template = 'shared_models/generic_confirm_delete.html'
        self.admin_user = self.get_and_login_user(in_group="travel_admin")

    @tag("branch_delete", 'delete', "view")
    def test_view_class(self):
        self.assert_inheritance(views.BranchDeleteView, CommonDeleteView)
        self.assert_inheritance(views.BranchDeleteView, views.AdminRequiredMixin)

    @tag("branch_delete", 'delete', "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.admin_user)

    @tag("branch_delete", 'delete', "submit")
    def test_submit(self):
        data = FactoryFloor.BranchFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.admin_user)

        # for delete views...
        self.assertEqual(models.Branch.objects.filter(pk=self.instance.pk).count(), 0)


class TestBranchListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('shared_models:branch_list')
        self.expected_template = 'shared_models/org_list.html'
        self.admin_user = self.get_and_login_user(in_group="travel_admin")

    @tag("branch_list", 'list', "view")
    def test_view_class(self):
        self.assert_inheritance(views.BranchListView, CommonFilterView)
        self.assert_inheritance(views.BranchListView, views.AdminRequiredMixin)

    @tag("branch_list", 'list', "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.admin_user)

    @tag("branch_list", 'list', "context")
    def test_context(self):
        context_vars = [
            "section",
            "division",
            "branch",
            "region",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.admin_user)


class TestBranchUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.BranchFactory()
        self.test_url = reverse_lazy('shared_models:branch_edit', kwargs={"pk": self.instance.pk})
        self.expected_template = 'shared_models/org_form.html'
        self.admin_user = self.get_and_login_user(in_group="travel_admin")

    @tag("branch_edit", 'update', "view")
    def test_view_class(self):
        self.assert_inheritance(views.BranchUpdateView, CommonUpdateView)
        self.assert_inheritance(views.BranchUpdateView, views.AdminRequiredMixin)

    @tag("branch_edit", 'update', "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.admin_user)

    @tag("branch_edit", 'update', "submit")
    def test_submit(self):
        data = FactoryFloor.BranchFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.admin_user)


class TestDivisionCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('shared_models:division_new')
        self.expected_template = 'shared_models/generic_form.html'
        self.admin_user = self.get_and_login_user(in_group="travel_admin")

    @tag("division_new", 'update', "view")
    def test_view_class(self):
        self.assert_inheritance(views.DivisionCreateView, CommonCreateView)
        self.assert_inheritance(views.DivisionCreateView, views.AdminRequiredMixin)

    @tag("division_new", 'update', "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.admin_user)

    @tag("division_new", 'update', "submit")
    def test_submit(self):
        data = FactoryFloor.DivisionFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.admin_user)


class TestDivisionDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.DivisionFactory()
        self.test_url = reverse_lazy('shared_models:division_delete', kwargs={"pk": self.instance.pk})
        self.expected_template = 'shared_models/generic_confirm_delete.html'
        self.admin_user = self.get_and_login_user(in_group="travel_admin")

    @tag("division_delete", 'delete', "view")
    def test_view_class(self):
        self.assert_inheritance(views.DivisionDeleteView, CommonDeleteView)
        self.assert_inheritance(views.DivisionDeleteView, views.AdminRequiredMixin)

    @tag("division_delete", 'delete', "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.admin_user)

    @tag("division_delete", 'delete', "submit")
    def test_submit(self):
        data = FactoryFloor.DivisionFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.admin_user)

        # for delete views...
        self.assertEqual(models.Division.objects.filter(pk=self.instance.pk).count(), 0)


class TestDivisionListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('shared_models:division_list')
        self.expected_template = 'shared_models/org_list.html'
        self.admin_user = self.get_and_login_user(in_group="travel_admin")

    @tag("division_list", 'list', "view")
    def test_view_class(self):
        self.assert_inheritance(views.DivisionListView, CommonFilterView)
        self.assert_inheritance(views.DivisionListView, views.AdminRequiredMixin)

    @tag("division_list", 'list', "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.admin_user)

    @tag("division_list", 'list', "context")
    def test_context(self):
        context_vars = [
            "section",
            "division",
            "branch",
            "region",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.admin_user)


class TestDivisionUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.DivisionFactory()
        self.test_url = reverse_lazy('shared_models:division_edit', kwargs={"pk": self.instance.pk})
        self.expected_template = 'shared_models/org_form.html'
        self.admin_user = self.get_and_login_user(in_group="travel_admin")

    @tag("division_edit", 'update', "view")
    def test_view_class(self):
        self.assert_inheritance(views.DivisionUpdateView, CommonUpdateView)
        self.assert_inheritance(views.DivisionUpdateView, views.AdminRequiredMixin)

    @tag("division_edit", 'update', "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.admin_user)

    @tag("division_edit", 'update', "submit")
    def test_submit(self):
        data = FactoryFloor.DivisionFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.admin_user)


class TestRegionCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('shared_models:region_new')
        self.expected_template = 'shared_models/generic_form.html'
        self.admin_user = self.get_and_login_user(in_group="travel_admin")

    @tag("region_new", 'update', "view")
    def test_view_class(self):
        self.assert_inheritance(views.RegionCreateView, CommonCreateView)
        self.assert_inheritance(views.RegionCreateView, views.AdminRequiredMixin)

    @tag("region_new", 'update', "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.admin_user)

    @tag("region_new", 'update', "submit")
    def test_submit(self):
        data = FactoryFloor.RegionFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.admin_user)


class TestRegionDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.RegionFactory()
        self.test_url = reverse_lazy('shared_models:region_delete', kwargs={"pk": self.instance.pk})
        self.expected_template = 'shared_models/generic_confirm_delete.html'
        self.admin_user = self.get_and_login_user(in_group="travel_admin")

    @tag("region_delete", 'delete', "view")
    def test_view_class(self):
        self.assert_inheritance(views.RegionDeleteView, CommonDeleteView)
        self.assert_inheritance(views.RegionDeleteView, views.AdminRequiredMixin)

    @tag("region_delete", 'delete', "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.admin_user)

    @tag("region_delete", 'delete', "submit")
    def test_submit(self):
        data = FactoryFloor.RegionFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.admin_user)

        # for delete views...
        self.assertEqual(models.Region.objects.filter(pk=self.instance.pk).count(), 0)


class TestRegionListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('shared_models:region_list')
        self.expected_template = 'shared_models/org_list.html'
        self.admin_user = self.get_and_login_user(in_group="travel_admin")

    @tag("region_list", 'list', "view")
    def test_view_class(self):
        self.assert_inheritance(views.RegionListView, CommonListView)
        self.assert_inheritance(views.RegionListView, views.AdminRequiredMixin)

    @tag("region_list", 'list', "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.admin_user)


class TestRegionUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.RegionFactory()
        self.test_url = reverse_lazy('shared_models:region_edit', kwargs={"pk": self.instance.pk})
        self.expected_template = 'shared_models/org_form.html'
        self.admin_user = self.get_and_login_user(in_group="travel_admin")

    @tag("region_edit", 'update', "view")
    def test_view_class(self):
        self.assert_inheritance(views.RegionUpdateView, CommonUpdateView)
        self.assert_inheritance(views.RegionUpdateView, views.AdminRequiredMixin)

    @tag("region_edit", 'update', "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.admin_user)

    @tag("region_edit", 'update', "submit")
    def test_submit(self):
        data = FactoryFloor.RegionFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.admin_user)


class TestScriptCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('shared_models:script_new')
        self.expected_template = 'shared_models/generic_form.html'
        self.user = self.get_and_login_user(is_superuser=True)

    @tag("Script", "script_new", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ScriptCreateView, CommonCreateView)

    @tag("Script", "script_new", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Script", "script_new", "submit")
    def test_submit(self):
        data = FactoryFloor.ScriptFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("Script", "script_new", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("shared_models:script_new", f"/en/shared/script/new/")


class TestScriptDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ScriptFactory()
        self.test_url = reverse_lazy('shared_models:script_delete', args=[self.instance.pk, ])
        self.expected_template = 'shared_models/generic_confirm_delete.html'
        self.user = self.get_and_login_user(is_superuser=True)

    @tag("Script", "script_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ScriptDeleteView, CommonDeleteView)

    @tag("Script", "script_delete", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Script", "script_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.ScriptFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(models.Script.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("Script", "script_delete", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("shared_models:script_delete", f"/en/shared/script/{self.instance.pk}/delete/", [self.instance.pk])


class TestScriptListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('shared_models:script_list')
        self.expected_template = 'shared_models/script_list.html'
        self.user = self.get_and_login_user(is_superuser=True)

    @tag("Script", "script_list", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ScriptListView, CommonListView)

    @tag("Script", "script_list", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Script", "script_list", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("shared_models:script_list", f"/en/shared/scripts/")


class TestScriptUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ScriptFactory()
        self.test_url = reverse_lazy('shared_models:script_edit', args=[self.instance.pk, ])
        self.expected_template = 'shared_models/generic_form.html'
        self.user = self.get_and_login_user(is_superuser=True)

    @tag("Script", "script_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ScriptUpdateView, CommonUpdateView)

    @tag("Script", "script_edit", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Script", "script_edit", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("shared_models:script_edit", f"/en/shared/script/{self.instance.pk}/edit/", [self.instance.pk])


class TestSectionCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('shared_models:section_new')
        self.expected_template = 'shared_models/generic_form.html'
        self.admin_user = self.get_and_login_user(in_group="travel_admin")

    @tag("section_new", 'update', "view")
    def test_view_class(self):
        self.assert_inheritance(views.SectionCreateView, CommonCreateView)
        self.assert_inheritance(views.SectionCreateView, views.AdminRequiredMixin)

    @tag("section_new", 'update', "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.admin_user)

    @tag("section_new", 'update', "submit")
    def test_submit(self):
        data = FactoryFloor.SectionFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.admin_user)


class TestSectionDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SectionFactory()
        self.test_url = reverse_lazy('shared_models:section_delete', kwargs={"pk": self.instance.pk})
        self.expected_template = 'shared_models/generic_confirm_delete.html'
        self.admin_user = self.get_and_login_user(in_group="travel_admin")

    @tag("section_delete", 'delete', "view")
    def test_view_class(self):
        self.assert_inheritance(views.SectionDeleteView, CommonDeleteView)
        self.assert_inheritance(views.SectionDeleteView, views.AdminRequiredMixin)

    @tag("section_delete", 'delete', "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.admin_user)

    @tag("section_delete", 'delete', "submit")
    def test_submit(self):
        data = FactoryFloor.SectionFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.admin_user)

        # for delete views...
        self.assertEqual(models.Section.objects.filter(pk=self.instance.pk).count(), 0)


class TestSectionListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('shared_models:section_list')
        self.expected_template = 'shared_models/org_list.html'
        self.admin_user = self.get_and_login_user(in_group="travel_admin")

    @tag("section_list", 'list', "view")
    def test_view_class(self):
        self.assert_inheritance(views.SectionListView, CommonFilterView)
        self.assert_inheritance(views.SectionListView, views.AdminRequiredMixin)

    @tag("section_list", 'list', "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.admin_user)

    @tag("section_list", 'list', "context")
    def test_context(self):
        context_vars = [
            "section",
            "division",
            "branch",
            "region",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.admin_user)


class TestSectionUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.SectionFactory()
        self.test_url = reverse_lazy('shared_models:section_edit', kwargs={"pk": self.instance.pk})
        self.expected_template = 'shared_models/org_form.html'
        self.admin_user = self.get_and_login_user(in_group="travel_admin")

    @tag("section_edit", 'update', "view")
    def test_view_class(self):
        self.assert_inheritance(views.SectionUpdateView, CommonUpdateView)
        self.assert_inheritance(views.SectionUpdateView, views.AdminRequiredMixin)

    @tag("section_edit", 'update', "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.admin_user)

    @tag("section_edit", 'update', "submit")
    def test_submit(self):
        data = FactoryFloor.SectionFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.admin_user)


class TestUserFormView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('shared_models:user_new')
        self.expected_template = 'shared_models/generic_popout_form.html'
        self.user = self.get_and_login_user(in_group="projects_admin")

    @tag("User", "user_new", "view")
    def test_view_class(self):
        self.assert_inheritance(views.UserCreateView, CommonPopoutFormView)

    @tag("User", "user_new", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("User", "user_new", "submit")
    def test_submit(self):
        data = FactoryFloor.UserFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("User", "user_new", "correct_url")
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("shared_models:user_new", f"/en/shared/user/new/")
