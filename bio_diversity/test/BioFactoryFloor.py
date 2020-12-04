import factory
from faker import Factory

from bio_diversity import models

faker = Factory.create()


class ContdcFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ContainerDetCode

    name = factory.lazy_attribute(lambda o: faker.word())
    nom = factory.lazy_attribute(lambda o: faker.word())
    description_en = factory.lazy_attribute(lambda o: faker.text())
    description_fr = factory.lazy_attribute(lambda o: faker.text())
    min_val = factory.lazy_attribute(lambda o: faker.random_int(1, 1000))
    max_val = factory.lazy_attribute(lambda o: faker.random_int(1000, 2000))
    unit_id = factory.SubFactory("bio_diversity.test.BioFactoryFloor.UnitFactory")
    cont_subj_flag = factory.lazy_attribute(lambda o: faker.random_letter())
    created_by = factory.lazy_attribute(lambda o: faker.name())
    created_date = factory.lazy_attribute(lambda o: faker.date())

    @staticmethod
    def build_valid_data(**kwargs):
        unit = UnitFactory()
        obj = ContdcFactory.build(**kwargs)

        # Convert the data to a dictionary to be used in testing
        data = {
            'name': obj.name,
            'nom': obj.nom,
            'description_en': obj.description_en,
            'description_fr': obj.description_fr,
            'min_val': obj.min_val,
            'max_val': obj.max_val,
            'unit_id': unit.pk,
            'cont_subj_flag': obj.cont_subj_flag,
            'created_by': obj.created_by,
            'created_date': obj.created_date,
        }

        return data


class CdscFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ContDetSubjCode

    contdc_id = factory.SubFactory("bio_diversity.test.BioFactoryFloor.ContdcFactory")
    name = factory.lazy_attribute(lambda o: faker.word())
    nom = factory.lazy_attribute(lambda o: faker.word())
    description_en = factory.lazy_attribute(lambda o: faker.text())
    description_fr = factory.lazy_attribute(lambda o: faker.text())
    created_by = factory.lazy_attribute(lambda o: faker.name())
    created_date = factory.lazy_attribute(lambda o: faker.date())

    @staticmethod
    def build_valid_data(**kwargs):
        contdc = ContdcFactory()
        obj = ContdcFactory.build(**kwargs)

        # Convert the data to a dictionary to be used in testing
        data = {
            'contdc_id': contdc.pk,
            'name': obj.name,
            'nom': obj.nom,
            'description_en': obj.description_en,
            'description_fr': obj.description_fr,
            'created_by': obj.created_by,
            'created_date': obj.created_date,
        }

        return data


class CupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Cup

    name = factory.lazy_attribute(lambda o: faker.word())
    nom = factory.lazy_attribute(lambda o: faker.word())
    description_en = factory.lazy_attribute(lambda o: faker.text())
    description_fr = factory.lazy_attribute(lambda o: faker.text())
    created_by = factory.lazy_attribute(lambda o: faker.name())
    created_date = factory.lazy_attribute(lambda o: faker.date())

    @staticmethod
    def build_valid_data(**kwargs):
        obj = CupFactory.build(**kwargs)

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


class CupdFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.CupDet

    contdc_id = factory.SubFactory("bio_diversity.test.BioFactoryFloor.ContdcFactory")
    cup_id = factory.SubFactory("bio_diversity.test.BioFactoryFloor.CupFactory")

    det_value = factory.lazy_attribute(lambda o: faker.random_number(1, 1000))
    cdsc_id = factory.SubFactory("bio_diversity.test.BioFactoryFloor.CdscFactory")
    start_date = factory.lazy_attribute(lambda o: faker.date())
    end_date = factory.lazy_attribute(lambda o: faker.date())
    det_valid = factory.lazy_attribute(lambda o: faker.boolean())
    comments = factory.lazy_attribute(lambda o: faker.text())
    created_by = factory.lazy_attribute(lambda o: faker.name())
    created_date = factory.lazy_attribute(lambda o: faker.date())

    @staticmethod
    def build_valid_data(**kwargs):

        contdc = ContdcFactory()
        cup = CupFactory()
        cdsc = CdscFactory()
        obj = CupdFactory.build(**kwargs)

        # Convert the data to a dictionary to be used in testing
        data = {
            'contdc_id': contdc.pk,
            'cup_id': cup.pk,
            'det_value': obj.det_value,
            'cdsc_id': cdsc.pk,
            'start_date': obj.start_date,
            'end_date': obj.end_date,
            'det_valid': obj.det_valid,
            'comments': obj.comments,
            'created_by': obj.created_by,
            'created_date': obj.created_date,
        }

        return data


class HeatFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.HeathUnit

    name = factory.lazy_attribute(lambda o: faker.word())
    nom = factory.lazy_attribute(lambda o: faker.word())
    description_en = factory.lazy_attribute(lambda o: faker.text())
    description_fr = factory.lazy_attribute(lambda o: faker.text())
    manufacturer = factory.lazy_attribute(lambda o: faker.word())
    inservice_date = factory.lazy_attribute(lambda o: faker.date())
    serial_number = factory.lazy_attribute(lambda o: faker.word())
    created_by = factory.lazy_attribute(lambda o: faker.name())
    created_date = factory.lazy_attribute(lambda o: faker.date())

    @staticmethod
    def build_valid_data(**kwargs):
        obj = HeatFactory.build(**kwargs)

        # Convert the data to a dictionary to be used in testing
        data = {
            'name': obj.name,
            'nom': obj.nom,
            'description_en': obj.description_en,
            'description_fr': obj.description_fr,
            'manufacturer': obj.manufacturer,
            'inservice_date': obj.inservice_date,
            'serial_number': obj.serial_number,
            'created_by': obj.created_by,
            'created_date': obj.created_date,
        }

        return data


class HeatdFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.HeathUnitDet

    contdc_id = factory.SubFactory("bio_diversity.test.BioFactoryFloor.ContdcFactory")
    heat_id = factory.SubFactory("bio_diversity.test.BioFactoryFloor.HeatFactory")
    det_value = factory.lazy_attribute(lambda o: faker.random_number(1, 1000))
    cdsc_id = factory.SubFactory("bio_diversity.test.BioFactoryFloor.CdscFactory")
    start_date = factory.lazy_attribute(lambda o: faker.date())
    end_date = factory.lazy_attribute(lambda o: faker.date())
    det_valid = factory.lazy_attribute(lambda o: faker.boolean())
    comments = factory.lazy_attribute(lambda o: faker.text())
    created_by = factory.lazy_attribute(lambda o: faker.name())
    created_date = factory.lazy_attribute(lambda o: faker.date())

    @staticmethod
    def build_valid_data(**kwargs):

        contdc = ContdcFactory()
        heat = HeatFactory()
        cdsc = CdscFactory()
        obj = HeatdFactory.build(**kwargs)

        # Convert the data to a dictionary to be used in testing
        data = {
            'contdc_id': contdc.pk,
            'heat_id': heat.pk,
            'det_value': obj.det_value,
            'cdsc_id': cdsc.pk,
            'start_date': obj.start_date,
            'end_date': obj.end_date,
            'det_valid': obj.det_valid,
            'comments': obj.comments,
            'created_by': obj.created_by,
            'created_date': obj.created_date,
        }

        return data



class InstFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Instrument

    # needs an instcode id
    instc = factory.SubFactory("bio_diversity.test.BioFactoryFloor.InstcFactory")
    serial_number = factory.lazy_attribute(lambda o: faker.word())
    comments = factory.lazy_attribute(lambda o: faker.text())
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

        instc = InstcFactory()

        obj = InstFactory.build(**kwargs)

        # Convert the data to a dictionary to be used in testing
        data = {
            'instc': instc.pk,
            'serial_number': obj.serial_number,
            'comments': obj.comments,
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


class InstdFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.InstrumentDet

    # needs an inst id
    inst = factory.SubFactory("bio_diversity.test.BioFactoryFloor.InstFactory")
    instdc = factory.SubFactory("bio_diversity.test.BioFactoryFloor.InstdcFactory")
    det_value = factory.lazy_attribute(lambda o: faker.random_int(1, 1000))
    start_date = factory.lazy_attribute(lambda o: faker.date())
    end_date = factory.lazy_attribute(lambda o: faker.date())
    valid = factory.lazy_attribute(lambda o: faker.boolean())
    comments = factory.lazy_attribute(lambda o: faker.text())
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

        inst = InstFactory()
        instdc = InstdcFactory()

        obj = InstdFactory.build(**kwargs)

        # Convert the data to a dictionary to be used in testing
        data = {
            'inst': inst.pk,
            'instdc': instdc.pk,
            'det_value': obj.det_value,
            'start_date': obj.start_date,
            'end_date': obj.end_date,
            'valid': obj.valid,
            'comments': obj.comments,
            'created_by': obj.created_by,
            'created_date': obj.created_date,
        }

        return data


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


class OrgaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Organization

    name = factory.lazy_attribute(lambda o: faker.word())
    nom = factory.lazy_attribute(lambda o: faker.word())
    description_en = factory.lazy_attribute(lambda o: faker.text())
    description_fr = factory.lazy_attribute(lambda o: faker.text())
    created_by = factory.lazy_attribute(lambda o: faker.name())
    created_date = factory.lazy_attribute(lambda o: faker.date())

    @staticmethod
    def build_valid_data(**kwargs):

        obj = OrgaFactory.build(**kwargs)

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


class ProgFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Program

    prog_name = factory.lazy_attribute(lambda o: faker.word())
    prog_desc = factory.lazy_attribute(lambda o: faker.text())
    proga_id = factory.SubFactory("bio_diversity.test.BioFactoryFloor.ProgaFactory")
    orga_id = factory.SubFactory("bio_diversity.test.BioFactoryFloor.OrgaFactory")
    start_date = factory.lazy_attribute(lambda o: faker.date())
    end_date = factory.lazy_attribute(lambda o: faker.date())
    valid = factory.lazy_attribute(lambda o: faker.boolean())
    comments = factory.lazy_attribute(lambda o: faker.text())
    created_by = factory.lazy_attribute(lambda o: faker.name())
    created_date = factory.lazy_attribute(lambda o: faker.date())

    @staticmethod
    def build_valid_data(**kwargs):
        proga = ProgaFactory()
        orga = OrgaFactory()

        obj = ProgFactory.build(**kwargs)

        # Convert the data to a dictionary to be used in testing
        data = {
            'prog_name': obj.prog_name,
            'prog_desc': obj.prog_desc,
            'proga_id': proga.pk,
            'orga_id': orga.pk,
            'start_date': obj.start_date,
            'end_date': obj.end_date,
            'valid': obj.valid,
            'comments': obj.comments,
            'created_by': obj.created_by,
            'created_date': obj.created_date,
        }

        return data


class ProgaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ProgAuthority

    proga_last_name = factory.lazy_attribute(lambda o: faker.word())
    proga_first_name = factory.lazy_attribute(lambda o: faker.word())
    created_by = factory.lazy_attribute(lambda o: faker.name())
    created_date = factory.lazy_attribute(lambda o: faker.date())

    @staticmethod
    def build_valid_data(**kwargs):

        obj = ProgaFactory.build(**kwargs)

        # Convert the data to a dictionary to be used in testing
        data = {
            'proga_last_name': obj.proga_last_name,
            'proga_first_name': obj.proga_first_name,
            'created_by': obj.created_by,
            'created_date': obj.created_date,
        }

        return data


class ProtFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Protocol

    prog_id = factory.SubFactory("bio_diversity.test.BioFactoryFloor.ProgFactory")
    protc_id = factory.SubFactory("bio_diversity.test.BioFactoryFloor.ProtcFactory")
    # protf_id = factory.SubFactory("bio_diversity.test.BioFactoryFloor.ProtfFactory")
    prot_desc = factory.lazy_attribute(lambda o: faker.text())
    start_date = factory.lazy_attribute(lambda o: faker.date())
    end_date = factory.lazy_attribute(lambda o: faker.date())
    valid = factory.lazy_attribute(lambda o: faker.boolean())
    comments = factory.lazy_attribute(lambda o: faker.text())
    created_by = factory.lazy_attribute(lambda o: faker.name())
    created_date = factory.lazy_attribute(lambda o: faker.date())

    @staticmethod
    def build_valid_data(**kwargs):
        prog = ProgFactory()
        protc = ProtcFactory()
        # protf = ProtFactory()

        obj = ProtFactory.build(**kwargs)

        # Convert the data to a dictionary to be used in testing
        data = {
            'prog_id': prog.pk,
            'protc_id': protc.pk,
            # 'protf_id' : protf.pk,
            'prot_desc': obj.prot_desc,
            'start_date': obj.start_date,
            'end_date': obj.end_date,
            'valid': obj.valid,
            'comments': obj.comments,
            'created_by': obj.created_by,
            'created_date': obj.created_date,
        }

        return data


class ProtcFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ProtoCode

    name = factory.lazy_attribute(lambda o: faker.word())
    nom = factory.lazy_attribute(lambda o: faker.word())
    description_en = factory.lazy_attribute(lambda o: faker.text())
    description_fr = factory.lazy_attribute(lambda o: faker.text())
    created_by = factory.lazy_attribute(lambda o: faker.name())
    created_date = factory.lazy_attribute(lambda o: faker.date())

    @staticmethod
    def build_valid_data(**kwargs):

        obj = ProtcFactory.build(**kwargs)

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


class ProtfFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Protofile

    prot_id = factory.SubFactory("bio_diversity.test.BioFactoryFloor.ProtFactory")
    protf_pdf = factory.lazy_attribute(lambda o: faker.url())
    comments = factory.lazy_attribute(lambda o: faker.text())
    created_by = factory.lazy_attribute(lambda o: faker.name())
    created_date = factory.lazy_attribute(lambda o: faker.date())

    @staticmethod
    def build_valid_data(**kwargs):

        prot = ProtFactory()
        obj = ProtfFactory.build(**kwargs)

        # Convert the data to a dictionary to be used in testing
        data = {
            'prot_id': prot.pk,
            'comments': obj.comments,
            'created_by': obj.created_by,
            'created_date': obj.created_date,
        }

        return data


class TankFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Tank

    name = factory.lazy_attribute(lambda o: faker.word())
    nom = factory.lazy_attribute(lambda o: faker.word())
    description_en = factory.lazy_attribute(lambda o: faker.text())
    description_fr = factory.lazy_attribute(lambda o: faker.text())
    created_by = factory.lazy_attribute(lambda o: faker.name())
    created_date = factory.lazy_attribute(lambda o: faker.date())

    @staticmethod
    def build_valid_data(**kwargs):
        obj = TankFactory.build(**kwargs)

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


class TankdFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TankDet

    contdc_id = factory.SubFactory("bio_diversity.test.BioFactoryFloor.ContdcFactory")
    tank_id = factory.SubFactory("bio_diversity.test.BioFactoryFloor.TankFactory")

    det_value = factory.lazy_attribute(lambda o: faker.random_number(1, 1000))
    cdsc_id = factory.SubFactory("bio_diversity.test.BioFactoryFloor.CdscFactory")
    start_date = factory.lazy_attribute(lambda o: faker.date())
    end_date = factory.lazy_attribute(lambda o: faker.date())
    det_valid = factory.lazy_attribute(lambda o: faker.boolean())
    comments = factory.lazy_attribute(lambda o: faker.text())
    created_by = factory.lazy_attribute(lambda o: faker.name())
    created_date = factory.lazy_attribute(lambda o: faker.date())

    @staticmethod
    def build_valid_data(**kwargs):
        contdc = ContdcFactory()
        tank = TankFactory()
        cdsc = CdscFactory()
        obj = TankdFactory.build(**kwargs)

        # Convert the data to a dictionary to be used in testing
        data = {
            'contdc_id': contdc.pk,
            'tank_id': tank.pk,
            'det_value': obj.det_value,
            'cdsc_id': cdsc.pk,
            'start_date': obj.start_date,
            'end_date': obj.end_date,
            'det_valid': obj.det_valid,
            'comments': obj.comments,
            'created_by': obj.created_by,
            'created_date': obj.created_date,
        }

        return data


class TrayFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Tray

    name = factory.lazy_attribute(lambda o: faker.word())
    nom = factory.lazy_attribute(lambda o: faker.word())
    description_en = factory.lazy_attribute(lambda o: faker.text())
    description_fr = factory.lazy_attribute(lambda o: faker.text())
    created_by = factory.lazy_attribute(lambda o: faker.name())
    created_date = factory.lazy_attribute(lambda o: faker.date())

    @staticmethod
    def build_valid_data(**kwargs):
        obj = TrayFactory.build(**kwargs)

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


class TraydFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TrayDet

    contdc_id = factory.SubFactory("bio_diversity.test.BioFactoryFloor.ContdcFactory")
    tray_id = factory.SubFactory("bio_diversity.test.BioFactoryFloor.TrayFactory")

    det_value = factory.lazy_attribute(lambda o: faker.random_number(1, 1000))
    cdsc_id = factory.SubFactory("bio_diversity.test.BioFactoryFloor.CdscFactory")
    start_date = factory.lazy_attribute(lambda o: faker.date())
    end_date = factory.lazy_attribute(lambda o: faker.date())
    det_valid = factory.lazy_attribute(lambda o: faker.boolean())
    comments = factory.lazy_attribute(lambda o: faker.text())
    created_by = factory.lazy_attribute(lambda o: faker.name())
    created_date = factory.lazy_attribute(lambda o: faker.date())

    @staticmethod
    def build_valid_data(**kwargs):
        contdc = ContdcFactory()
        tray = TrayFactory()
        cdsc = CdscFactory()
        obj = TraydFactory.build(**kwargs)

        # Convert the data to a dictionary to be used in testing
        data = {
            'contdc_id': contdc.pk,
            'tray_id': tray.pk,
            'det_value': obj.det_value,
            'cdsc_id': cdsc.pk,
            'start_date': obj.start_date,
            'end_date': obj.end_date,
            'det_valid': obj.det_valid,
            'comments': obj.comments,
            'created_by': obj.created_by,
            'created_date': obj.created_date,
        }

        return data

class TrofFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Trough

    name = factory.lazy_attribute(lambda o: faker.word())
    nom = factory.lazy_attribute(lambda o: faker.word())
    description_en = factory.lazy_attribute(lambda o: faker.text())
    description_fr = factory.lazy_attribute(lambda o: faker.text())
    created_by = factory.lazy_attribute(lambda o: faker.name())
    created_date = factory.lazy_attribute(lambda o: faker.date())

    @staticmethod
    def build_valid_data(**kwargs):
        obj = TrofFactory.build(**kwargs)

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


class TrofdFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TroughDet

    contdc_id = factory.SubFactory("bio_diversity.test.BioFactoryFloor.ContdcFactory")
    trof_id = factory.SubFactory("bio_diversity.test.BioFactoryFloor.TrofFactory")

    det_value = factory.lazy_attribute(lambda o: faker.random_number(1, 1000))
    cdsc_id = factory.SubFactory("bio_diversity.test.BioFactoryFloor.CdscFactory")
    start_date = factory.lazy_attribute(lambda o: faker.date())
    end_date = factory.lazy_attribute(lambda o: faker.date())
    det_valid = factory.lazy_attribute(lambda o: faker.boolean())
    comments = factory.lazy_attribute(lambda o: faker.text())
    created_by = factory.lazy_attribute(lambda o: faker.name())
    created_date = factory.lazy_attribute(lambda o: faker.date())

    @staticmethod
    def build_valid_data(**kwargs):
        contdc = ContdcFactory()
        trof = TrofFactory()
        cdsc = CdscFactory()
        obj = TrofdFactory.build(**kwargs)

        # Convert the data to a dictionary to be used in testing
        data = {
            'contdc_id': contdc.pk,
            'trof_id': trof.pk,
            'det_value': obj.det_value,
            'cdsc_id': cdsc.pk,
            'start_date': obj.start_date,
            'end_date': obj.end_date,
            'det_valid': obj.det_valid,
            'comments': obj.comments,
            'created_by': obj.created_by,
            'created_date': obj.created_date,
        }

        return data


class UnitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.UnitCode

    name = factory.lazy_attribute(lambda o: faker.word())
    nom = factory.lazy_attribute(lambda o: faker.word())
    description_en = factory.lazy_attribute(lambda o: faker.text())
    description_fr = factory.lazy_attribute(lambda o: faker.text())
    created_by = factory.lazy_attribute(lambda o: faker.name())
    created_date = factory.lazy_attribute(lambda o: faker.date())

    @staticmethod
    def build_valid_data(**kwargs):

        obj = UnitFactory.build(**kwargs)

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
