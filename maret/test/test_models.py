from django.test import tag

from maret import models
from maret.test import FactoryFloor
from maret.test.common_tests import CommonMaretTest as CommonTest


@tag("interaction", "model", "interaction_model")
class TestInteractionModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.InteractionFactory()

    @tag("fields", "interaction_model_fields")
    def test_fields(self):
        fields_to_check = ["description", "interaction_type", "committee", "dfo_role", "dfo_liaison",
                           "other_dfo_participants", "date_of_meeting", "main_topic", "species", "action_items",
                           "comments", "last_modified", "last_modified_by"]
        self.assert_has_fields(models.Interaction, fields_to_check)


@tag("committee", "model", "committee_model")
class TestCommitteeModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.CommitteeFactory()

    @tag("fields", "committee_model_fields")
    def test_fields(self):
        fields_to_check = ['name', 'branch', 'division', 'is_dfo_chair', 'dfo_liaison', 'other_dfo_branch',
                           'first_nation_participation', 'provincial_participation', 'meeting_frequency', 'are_tor',
                           'location_of_tor', 'main_actions', 'comments', 'last_modified', 'last_modified_by']
        self.assert_has_fields(models.Committee, fields_to_check)


@tag("org_ext", "model", "org_ext_model")
class TestOrganizationExtensionModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = FactoryFloor.OrganizationExtensionFactory()

    @tag("fields", "org_ext_model_fields")
    def test_fields(self):
        fields_to_check = ['organization', 'area', ]
        self.assert_has_fields(models.OrganizationExtension, fields_to_check)


@tag("species", "model", "species_model")
class TestSpeciesModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = models.Species.objects.first()

    @tag("fields", "species_model_fields")
    def test_fields(self):
        fields_to_check = ["name", "nom"]
        self.assert_has_fields(models.Species, fields_to_check)


@tag("discussion_topic", "model", "discussion_topic_model")
class TestDiscussionTopicModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = models.DiscussionTopic.objects.first()

    @tag("fields", "discussion_topic_model_fields")
    def test_fields(self):
        fields_to_check = ["name", "nom"]
        self.assert_has_fields(models.DiscussionTopic, fields_to_check)


@tag("area", "model", "area_model")
class TestAreaModel(CommonTest):
    def setUp(self):
        super().setUp()
        self.instance = models.Area.objects.first()

    @tag("fields", "area_model_fields")
    def test_fields(self):
        fields_to_check = ["name", "nom"]
        self.assert_has_fields(models.Area, fields_to_check)


