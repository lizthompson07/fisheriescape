import factory
from django.utils import timezone
from faker import Factory

from shared_models.test.SharedModelsFactoryFloor import ProvinceFactory
from .. import models

faker = Factory.create()


class SpeciesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Species

    common_name = factory.lazy_attribute(lambda o: faker.word())
    common_name_fra = factory.lazy_attribute(lambda o: faker.word())
    color_morph = factory.lazy_attribute(lambda o: faker.pybool())
    invasive = factory.lazy_attribute(lambda o: faker.pybool())

    @staticmethod
    def get_valid_data():
        return {
            'common_name': faker.word(),
            'common_name_fra': faker.word(),
            'color_morph': faker.pybool(),
            'invasive': faker.pybool(),
        }


class SamplerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Sampler

    first_name = factory.lazy_attribute(lambda o: faker.first_name())
    last_name = factory.lazy_attribute(lambda o: faker.last_name())
    email = factory.lazy_attribute(lambda o: faker.email())

    @staticmethod
    def get_valid_data():
        return {
            'first_name': faker.first_name(),
            'last_name': faker.last_name(),
            'email': faker.email(),
        }


class StationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Station

    province = factory.SubFactory(ProvinceFactory)
    station_name = factory.lazy_attribute(lambda o: faker.word())

    @staticmethod
    def get_valid_data():
        return {
            'province': ProvinceFactory().id,
            'station_name': faker.word(),
        }


class SampleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Sample

    station = factory.SubFactory(StationFactory)
    sample_type = 'full'
    date_deployed = factory.lazy_attribute(lambda o: faker.date_time_this_year(tzinfo=timezone.get_current_timezone()))

    @staticmethod
    def get_valid_data():
        return {
            'station': StationFactory().id,
            'sample_type': 'full',
            'date_deployed': faker.date_time_this_year(tzinfo=timezone.get_current_timezone()),
            'samplers': [SamplerFactory().id, ]
        }


class SampleNoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.SampleNote

    sample = factory.SubFactory(SampleFactory)
    note = factory.lazy_attribute(lambda o: faker.text())
    date = factory.lazy_attribute(lambda o: faker.date_time_this_year(tzinfo=timezone.get_current_timezone()))

    @staticmethod
    def get_valid_data():
        return {
            'sample': SampleFactory().id,
            'note': faker.text(),
            'date': faker.date_time_this_year(tzinfo=timezone.get_current_timezone()),
        }


class LineFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Line

    sample = factory.SubFactory(SampleFactory)
    is_lost = factory.lazy_attribute(lambda o: faker.pybool())

    @staticmethod
    def get_valid_data():
        return {
            'sample': SamplerFactory().id,
            'is_lost': faker.pybool(),
        }


class SurfaceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Surface

    line = factory.SubFactory(LineFactory)
    surface_type = factory.lazy_attribute(lambda o: models.Surface.SURFACE_TYPE_CHOICES[faker.random_int(0, len(models.Surface.SURFACE_TYPE_CHOICES) - 1)][0])
    label = factory.lazy_attribute(lambda o: faker.catch_phrase())
    is_lost = factory.lazy_attribute(lambda o: faker.pybool())
    is_damaged = factory.lazy_attribute(lambda o: faker.pybool())

    @staticmethod
    def get_valid_data():
        return {
            'line': LineFactory().id,
            'surface_type': models.Surface.SURFACE_TYPE_CHOICES[faker.random_int(0, len(models.Surface.SURFACE_TYPE_CHOICES) - 1)][0],
            'label': faker.catch_phrase(),
            'is_lost': faker.pybool(),
            'is_damaged': faker.pybool(),
        }


class ProbeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Probe

    probe_name = factory.lazy_attribute(lambda o: faker.word())

    @staticmethod
    def get_valid_data():
        return {
            'probe_name': faker.word(),
        }


class ProbeMeasurementFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ProbeMeasurement

    sample = factory.SubFactory(SampleFactory)
    probe = factory.SubFactory(ProbeFactory)
    time_date = factory.lazy_attribute(lambda o: faker.date_time_this_year(tzinfo=timezone.get_current_timezone()))
    temp_c = factory.lazy_attribute(lambda o: faker.pyfloat(positive=True))

    @staticmethod
    def get_valid_data():
        return {
            'sample': SampleFactory().id,
            'probe': ProbeFactory().id,
            'time_date': faker.date_time_this_year(tzinfo=timezone.get_current_timezone()),
            'temp_c': faker.pyfloat(positive=True),
        }


class IncidentalReportFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.IncidentalReport

    report_date = factory.lazy_attribute(lambda o: faker.date_time_this_year(tzinfo=timezone.get_current_timezone()))
    date_of_occurrence = factory.lazy_attribute(lambda o: faker.date_time_this_year(tzinfo=timezone.get_current_timezone()))
    language_of_report = factory.lazy_attribute(lambda o: faker.pyint())
    requestor_name = factory.lazy_attribute(lambda o: faker.word())
    report_source = factory.lazy_attribute(lambda o: faker.pyint())
    observation_type = factory.lazy_attribute(lambda o: faker.pyint())

    @staticmethod
    def get_valid_data():
        return {
            'report_date': faker.date_time_this_year(tzinfo=timezone.get_current_timezone()),
            'date_of_occurrence': faker.date_time_this_year(tzinfo=timezone.get_current_timezone()),
            'language_of_report': 1,
            'requestor_name': faker.word(),
            'report_source': 1,
            'observation_type': 1,
        }


class FollowUpFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.FollowUp

    incidental_report = factory.SubFactory(IncidentalReportFactory)
    date = factory.lazy_attribute(lambda o: faker.date_time_this_year(tzinfo=timezone.get_current_timezone()))
    note = factory.lazy_attribute(lambda o: faker.text())

    @staticmethod
    def get_valid_data():
        return {
            'incidental_report': IncidentalReportFactory().id,
            'date': faker.date_time_this_year(tzinfo=timezone.get_current_timezone()),
            'note': faker.text(),
        }


class EstuaryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Estuary

    province = factory.SubFactory(ProvinceFactory)
    name = factory.lazy_attribute(lambda o: faker.catch_phrase())

    @staticmethod
    def get_valid_data():
        return {
            'province': ProvinceFactory().id,
            'name': faker.catch_phrase(),
        }


class SiteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Site

    estuary = factory.SubFactory(EstuaryFactory)
    code = factory.lazy_attribute(lambda o: faker.word())
    name = factory.lazy_attribute(lambda o: faker.catch_phrase())

    @staticmethod
    def get_valid_data():
        return {
            'estuary': EstuaryFactory().id,
            'code': faker.word(),
            'name': faker.catch_phrase(),
        }


class GCSampleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.GCSample

    site = factory.SubFactory(SiteFactory)
    traps_set = factory.lazy_attribute(lambda o: faker.date_time_this_year(tzinfo=timezone.get_current_timezone()))

    @staticmethod
    def get_valid_data():
        return {
            'site': SiteFactory().id,
            'traps_set': faker.date_time_this_year(tzinfo=timezone.get_current_timezone()),
            'samplers': [SamplerFactory().id, ]

        }


class WeatherConditionsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.WeatherConditions

    name = factory.lazy_attribute(lambda o: faker.catch_phrase())

    @staticmethod
    def get_valid_data():
        return {
            'name': faker.catch_phrase(),
        }


class GCProbeMeasurementFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.GCProbeMeasurement

    sample = factory.SubFactory(GCSampleFactory)
    probe = factory.SubFactory(ProbeFactory)
    time_date = factory.lazy_attribute(lambda o: faker.date_time_this_year(tzinfo=timezone.get_current_timezone()))
    temp_c = factory.lazy_attribute(lambda o: faker.pyfloat(positive=True))

    @staticmethod
    def get_valid_data():
        return {
            'sample': GCSampleFactory().id,
            'probe': ProbeFactory().id,
            'time_date': faker.date_time_this_year(tzinfo=timezone.get_current_timezone()),
            'temp_c': faker.pyfloat(positive=True),
        }


class BaitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Bait

    name = factory.lazy_attribute(lambda o: faker.catch_phrase())

    @staticmethod
    def get_valid_data():
        return {
            'name': faker.catch_prase(),
        }


class TrapFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Trap

    sample = factory.SubFactory(GCSampleFactory)
    bait_type = factory.SubFactory(BaitFactory)
    trap_number = factory.lazy_attribute(lambda o: faker.pyint(1, 100))
    trap_type = factory.lazy_attribute(lambda o: 1)

    @staticmethod
    def get_valid_data():
        return {
            'sample': GCSampleFactory().id,
            'trap_number': faker.pyint(1, 100),
            'trap_type': 1,
            'bait_type': BaitFactory().id,
        }


class CatchFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Catch

    trap = factory.SubFactory(TrapFactory)
    species = factory.SubFactory(SpeciesFactory)

    @staticmethod
    def get_valid_data():
        return {
            'trap': TrapFactory().id,
            'species': SpeciesFactory().id,
        }


class SampleSpeciesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.SampleSpecies

    species = factory.SubFactory(SpeciesFactory)
    sample = factory.SubFactory(SampleFactory)
    observation_date = factory.lazy_attribute(lambda o: faker.date_time_this_year(tzinfo=timezone.get_current_timezone()))

    @staticmethod
    def get_valid_data():
        return {
            'species': SpeciesFactory().id,
            'sample': SampleFactory().id,
            'observation_date': faker.date_time_this_year(tzinfo=timezone.get_current_timezone()).strftime("%Y-%m-%dT%H:%M"),
        }


class LineSpeciesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.LineSpecies

    species = factory.SubFactory(SpeciesFactory)
    line = factory.SubFactory(LineFactory)
    observation_date = factory.lazy_attribute(lambda o: faker.date_time_this_year(tzinfo=timezone.get_current_timezone()))

    @staticmethod
    def get_valid_data():
        return {
            'species': SpeciesFactory().id,
            'line': LineFactory().id,
            'observation_date': faker.date_time_this_year(tzinfo=timezone.get_current_timezone()).strftime("%Y-%m-%dT%H:%M"),
        }


class SurfaceSpeciesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.SurfaceSpecies

    species = factory.SubFactory(SpeciesFactory)
    surface = factory.SubFactory(SurfaceFactory)
    percent_coverage = factory.lazy_attribute(lambda o: 0)

    @staticmethod
    def get_valid_data():
        return {
            'species': SpeciesFactory().id,
            'surface': SurfaceFactory().id,
            'percent_coverage': 0,
        }


class IncidentalReportSpeciesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.IncidentalReportSpecies

    species = factory.SubFactory(SpeciesFactory)
    incidental_report = factory.SubFactory(IncidentalReportFactory)

    @staticmethod
    def get_valid_data():
        return {
            'species': SpeciesFactory().id,
            'incidental_report': IncidentalReportFactory().id,
            'observation_date': faker.date_time_this_year(tzinfo=timezone.get_current_timezone()).strftime("%Y-%m-%dT%H:%M"),
        }


class CatchSpeciesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Catch

    species = factory.SubFactory(SpeciesFactory)
    trap = factory.SubFactory(TrapFactory)

    @staticmethod
    def get_valid_data():
        return {
            'species': SpeciesFactory().id,
            'trap': TrapFactory().id,
        }
