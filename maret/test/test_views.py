from django.test import tag, RequestFactory
from django.urls import reverse_lazy

from shared_models.views import CommonCreateView, CommonDetailView, CommonDeleteView, CommonUpdateView, \
    CommonPopoutUpdateView, CommonPopoutCreateView, CommonPopoutDeleteView
from shared_models import views as shared_views
from masterlist import models as ml_models

from maret import views, models, utils
from maret.test import FactoryFloor
from maret.test.common_tests import CommonMaretTest

from ihub.test import FactoryFloor as i_factory


def setup_view(view, request, *args, **kwargs):
    view.request = request
    view.args = args
    view.kwargs = kwargs
    return view


@tag('all', 'view', 'index')
class TestIndexView(CommonMaretTest):
    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('maret:index')
        self.expected_template = 'maret/index.html'
        self.user = self.get_and_login_user(in_group="maret_user")

    @tag('url')
    def test_correct_url(self):
        # use the 'en' locale prefix to url
        self.assert_correct_url("maret:index", f"/en/maret/")

    @tag('access')
    def test_view_access(self):
        self.assert_good_response(self.test_url)
        admin_user = self.get_and_login_user(in_group="maret_admin")
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=admin_user)

        author_user = self.get_and_login_user(in_group="maret_author")
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=author_user)

        user_user = self.get_and_login_user(in_group="maret_user")
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=user_user)

    @tag('class')
    def test_view_class(self):
        self.assert_inheritance(views.IndexView, shared_views.CommonTemplateView)


#######################################################
# Organizations
#######################################################
@tag('all', 'view', 'list', 'org', 'org_list')
class TestOrganizationListView(CommonMaretTest):

    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('maret:org_list')
        self.expected_template = 'maret/maret_list.html'
        self.user = self.get_and_login_user(in_group="maret_user")

    @tag("view", 'org_list_view')
    def test_view_class(self):
        self.assert_inheritance(views.OrganizationListView, shared_views.CommonFilterView)

    @tag("access", 'org_list_access')
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("context", 'org_list_context')
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)


@tag('all', 'view', 'details', 'org', 'org_details')
class TestOrganizationDetailView(CommonMaretTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.OrganizationFactory()
        self.test_url = reverse_lazy('maret:org_detail', args=[self.instance.pk, ])
        self.expected_template = 'maret/organization_detail.html'
        self.user = self.get_and_login_user(in_group="maret_user")

    @tag("view", "org_details_view")
    def test_view_class(self):
        self.assert_inheritance(views.OrganizationDetailView, CommonDetailView)

    @tag("access", "org_details_access", )
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("context", "org_details_context")
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)


@tag('all', 'view', 'update', 'org', 'org_update')
class TestOrganizationUpdateView(CommonMaretTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.OrganizationFactory()
        self.test_url = reverse_lazy('maret:org_edit', args=[self.instance.pk, ])
        self.expected_template = 'maret/form.html'
        self.user = self.get_and_login_user(in_group="maret_author")

    @tag("view", "org_update_view")
    def test_view_class(self):
        self.assert_inheritance(views.OrganizationUpdateView, CommonUpdateView)
        self.assert_inheritance(views.OrganizationUpdateView, utils.AuthorRequiredMixin)

    @tag("access", "org_update_access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("submit", "org_update_submit")
    def test_submit(self):
        data = FactoryFloor.OrganizationFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("locked", "org_update_locked")
    def test_locked_by_ihub(self):
        self.instance.locked_by_ihub = True
        self.instance.save()

        update_data = FactoryFloor.OrganizationFactory.get_valid_data()
        self.assert_message_returned_url(self.test_url, data=update_data, user=self.user,
                                         expected_messages=["This record can only be modified through iHub",])


@tag('all', 'view', 'delete', 'org', 'org_delete')
class TestOrganizationDeleteView(CommonMaretTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.OrganizationFactory()
        self.test_url = reverse_lazy('maret:org_delete', args=[self.instance.pk, ])
        self.expected_template = 'maret/confirm_delete.html'
        self.user = self.get_and_login_user(in_group="maret_admin")

    @tag("view", "org_delete_view")
    def test_view_class(self):
        self.assert_inheritance(views.OrganizationDeleteView, CommonDeleteView)

    @tag("access", "org_delete_access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("submit", "org_delete_submit")
    def test_submit(self):
        data = FactoryFloor.OrganizationFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(ml_models.Organization.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("locked", "org_delete_locked")
    def test_locked_by_ihub(self):
        self.instance.locked_by_ihub = True
        self.instance.save()

        update_data = FactoryFloor.OrganizationFactory.get_valid_data()
        self.assert_message_returned_url(self.test_url, data=update_data, user=self.user,
                                         expected_messages=["This record can only be modified through iHub",])


#######################################################
# Organizations memberships
#######################################################
@tag('all', 'view', 'create', 'member', 'member_create')
class TestOrganizationMemberCreateView(CommonMaretTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.OrganizationFactory()
        self.test_url = reverse_lazy('maret:member_new', args=[self.instance.pk, ])
        self.expected_template = 'maret/member_form_popout.html'
        self.user = self.get_and_login_user(in_group="maret_author")

    @tag("view", "member_create_view")
    def test_view_class(self):
        self.assert_inheritance(views.MemberCreateView, CommonPopoutCreateView)

    @tag("access", "member_create_access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("submit", "member_create_submit")
    def test_submit(self):
        data = i_factory.OrganizationMemberFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("locked", "member_create_locked")
    def test_locked_by_ihub(self):
        self.instance.locked_by_ihub = True
        self.instance.save()

        data = i_factory.OrganizationMemberFactory.get_valid_data()
        data["organization"] = self.instance.id
        self.assert_message_returned_url(self.test_url, data=data, user=self.user,
                                         expected_messages=["This record can only be modified through iHub",])


@tag('all', 'view', 'update', 'member', 'member_update')
class TestOrganizationMemberUpdateView(CommonMaretTest):
    def setUp(self):
        super().setUp()
        self.instance = i_factory.OrganizationMemberFactory()
        self.test_url = reverse_lazy('maret:member_edit', args=[self.instance.pk, ])
        self.expected_template = 'maret/member_form_popout.html'
        self.user = self.get_and_login_user(in_group="maret_author")

    @tag("view", "member_update_view")
    def test_view_class(self):
        self.assert_inheritance(views.MemberUpdateView, CommonPopoutUpdateView)

    @tag("access", "member_update_access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("submit", "member_update_submit")
    def test_submit(self):
        data = i_factory.OrganizationMemberFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

    @tag("locked", "member_update_locked")
    def test_locked_by_ihub(self):
        org = self.instance.organization
        org.locked_by_ihub = True
        org.save()

        data = i_factory.OrganizationMemberFactory.get_valid_data()
        data["organization"] = self.instance.id
        self.assert_message_returned_url(self.test_url, data=data, user=self.user,
                                         expected_messages=["This record can only be modified through iHub",])


@tag('all', 'view', 'delete', 'member', 'member_delete')
class TestOrganizationMemberDeleteView(CommonMaretTest):
    def setUp(self):
        super().setUp()
        self.instance = i_factory.OrganizationMemberFactory()
        self.test_url = reverse_lazy('maret:member_delete', args=[self.instance.pk, ])
        self.expected_template = 'shared_models/generic_popout_confirm_delete.html'
        self.user = self.get_and_login_user(in_group="maret_admin")

    @tag("view", "member_delete_view")
    def test_view_class(self):
        self.assert_inheritance(views.MemberDeleteView, CommonPopoutDeleteView)

    @tag("access", "member_delete_access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("submit", "member_delete_submit")
    def test_submit(self):
        data = i_factory.OrganizationMemberFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(ml_models.OrganizationMember.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("locked", "member_delete_locked")
    def test_locked_by_ihub(self):
        org = self.instance.organization
        org.locked_by_ihub = True
        org.save()

        data = i_factory.OrganizationMemberFactory.get_valid_data()
        data["organization"] = self.instance.id
        self.assert_message_returned_url(self.test_url, data=data, user=self.user,
                                         expected_messages=["This record can only be modified through iHub",])


#######################################################
# Person / Contacts
#######################################################
@tag('all', 'view', 'list', 'person', 'person_list')
class TestPersonListView(CommonMaretTest):

    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('maret:person_list')
        self.expected_template = 'maret/maret_list.html'
        self.user = self.get_and_login_user(in_group="maret_author")

    @tag("view")
    def test_view_class(self):
        self.assert_inheritance(views.PersonListView, shared_views.CommonFilterView)

    @tag("access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("context")
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)


@tag('all', 'view', 'create', 'person', 'person_create')
class TestPersonCreateView(CommonMaretTest):

    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('maret:person_new')
        self.test_url1 = reverse_lazy('maret:person_new_pop')
        self.expected_template = 'maret/form.html'
        self.expected_template1 = 'shared_models/generic_popout_form.html'
        self.user = self.get_and_login_user(in_group="maret_author")

    @tag("view", "person_create_view")
    def test_view_class(self):
        self.assert_inheritance(views.PersonCreateView, CommonCreateView)
        self.assert_inheritance(views.PersonCreateView, views.AuthorRequiredMixin)
        self.assert_inheritance(views.PersonCreateViewPopout, CommonPopoutCreateView)
        self.assert_inheritance(views.PersonCreateViewPopout, views.AuthorRequiredMixin)

    @tag("access", "person_create_access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)
        self.assert_good_response(self.test_url1)
        self.assert_non_public_view(test_url=self.test_url1, expected_template=self.expected_template1, user=self.user)

    @tag("submit", "person_create_submit")
    def test_submit(self):
        data = i_factory.PersonFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)
        self.assert_success_url(self.test_url1, data=data, user=self.user)


@tag('all', 'view', 'create', 'person', 'person_update')
class TestPersonUpdateView(CommonMaretTest):

    def setUp(self):
        super().setUp()
        self.instance = i_factory.PersonFactory()
        self.test_url = reverse_lazy('maret:person_edit', args=[self.instance.pk, ])
        self.test_url1 = reverse_lazy('maret:person_edit_pop', args=[self.instance.pk, ])
        self.expected_template = 'maret/form.html'
        self.expected_template1 = 'shared_models/generic_popout_form.html'
        self.user = self.get_and_login_user(in_group="maret_author")

    @tag("view", "person_update_view")
    def test_view_class(self):
        self.assert_inheritance(views.PersonUpdateView, CommonUpdateView)
        self.assert_inheritance(views.PersonUpdateView, views.AuthorRequiredMixin)
        self.assert_inheritance(views.PersonUpdateViewPopout, CommonPopoutUpdateView)
        self.assert_inheritance(views.PersonUpdateViewPopout, views.AuthorRequiredMixin)

    @tag("access", "person_update_access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)
        self.assert_good_response(self.test_url1)
        self.assert_non_public_view(test_url=self.test_url1, expected_template=self.expected_template1, user=self.user)

    @tag("submit", "person_update_submit")
    def test_submit(self):
        data = i_factory.PersonFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)
        self.assert_success_url(self.test_url1, data=data, user=self.user)

    @tag("locked", "person_update_locked")
    def test_locked_by_ihub(self):
        self.instance.locked_by_ihub = True
        self.instance.save()

        update_data = i_factory.PersonFactory.get_valid_data()
        self.assert_message_returned_url(self.test_url, data=update_data, user=self.user,
                                         expected_messages=["This record can only be modified through iHub",])
        self.assert_message_returned_url(self.test_url1, data=update_data, user=self.user,
                                         expected_messages=["This record can only be modified through iHub",])


@tag('all', 'view', 'details', 'person', 'person_details')
class TestPersonDetailView(CommonMaretTest):
    def setUp(self):
        super().setUp()
        self.instance = i_factory.PersonFactory()
        self.test_url = reverse_lazy('maret:person_detail', args=[self.instance.pk, ])
        self.expected_template = 'maret/person_detail.html'
        self.user = self.get_and_login_user(in_group="maret_user")

    def test_view_class(self):
        self.assert_inheritance(views.CommitteeDetailView, CommonDetailView)

    @tag("access", "person_details_access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("context", "person_details_context")
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)


@tag('all', 'view', 'delete', 'person', 'person_delete')
class TestPersonDeleteView(CommonMaretTest):
    def setUp(self):
        super().setUp()
        self.instance = i_factory.PersonFactory()
        self.test_url = reverse_lazy('maret:person_delete', args=[self.instance.pk, ])
        self.expected_template = 'maret/confirm_delete.html'
        self.user = self.get_and_login_user(in_group="maret_admin")

    @tag("view", "person_delete_view")
    def test_view_class(self):
        self.assert_inheritance(views.PersonDeleteView, CommonDeleteView)
        self.assert_inheritance(views.PersonDeleteView, utils.AdminRequiredMixin)

    @tag("access", "person_delete_access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("submit", "person_delete_submit")
    def test_submit(self):
        data = i_factory.PersonFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(ml_models.Person.objects.filter(pk=self.instance.pk).count(), 0)

    @tag("locked", "person_delete_locked")
    def test_locked_by_ihub(self):
        self.instance.locked_by_ihub = True
        self.instance.save()

        update_data = i_factory.PersonFactory.get_valid_data()
        self.assert_message_returned_url(self.test_url, data=update_data, user=self.user,
                                         expected_messages=["This record can only be modified through iHub",])


#######################################################
# Committee / Working Groups
#######################################################
@tag('all', 'view', 'list', 'committee_list')
class TestCommitteeListView(CommonMaretTest):

    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('maret:committee_list')
        self.expected_template = 'maret/maret_list.html'
        self.user = self.get_and_login_user(in_group="maret_user")

    @tag("view")
    def test_view_class(self):
        self.assert_inheritance(views.CommitteeListView, shared_views.CommonFilterView)

    @tag("access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("context")
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)


@tag('all', 'view', 'create', 'committee_create')
class TestCommitteeCreateView(CommonMaretTest):

    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('maret:committee_new')
        self.expected_template = 'maret/form.html'
        self.user = self.get_and_login_user(in_group="maret_author")

    @tag("view", "committee_create_view")
    def test_view_class(self):
        self.assert_inheritance(views.CommonCreateView, CommonCreateView)

    @tag("access", "committee_create_access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("submit", "committee_create_submit")
    def test_submit(self):
        data = FactoryFloor.CommitteeFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)


@tag('all', 'view', 'details', 'committee_details')
class TestCommitteeDetailView(CommonMaretTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.CommitteeFactory()
        self.test_url = reverse_lazy('maret:committee_detail', args=[self.instance.pk, ])
        self.expected_template = 'maret/committee_detail.html'
        self.user = self.get_and_login_user(in_group="maret_user")

    def test_view_class(self):
        self.assert_inheritance(views.CommitteeDetailView, CommonDetailView)

    @tag("access", "committee_details_access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("context", "committee_details_context")
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)


@tag('all', 'view', 'delete', 'committee_delete')
class TestCommitteeDeleteView(CommonMaretTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.CommitteeFactory()
        self.test_url = reverse_lazy('maret:committee_delete', args=[self.instance.pk, ])
        self.expected_template = 'maret/confirm_delete.html'
        self.user = self.get_and_login_user(in_group="maret_admin")

    @tag("view", 'committee_delete_view')
    def test_view_class(self):
        self.assert_inheritance(views.CommitteeDeleteView, CommonDeleteView)
        self.assert_inheritance(views.CommitteeDeleteView, utils.AuthorRequiredMixin)

    @tag("access", 'committee_delete_access')
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("submit", 'committee_delete_submit')
    def test_submit(self):
        data = FactoryFloor.CommitteeFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(models.Committee.objects.filter(pk=self.instance.pk).count(), 0)


@tag('all', 'view', 'update', 'committee_update')
class TestCommitteeUpdateView(CommonMaretTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.CommitteeFactory()
        self.test_url = reverse_lazy('maret:committee_edit', args=[self.instance.pk, ])
        self.expected_template = 'maret/form.html'
        self.user = self.get_and_login_user(in_group="maret_author")

    @tag("view", 'committee_update_view')
    def test_view_class(self):
        self.assert_inheritance(views.CommitteeUpdateView, CommonUpdateView)
        self.assert_inheritance(views.CommitteeUpdateView, utils.AuthorRequiredMixin)

    @tag("access", 'committee_update_access')
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("submit", 'committee_update_submit')
    def test_submit(self):
        # need to make sure the organization is
        data = FactoryFloor.CommitteeFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)


#######################################################
# Interactions
#######################################################
@tag('all', 'view', 'interaction_list')
class TestInteractionListView(CommonMaretTest):

    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('maret:interaction_list')
        self.expected_template = 'maret/maret_list.html'
        self.user = self.get_and_login_user(in_group="maret_user")

    @tag("view")
    def test_view_class(self):
        self.assert_inheritance(views.InteractionListView, shared_views.CommonFilterView)

    @tag("access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("context")
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)


@tag('all', 'view', 'interaction_create')
class TestInteractionCreateView(CommonMaretTest):

    def setUp(self):
        super().setUp()
        self.test_url = reverse_lazy('maret:interaction_new')
        self.expected_template = 'maret/form.html'
        self.user = self.get_and_login_user(in_group="maret_admin")

    @tag("view", "interaction_create_view")
    def test_view_class(self):
        self.assert_inheritance(views.InteractionCreateView, CommonCreateView)

    @tag("access", "interaction_create_access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("submit", "interaction_create_submit")
    def test_submit(self):
        data = FactoryFloor.InteractionFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)


@tag('all', 'view', 'details', 'interaction_details')
class TestInteractionDetailView(CommonMaretTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.InteractionFactory()
        self.test_url = reverse_lazy('maret:interaction_detail', args=[self.instance.pk, ])
        self.expected_template = 'maret/interaction_detail.html'
        self.user = self.get_and_login_user(in_group="maret_user")

    def test_view_class(self):
        self.assert_inheritance(views.InteractionDetailView, CommonDetailView)

    @tag("access", "interaction_details_access")
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("context", "interaction_details_context")
    def test_context(self):
        context_vars = [
            "field_list",
        ]
        self.assert_presence_of_context_vars(self.test_url, context_vars, user=self.user)


@tag('all', 'view', 'delete', 'interaction_delete')
class TestInteractionDeleteView(CommonMaretTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.InteractionFactory()
        self.test_url = reverse_lazy('maret:interaction_delete', args=[self.instance.pk, ])
        self.expected_template = 'maret/confirm_delete.html'
        self.user = self.get_and_login_user(in_group="maret_admin")

    @tag("view", 'interaction_delete_view')
    def test_view_class(self):
        self.assert_inheritance(views.InteractionDeleteView, CommonDeleteView)
        self.assert_inheritance(views.InteractionDeleteView, utils.AuthorRequiredMixin)

    @tag("access", 'interaction_delete_access')
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("submit", 'interaction_delete_submit')
    def test_submit(self):
        data = FactoryFloor.InteractionFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)

        # for delete views...
        self.assertEqual(models.Interaction.objects.filter(pk=self.instance.pk).count(), 0)


@tag('all', 'view', 'update', 'interaction_update')
class TestInteractionUpdateView(CommonMaretTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.InteractionFactory()
        self.test_url = reverse_lazy('maret:interaction_edit', args=[self.instance.pk, ])
        self.expected_template = 'maret/form.html'
        self.user = self.get_and_login_user(in_group="maret_author")

    @tag("view", 'interaction_update_view')
    def test_view_class(self):
        self.assert_inheritance(views.InteractionUpdateView, CommonUpdateView)
        self.assert_inheritance(views.InteractionUpdateView, utils.AuthorRequiredMixin)

    @tag("access", 'interaction_update_access')
    def test_view(self):
        self.assert_good_response(self.test_url)
        self.assert_non_public_view(test_url=self.test_url, expected_template=self.expected_template, user=self.user)

    @tag("submit", 'interaction_update_submit')
    def test_submit(self):
        # need to make sure the organization is
        data = FactoryFloor.InteractionFactory.get_valid_data()
        self.assert_success_url(self.test_url, data=data, user=self.user)


