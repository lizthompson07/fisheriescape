import factory
from faker import Factory

from bio_diversity import models

faker = Factory.create()


class InstdcFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.InstDetCode

    name = factory.lazy_attribute(lambda o: faker.word())
    nom = factory.lazy_attribute(lambda o: faker.word())
    description_en = factory.lazy_attribute(lambda o: faker.text())
    description_fr = factory.lazy_attribute(lambda o: faker.text())
    created_by = factory.lazy_attribute(lambda o: faker.name())
    created_date = factory.lazy_attribute(lambda o: faker.date())

    @staticmethod
    def build_valid_data(**kwargs):
        # There are a couple of ways to get data out of a Factory
        #
        # Create an instance (BioFactoryFloor.InstFactory() or BioFactoryFloor.InstFactory.create()). This will make
        # an entry in the database and return the object.
        #
        # Build an instance (BioFactoryFloor.InstFactory.build()). This will create an instance of the object, but not
        # enter it in the database.
        #
        # Similar there are Create and Build batches (BioFactoryFloor.InstFactory.create_batch(),
        # BioFactoryFloor.InstFactory.build_batch()) which will produce multiple instances of objects.

        # In this case I created the data, as a dictionary, but didn't want that entered into the database. I just want
        # an dictionary of data to pass to the test method to ensure the creation form puts the data in the database
        # correctly.

        obj = InstdcFactory.build(**kwargs)

        # Convert the data to a dictionary to be used in testing
        data = {
            'name': obj.name,
            'nom': obj.nom,
            'description_en': obj.description_en,
            'description_fr': obj.description_fr,
            'created_by': obj.created_by,
            'created_date': obj.created_date,
        }

        return data

class InstcFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.InstrumentCode

    name = factory.lazy_attribute(lambda o: faker.word())
    nom = factory.lazy_attribute(lambda o: faker.word())
    description_en = factory.lazy_attribute(lambda o: faker.text())
    description_fr = factory.lazy_attribute(lambda o: faker.text())
    created_by = factory.lazy_attribute(lambda o: faker.name())
    created_date = factory.lazy_attribute(lambda o: faker.date())

    @staticmethod
    def build_valid_data(**kwargs):
        # There are a couple of ways to get data out of a Factory
        #
        # Create an instance (BioFactoryFloor.InstFactory() or BioFactoryFloor.InstFactory.create()). This will make
        # an entry in the database and return the object.
        #
        # Build an instance (BioFactoryFloor.InstFactory.build()). This will create an instance of the object, but not
        # enter it in the database.
        #
        # Similar there are Create and Build batches (BioFactoryFloor.InstFactory.create_batch(),
        # BioFactoryFloor.InstFactory.build_batch()) which will produce multiple instances of objects.

        # In this case I created the data, as a dictionary, but didn't want that entered into the database. I just want
        # an dictionary of data to pass to the test method to ensure the creation form puts the data in the database
        # correctly.

        obj = InstcFactory.build(**kwargs)

        # Convert the data to a dictionary to be used in testing
        data = {
            'name': obj.name,
            'nom': obj.nom,
            'description_en': obj.description_en,
            'description_fr': obj.description_fr,
            'created_by': obj.created_by,
            'created_date': obj.created_date,
        }

        return data