import datetime
import factory
from faker import Factory

from django.utils import timezone

from shared_models.test.SharedModelsFactoryFloor import UserFactory, BranchFactory, DivisionFactory

from maret import models
from masterlist import models as ml_models
from ihub.test import FactoryFloor as i_factory

faker = Factory.create()


class InteractionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Interaction

    description = factory.lazy_attribute(lambda o: faker.text())
    interaction_type = factory.lazy_attribute(lambda o: faker.pyint(1, 3))
    committee = factory.SubFactory("maret.test.FactoryFloor.CommitteeFactory")
    dfo_role = factory.lazy_attribute(lambda o: faker.pyint(1, 11))
    other_dfo_participants = factory.SubFactory(UserFactory)
    action_items = factory.lazy_attribute(lambda o: faker.text())

    @factory.post_generation
    def main_topic(self, create, extracted, **kwargs):
        if create:
            dis = models.DiscussionTopic.objects.first()
            self.main_topic.set((dis,))

    @factory.post_generation
    def species(self, create, extracted, **kwargs):
        if create:
            species = models.Species.objects.first()
            self.species.set((species,))

    @factory.post_generation
    def dfo_liaison(self, create, extracted, **kwargs):
        if create:
            usr = UserFactory()
            self.dfo_liaison.set((usr,))

    @factory.post_generation
    def other_dfo_participants(self, create, extracted, **kwargs):
        if create:
            usr = UserFactory()
            self.other_dfo_participants.set((usr,))

    @staticmethod
    def get_valid_data():
        obj = InteractionFactory.build()
        committee = CommitteeFactory()
        dis = models.DiscussionTopic.objects.first()
        species = models.Species.objects.first()
        usr = UserFactory()

        return {
            'description': obj.description,
            'interaction_type': obj.interaction_type,
            'committee': committee.pk,
            'dfo_role': obj.dfo_role,
            'action_items': obj.action_items,
            'species': [species.pk, ],
            'main_topic': [dis.pk, ],
            'dfo_liaison': [usr.pk, ],
            'other_dfo_participants': [usr.pk, ],
        }


class CommitteeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Committee

    name = factory.lazy_attribute(lambda o: faker.name())
    branch = factory.SubFactory(BranchFactory)
    division = factory.SubFactory(DivisionFactory)
    is_dfo_chair = factory.lazy_attribute(lambda o: faker.pyint(0, 1))
    meeting_frequency = factory.lazy_attribute(lambda o: faker.pyint(0, 9))
    main_actions = factory.lazy_attribute(lambda o: faker.text())

    last_modified = factory.lazy_attribute(lambda o: timezone.now())
    last_modified_by = factory.SubFactory(UserFactory)

    @factory.post_generation
    def dfo_liaison(self, create, extracted, **kwargs):
        if create:
            usr = UserFactory()
            self.dfo_liaison.set((usr,))

    @factory.post_generation
    def other_dfo_branch(self, create, extracted, **kwargs):
        if create:
            branch = BranchFactory()
            self.other_dfo_branch.set((branch,))

    @staticmethod
    def get_valid_data():
        obj = CommitteeFactory.build()
        branch = BranchFactory()
        division = DivisionFactory()
        user = UserFactory()

        return {
            'name': obj.name,
            'branch': branch.pk,
            'division': division.pk,
            'is_dfo_chair': obj.is_dfo_chair,
            'meeting_frequency': obj.meeting_frequency,
            'main_actions': obj.main_actions,
            'last_modified': obj.last_modified,
            'last_modified_by': user.pk,
            'dfo_liaison': [user.pk, ],
            'other_dfo_branch': [branch.pk, ]
        }


class OrganizationExtensionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.OrganizationExtension

    organization = factory.SubFactory(i_factory.OrganizationFactory)

    @factory.post_generation
    def area(self, create, extracted, **kwargs):
        if create:
            area = faker.pyint(1, 4)
            self.area.set((area,))

    @staticmethod
    def get_valid_data():
        org_ext = OrganizationExtensionFactory.build()

        return {
            "organziation": org_ext.organization.pk,
            "area": org_ext.area
        }

class GroupingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ml_models.Grouping

    name = factory.lazy_attribute(lambda o: faker.word())
    is_indigenous = False


class OrganizationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ml_models.Organization

    name_eng = factory.lazy_attribute(lambda o: faker.word())

    @factory.post_generation
    def grouping(self, create, extracted, **kwargs):
        if create:
            grp = GroupingFactory()
            self.grouping.set((grp,))

    @staticmethod
    def get_valid_data():
        org = OrganizationFactory.build()
        grp = GroupingFactory()

        return {
            'name_eng': org.name_eng,
            'processing_plant': 0,
            'wharf': 0,
            'grouping': [grp.pk, ],
        }


class SimpleLookupFactory:
    name = factory.lazy_attribute(lambda o: faker.name())
    nom = factory.lazy_attribute(lambda o: faker.name())
