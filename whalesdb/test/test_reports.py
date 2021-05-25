import datetime
import csv as csv_reader
from django.test import TestCase, tag
from django.http import QueryDict
from . import WhalesdbFactoryFloor as whale_factory
from .. import models
from .. import reports

@tag("reports")
class TestDepSummary(TestCase):
    fixtures = ['initial_whale_data.json', 'institute.json']

    EXPECTED_HEADER = ['EDA_ID', 'Year', 'Month', 'Deployment', 'Station', "Project", 'Latitude', 'Longitude',
                       'Depth_m', 'Equipment make_model_serial', 'Hydrophone make_model_serial', 'Dataset timezone',
                       'Recording schedule', 'In-water_start', 'In-water_end', 'Dataset notes']

    EXPECTED_COUNT_2014 = 3
    EXPECTED_COUNT_2013 = 10
    EXPECTED_COUNT_2012 = 5

    EXPECTED_YEAR_COL = 1
    EXPECTED_MONTH_COL = 2
    EXPECTED_STATION_COL = 4
    EXPECTED_PROJECT_COL = 5

    EXPECTED_STATION_PK = -1
    EXPECTED_PROJECT_PK = -1

    def setUp(self):
        super().setUp()

        whale_factory.DepFactory.create_batch(self.EXPECTED_COUNT_2012, dep_year=2012)
        whale_factory.DepFactory.create_batch(self.EXPECTED_COUNT_2013, dep_year=2013)

        # subtract two from the expected 2014 batch create for the two objects being created later
        # that are in the 2014 year.
        whale_factory.DepFactory.create_batch((self.EXPECTED_COUNT_2014-2), dep_year=2014)

        # months are normally 0-12, I added 13 specifically for querying something that wasn't randomly created
        whale_factory.DepFactory.create(dep_year=2014, dep_month=13)

        # added a station specifically for querying something that wasn't randomly created
        stn = whale_factory.StnFactory.create(stn_name="Test Station", stn_code="TST", stn_revision=1)

        # added a project specifically for querying something that wasn't randomly created
        prj = whale_factory.PrjFactory.create(name="Test project", description_en="Some Project", prj_url="http://test.com")

        self.EXPECTED_STATION_PK = stn.pk
        self.EXPECTED_PROJECT_PK = prj.pk
        whale_factory.DepFactory.create(stn=stn, prj=prj, dep_year=2014)

        dep_objs = models.DepDeployment.objects.all()

        for d in dep_objs:
            whale_factory.EdaFactory.create(dep=d)
            whale_factory.SteFactory.create(dep=d, set_type=models.SetStationEventCode.objects.get(pk=1))

        eda_objs = models.EdaEquipmentAttachment.objects.all()
        for e in eda_objs:
            rec_start_date = datetime.datetime(year=int(e.dep.dep_year), month=1, day=1)
            whale_factory.RecFactory.create(eda_id=e, rec_start_date=rec_start_date)

    # test that all data objects are returned in the csv
    def test_response_no_prams(self):
        lst = QueryDict()
        response = reports.report_deployment_summary(lst)

        self.assertIsNotNone(response)

        csv = csv_reader.reader(response.content.decode('utf-8').splitlines(), delimiter=',')
        header = next(csv, None)

        # check header line
        self.assertEqual(header, self.EXPECTED_HEADER)

        # check the order and counts. returned csv data should be most recent to oldest
        c_2012 = 0
        c_2013 = 0
        c_2014 = 0
        cur = -1
        for line in csv:
            # element 2 of the csv should be the year
            cur = line[self.EXPECTED_YEAR_COL] if cur == -1 or line[self.EXPECTED_YEAR_COL] <= cur else \
                self.fail("Elements are not sorted: cur'{}' last'{}".format(cur, line[self.EXPECTED_YEAR_COL]))
            if int(cur) == 2012:
                c_2012 += 1
            elif int(cur) == 2013:
                c_2013 += 1
            elif int(cur) == 2014:
                c_2014 += 1
            else:
                self.fail("Unexpeted year '{}' found in data".format(cur))

        self.assertEqual(c_2012, self.EXPECTED_COUNT_2012)
        self.assertEqual(c_2013, self.EXPECTED_COUNT_2013)
        self.assertEqual(c_2014, self.EXPECTED_COUNT_2014)

    # test that a start_date filter can be applied to the data objects returned in the csv
    def test_response_start_date_query(self):
        lst = QueryDict('start_date=2014-01-01')
        response = reports.report_deployment_summary(lst)

        self.assertIsNotNone(response)

        csv = csv_reader.reader(response.content.decode('utf-8').splitlines(), delimiter=',')
        header = next(csv, None)
        # only 2014 deployments should be returned
        c_2014 = 0
        cur = -1
        for line in csv:
            # element 2 of the csv should be the year
            cur = line[self.EXPECTED_YEAR_COL] if cur == -1 or line[self.EXPECTED_YEAR_COL] >= cur else \
                self.fail('Elements are not sorted')
            if int(cur) == 2014:
                c_2014 += 1
            else:
                self.fail("Unexpeted year '{}' found in data".format(cur))

        # we should only have objects that were entered for or after the year 2014
        self.assertEqual(c_2014, self.EXPECTED_COUNT_2014)

    # test that an end_date filter can be applied to the data objects returned in the csv
    def test_response_end_date_query(self):
        lst = QueryDict('end_date=2013-12-31')
        response = reports.report_deployment_summary(lst)

        self.assertIsNotNone(response)

        csv = csv_reader.reader(response.content.decode('utf-8').splitlines(), delimiter=',')
        header = next(csv, None)
        # only month 13 deployments should be returned
        row_count = 0
        cur = -1
        for line in csv:
            # element 2 of the csv should be the year
            cur = line[self.EXPECTED_YEAR_COL] if cur == -1 or line[self.EXPECTED_YEAR_COL] <= cur else \
                self.fail('Elements are not sorted')
            if int(cur) == 2014:
                self.fail("Unexpeted year '{}' found in data".format(cur))
            else:
                row_count += 1

        self.assertEqual(row_count, (self.EXPECTED_COUNT_2012 + self.EXPECTED_COUNT_2013))

    # test that a station filter can be applied to the data objects returned in the csv
    def test_response_stn_query(self):
        lst = QueryDict(f'station={self.EXPECTED_STATION_PK}')
        response = reports.report_deployment_summary(lst)

        self.assertIsNotNone(response)

        expected_station = models.StnStation.objects.get(pk=self.EXPECTED_STATION_PK)
        csv = csv_reader.reader(response.content.decode('utf-8').splitlines(), delimiter=',')
        header = next(csv, None)
        # only month 13 deployments should be returned
        res_count = 0
        for line in csv:
            stn = line[self.EXPECTED_STATION_COL]
            self.assertEqual(stn, str(expected_station))
            res_count += 1

        self.assertEqual(res_count, 1)

    # test that a Project filter can be applied to the data objects returned in the csv
    def test_response_prj_query(self):
        lst = QueryDict(f'project={self.EXPECTED_PROJECT_PK}')
        response = reports.report_deployment_summary(lst)

        self.assertIsNotNone(response)

        expected_project = models.PrjProject.objects.get(pk=self.EXPECTED_PROJECT_PK)
        csv = csv_reader.reader(response.content.decode('utf-8').splitlines(), delimiter=',')
        header = next(csv, None)
        # only month 13 deployments should be returned
        res_count = 0
        for line in csv:
            stn = line[self.EXPECTED_PROJECT_COL]
            self.assertEqual(stn, str(expected_project))
            res_count += 1

        self.assertEqual(res_count, 1)