from django.test import tag
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DeleteView

from ihub.test import FactoryFloor
from ihub.test.common_tests import CommonIHubTest as CommonTest
from masterlist import models as ml_models
from shared_models.views import CommonPopoutCreateView, CommonPopoutDeleteView, CommonPopoutUpdateView, CommonCreateView, CommonDeleteView, \
    CommonDetailView, CommonFilterView, CommonUpdateView
from .. import views, models


class TestConsultationInstructionCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.OrganizationFactory()
        self.test_url = reverse_lazy('ihub:instruction_new', args=[self.instance.pk, ])
        self.expected_template = 'shared_models/generic_popout_form.html'
        self.user = self.get_and_login_user(in_group="ihub_edit")

    @tag("ConsultationInstruction", "instruction_new", "view")
    def test_view_class(self):
        self.assert_inheritance(views.InstructionCreateView, CommonPopoutCreateView)

    @tag("ConsultationInstruction", "instruction_new", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("ConsultationInstruction", "instruction_new", "submit")
    def test_submit(self):
        data = FactoryFloor.ConsultationInstructionFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)


class TestConsultationInstructionDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ConsultationInstructionFactory()
        self.test_url = reverse_lazy('ihub:instruction_delete', args=[self.instance.pk, ])
        self.expected_template = 'shared_models/generic_popout_confirm_delete.html'
        self.user = self.get_and_login_user(in_group="ihub_admin")

    @tag("ConsultationInstruction", "instruction_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(views.InstructionDeleteView, CommonPopoutDeleteView)

    @tag("ConsultationInstruction", "instruction_delete", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("ConsultationInstruction", "instruction_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.ConsultationInstructionFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(ml_models.ConsultationInstruction.objects.filter(pk=self.instance.pk).count(), 0)


class TestConsultationInstructionUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ConsultationInstructionFactory()
        self.test_url = reverse_lazy('ihub:instruction_edit', args=[self.instance.pk, ])
        self.expected_template = 'ihub/instruction_form.html'
        self.user = self.get_and_login_user(in_group="ihub_edit")

    @tag("ConsultationInstruction", "instruction_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.InstructionUpdateView, CommonPopoutUpdateView)

    @tag("ConsultationInstruction", "instruction_edit", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("ConsultationInstruction", "instruction_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.ConsultationInstructionFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)


class TestConsultationRoleCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance1 = FactoryFloor.OrganizationFactory()
        self.instance2 = FactoryFloor.OrganizationMemberFactory()
        self.test_url = reverse_lazy('ihub:consultee_new', args=[self.instance1.pk, self.instance2.pk, ])
        self.expected_template = 'shared_models/generic_popout_form.html'
        self.user = self.get_and_login_user(in_group="ihub_edit")

    @tag("ConsultationRole", "consultee_new", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ConsultationRoleCreateView, CommonPopoutCreateView)

    @tag("ConsultationRole", "consultee_new", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("ConsultationRole", "consultee_new", "submit")
    def test_submit(self):
        data = FactoryFloor.ConsultationRoleFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)


class TestConsultationRoleDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ConsultationRoleFactory()
        self.test_url = reverse_lazy('ihub:consultee_delete', args=[self.instance.pk, ])
        self.expected_template = 'shared_models/generic_popout_confirm_delete.html'
        self.user = self.get_and_login_user(in_group="ihub_admin")

    @tag("ConsultationRole", "consultee_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ConsultationRoleDeleteView, CommonPopoutDeleteView)

    @tag("ConsultationRole", "consultee_delete", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("ConsultationRole", "consultee_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.ConsultationRoleFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(ml_models.ConsultationRole.objects.filter(pk=self.instance.pk).count(), 0)


class TestConsultationRoleUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.ConsultationRoleFactory()
        self.test_url = reverse_lazy('ihub:consultee_edit', args=[self.instance.pk, ])
        self.expected_template = 'shared_models/generic_popout_form.html'
        self.user = self.get_and_login_user(in_group="ihub_edit")

    @tag("ConsultationRole", "consultee_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.ConsultationRoleUpdateView, CommonPopoutUpdateView)

    @tag("ConsultationRole", "consultee_edit", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("ConsultationRole", "consultee_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.ConsultationRoleFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)


class TestEntryCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('ihub:entry_new')
        self.expected_template = 'ihub/form.html'
        self.user = self.get_and_login_user(in_group="ihub_edit")

    @tag("Entry", "entry_new", "view")
    def test_view_class(self):
        self.assert_inheritance(views.EntryCreateView, CommonCreateView)

    @tag("Entry", "entry_new", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Entry", "entry_new", "submit")
    def test_submit(self):
        org = FactoryFloor.OrganizationFactory()
        grouping = ml_models.Grouping.objects.filter(is_indigenous=True).first()
        org.grouping.add(grouping)

        data = FactoryFloor.EntryFactory.get_valid_data()
        data["organizations"] = [org.id]
        self.assert_success_url(self.test_url, data=data, user=self.user)


class TestEntryDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.EntryFactory()
        self.test_url = reverse_lazy('ihub:entry_delete', args=[self.instance.pk, ])
        self.expected_template = 'ihub/confirm_delete.html'
        self.user = self.get_and_login_user(in_group="ihub_admin")

    @tag("Entry", "entry_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(views.EntryDeleteView, CommonDeleteView)
        self.assert_inheritance(views.EntryDeleteView, views.iHubAdminRequiredMixin)

    @tag("Entry", "entry_delete", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Entry", "entry_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.EntryFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(models.Entry.objects.filter(pk=self.instance.pk).count(), 0)


class TestEntryDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.EntryFactory()
        self.test_url = reverse_lazy('ihub:entry_detail', args=[self.instance.pk, ])
        self.expected_template = 'ihub/entry_detail.html'
        self.user = self.get_and_login_user()

    @tag("Entry", "entry_detail", "view")
    def test_view_class(self):
        self.assert_inheritance(views.EntryDetailView, CommonDetailView)

    @tag("Entry", "entry_detail", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Entry", "entry_detail", "context")
    def test_context(self):
        context_vars = [
            "field_list",
            "field_list_1",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)


class TestEntryListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('ihub:entry_list')
        self.expected_template = 'ihub/entry_list.html'
        self.user = self.get_and_login_user()

    @tag("Entry", "entry_list", "view")
    def test_view_class(self):
        self.assert_inheritance(views.EntryListView, CommonFilterView)

    @tag("Entry", "entry_list", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Entry", "entry_list", "context")
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)


class TestEntryNoteCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.EntryFactory()
        self.test_url = reverse_lazy('ihub:note_new', args=[self.instance.pk, ])
        self.expected_template = 'shared_models/generic_popout_form.html'
        self.user = self.get_and_login_user(in_group="ihub_edit")

    @tag("EntryNote", "note_new", "view")
    def test_view_class(self):
        self.assert_inheritance(views.NoteCreateView, CommonPopoutCreateView)

    @tag("EntryNote", "note_new", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("EntryNote", "note_new", "submit")
    def test_submit(self):
        data = FactoryFloor.EntryNoteFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)


class TestEntryNoteUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.EntryNoteFactory()
        self.test_url = reverse_lazy('ihub:note_edit', args=[self.instance.pk, ])
        self.expected_template = 'shared_models/generic_popout_form.html'
        self.user = self.get_and_login_user(in_group="ihub_edit")

    @tag("EntryNote", "note_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.NoteUpdateView, CommonPopoutUpdateView)

    @tag("EntryNote", "note_edit", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("EntryNote", "note_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.EntryNoteFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)


class TestEntryPersonCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.EntryPersonFactory()
        self.test_url = reverse_lazy('ihub:ep_new', args=[self.instance.pk, ])
        self.expected_template = 'ihub/entry_person_form_popout.html'
        self.user = self.get_and_login_user(in_group="ihub_edit")

    @tag("EntryPerson", "ep_new", "view")
    def test_view_class(self):
        self.assert_inheritance(views.EntryPersonCreateView, CommonPopoutCreateView)

    @tag("EntryPerson", "ep_new", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("EntryPerson", "ep_new", "submit")
    def test_submit(self):
        data = FactoryFloor.EntryPersonFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)


class TestEntryPersonDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.EntryPersonFactory()
        self.test_url = reverse_lazy('ihub:ep_delete', args=[self.instance.pk, ])
        self.user = self.get_and_login_user(in_group="ihub_edit")

    @tag("EntryPerson", "ep_delete", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)

    @tag("EntryPerson", "ep_delete", "access")
    def test_view2(self):
        self.assert_non_public_view(test_url=self.test_url, user=self.user, expected_code=302, locales=["en"])


class TestEntryPersonUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.EntryPersonFactory()
        self.test_url = reverse_lazy('ihub:ep_edit', args=[self.instance.pk, ])
        self.expected_template = 'ihub/entry_person_form_popout.html'
        self.user = self.get_and_login_user(in_group="ihub_edit")

    @tag("EntryPerson", "ep_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.EntryPersonUpdateView, CommonPopoutUpdateView)

    @tag("EntryPerson", "ep_edit", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("EntryPerson", "ep_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.EntryPersonFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)


class TestEntryUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.EntryFactory()
        self.test_url = reverse_lazy('ihub:entry_edit', args=[self.instance.pk, ])
        self.expected_template = 'ihub/form.html'
        self.user = self.get_and_login_user(in_group="ihub_edit")

    @tag("Entry", "entry_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.EntryUpdateView, CommonUpdateView)
        self.assert_inheritance(views.EntryUpdateView, views.iHubEditRequiredMixin)

    @tag("Entry", "entry_edit", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Entry", "entry_edit", "submit")
    def test_submit(self):
        # need to make sure the organization is
        org = FactoryFloor.OrganizationFactory()
        grouping = ml_models.Grouping.objects.filter(is_indigenous=True).first()
        org.grouping.add(grouping)

        data = FactoryFloor.EntryFactory.get_valid_data()
        data["organizations"] = [org.id]
        self.assert_success_url(self.test_url, data=data, user=self.user)


class TestIndexTemplateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('ihub:index')
        self.expected_template = 'ihub/index.html'
        self.user = self.get_and_login_user()

    @tag("Index", "index", "view")
    def test_view_class(self):
        self.assert_inheritance(views.IndexTemplateView, TemplateView)

    @tag("Index", "index", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)


class TestOrganizationCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('ihub:org_new')
        self.expected_template = 'ihub/form.html'
        self.user = self.get_and_login_user(in_group="ihub_edit")

    @tag("Organization", "org_new", "view")
    def test_view_class(self):
        self.assert_inheritance(views.OrganizationCreateView, CommonCreateView)

    @tag("Organization", "org_new", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Organization", "org_new", "submit")
    def test_submit(self):
        data = FactoryFloor.OrganizationFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)


class TestOrganizationDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.OrganizationFactory()
        self.test_url = reverse_lazy('ihub:org_delete', args=[self.instance.pk, ])
        self.expected_template = 'ihub/confirm_delete.html'
        self.user = self.get_and_login_user(in_group="ihub_admin")

    @tag("Organization", "org_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(views.OrganizationDeleteView, DeleteView)

    @tag("Organization", "org_delete", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Organization", "org_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.OrganizationFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(ml_models.Organization.objects.filter(pk=self.instance.pk).count(), 0)


class TestOrganizationDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.OrganizationFactory()
        self.test_url = reverse_lazy('ihub:org_detail', args=[self.instance.pk, ])
        self.expected_template = 'ihub/organization_detail.html'
        self.user = self.get_and_login_user()

    @tag("Organization", "org_detail", "view")
    def test_view_class(self):
        self.assert_inheritance(views.OrganizationDetailView, CommonDetailView)

    @tag("Organization", "org_detail", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Organization", "org_detail", "context")
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)


class TestOrganizationListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('ihub:org_list')
        self.expected_template = 'ihub/organization_list.html'
        self.user = self.get_and_login_user()

    @tag("Organization", "org_list", "view")
    def test_view_class(self):
        self.assert_inheritance(views.OrganizationListView, CommonFilterView)

    @tag("Organization", "org_list", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Organization", "org_list", "context")
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)


class TestOrganizationMemberCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.OrganizationFactory()
        self.test_url = reverse_lazy('ihub:member_new', args=[self.instance.pk, ])
        self.expected_template = 'ihub/member_form_popout.html'
        self.user = self.get_and_login_user(in_group="ihub_edit")

    @tag("OrganizationMember", "member_new", "view")
    def test_view_class(self):
        self.assert_inheritance(views.MemberCreateView, CommonPopoutCreateView)

    @tag("OrganizationMember", "member_new", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("OrganizationMember", "member_new", "submit")
    def test_submit(self):
        data = FactoryFloor.OrganizationMemberFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)


class TestOrganizationMemberDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.OrganizationMemberFactory()
        self.test_url = reverse_lazy('ihub:member_delete', args=[self.instance.pk, ])
        self.expected_template = 'shared_models/generic_popout_confirm_delete.html'
        self.user = self.get_and_login_user(in_group="ihub_admin")

    @tag("OrganizationMember", "member_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(views.MemberDeleteView, CommonPopoutDeleteView)

    @tag("OrganizationMember", "member_delete", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("OrganizationMember", "member_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.OrganizationMemberFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(ml_models.OrganizationMember.objects.filter(pk=self.instance.pk).count(), 0)


class TestOrganizationMemberUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.OrganizationMemberFactory()
        self.test_url = reverse_lazy('ihub:member_edit', args=[self.instance.pk, ])
        self.expected_template = 'ihub/member_form_popout.html'
        self.user = self.get_and_login_user(in_group="ihub_edit")

    @tag("OrganizationMember", "member_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.MemberUpdateView, CommonPopoutUpdateView)

    @tag("OrganizationMember", "member_edit", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("OrganizationMember", "member_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.OrganizationMemberFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)


class TestOrganizationUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.OrganizationFactory()
        self.test_url = reverse_lazy('ihub:org_edit', args=[self.instance.pk, ])
        self.expected_template = 'ihub/form.html'
        self.user = self.get_and_login_user(in_group="ihub_edit")

    @tag("Organization", "org_edit", "view")
    def test_view_class(self):
        self.assert_inheritance(views.OrganizationUpdateView, CommonUpdateView)
        self.assert_inheritance(views.OrganizationUpdateView, views.iHubEditRequiredMixin)

    @tag("Organization", "org_edit", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Organization", "org_edit", "submit")
    def test_submit(self):
        data = FactoryFloor.OrganizationFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)


class TestPersonCreateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('ihub:person_new')
        self.test_url1 = reverse_lazy('ihub:person_new_pop')
        self.expected_template = 'ihub/form.html'
        self.expected_template1 = 'shared_models/generic_popout_form.html'
        self.user = self.get_and_login_user(in_group="ihub_edit")

    @tag("Person", "person_new", "view")
    def test_view_class(self):
        self.assert_inheritance(views.PersonCreateView, CommonCreateView)
        self.assert_inheritance(views.PersonCreateView, views.iHubEditRequiredMixin)
        self.assert_inheritance(views.PersonCreateViewPopout, CommonPopoutCreateView)
        self.assert_inheritance(views.PersonCreateViewPopout, views.iHubEditRequiredMixin)

    @tag("Person", "person_new", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)
        self.assert_not_broken(self.test_url1)
        self.assert_non_public_view(test_url=self.test_url1, expected_template=self.expected_template1, user=self.user)

    @tag("Person", "person_new", "submit")
    def test_submit(self):
        data = FactoryFloor.PersonFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)
        self.assert_success_url(self.test_url1, data=data, user=self.user)


class TestPersonDeleteView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.PersonFactory()
        self.test_url = reverse_lazy('ihub:person_delete', args=[self.instance.pk, ])
        self.expected_template = 'ihub/confirm_delete.html'
        self.user = self.get_and_login_user(in_group="ihub_admin")

    @tag("Person", "person_delete", "view")
    def test_view_class(self):
        self.assert_inheritance(views.PersonDeleteView, CommonDeleteView)
        self.assert_inheritance(views.PersonDeleteView, views.iHubAdminRequiredMixin)

    @tag("Person", "person_delete", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Person", "person_delete", "submit")
    def test_submit(self):
        data = FactoryFloor.PersonFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(ml_models.Person.objects.filter(pk=self.instance.pk).count(), 0)


class TestPersonDetailView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.PersonFactory()
        self.test_url = reverse_lazy('ihub:person_detail', args=[self.instance.pk, ])
        self.expected_template = 'ihub/person_detail.html'
        self.user = self.get_and_login_user()

    @tag("Person", "person_detail", "view")
    def test_view_class(self):
        self.assert_inheritance(views.PersonDetailView, CommonDetailView)

    @tag("Person", "person_detail", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Person", "person_detail", "context")
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)


class TestPersonListView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.PersonFactory()
        self.test_url = reverse_lazy('ihub:person_list')
        self.expected_template = 'ihub/list.html'
        self.user = self.get_and_login_user()

    @tag("Person", "person_list", "view")
    def test_view_class(self):
        self.assert_inheritance(views.PersonListView, CommonFilterView)

    @tag("Person", "person_list", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("Person", "person_list", "context")
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)


class TestPersonUpdateView(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.PersonFactory()
        self.test_url = reverse_lazy('ihub:person_edit', args=[self.instance.pk, ])
        self.test_url1 = reverse_lazy('ihub:person_edit_pop', args=[self.instance.pk, ])
        self.expected_template = 'ihub/form.html'
        self.expected_template1 = 'shared_models/generic_popout_form.html'
        self.user = self.get_and_login_user(in_group="ihub_edit")

    @tag("Person", "person_form", "view")
    def test_view_class(self):
        self.assert_inheritance(views.PersonUpdateView, CommonUpdateView)
        self.assert_inheritance(views.PersonUpdateViewPopout, CommonPopoutUpdateView)

    @tag("Person", "person_form", "access")
    def test_view(self):
        self.assert_not_broken(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)
        self.assert_not_broken(self.test_url1)
        self.assert_non_public_view(test_url=self.test_url1, expected_template=self.expected_template1, user=self.user)

    @tag("Person", "person_form", "submit")
    def test_submit(self):
        data = FactoryFloor.PersonFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)
        self.assert_success_url(self.test_url1, data=data, user=self.user)
