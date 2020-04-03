import os
from django.test import TestCase
from django.conf import settings

from projects import reports

from projects.test import ProjectsFactory as Factory


class StdReportTest(TestCase):

    EXPECTED_TARGET_DIR = os.path.join(settings.BASE_DIR, 'media', 'projects', 'temp')
    EXPECTED_TARGET_FILE = "temp_export.xlsx"
    EXPECTED_TARGET_FILE_PATH = os.path.join(EXPECTED_TARGET_DIR, EXPECTED_TARGET_FILE)
    EXPECTED_TARGET_URL = os.path.join(settings.MEDIA_ROOT, 'projects', 'temp', EXPECTED_TARGET_FILE)

    report = None

    def setUp(self) -> None:
        self.report = reports.StdReport()

    def test_std_get_format(self):
        self.assertIsNotNone(self.report.get_format("section_header"))
        self.assertIsNotNone(self.report.get_format("col_header"))
        self.assertIsNotNone(self.report.get_format("normal_text"))

    def test_std_target_output_dir(self):
        self.assertEquals(self.report.target_dir, self.EXPECTED_TARGET_DIR)

    def test_std_target_file(self):
        self.assertEquals(self.report.target_file, self.EXPECTED_TARGET_FILE)

    def test_std_target_file_path(self):
        self.assertEquals(self.report.target_file_path, self.EXPECTED_TARGET_FILE_PATH)

    def test_std_target_url(self):
        self.assertEquals(self.report.target_url, self.EXPECTED_TARGET_URL)

    # I'm not going to test the styling of each format, but I will test that the expect formats exist
    def test_std_cel_formats(self):
        self.assertIn("section_header", self.report.formats)
        self.assertIn("col_header", self.report.formats)
        self.assertIn("normal_text", self.report.formats)

    def test_std_get_workbook(self):
        self.assertIsNotNone(self.report.get_workbook())

    def test_std_get_worksheet(self):
        # by default create and use "Sheet1" as the worksheet title
        sheet = self.report.get_worksheet()
        self.assertIsNotNone(sheet)
        self.assertEquals(sheet.name, "Sheet1")

        # should create a new sheet with the given name
        expected_name = "Test Sheet"
        sheet = self.report.get_worksheet(title=expected_name)
        self.assertIsNotNone(sheet)
        self.assertEquals(sheet.name, expected_name)

        # should return the existing sheet if name exists
        sheet2 = self.report.get_worksheet(title=expected_name)
        self.assertEquals(sheet, sheet2)


class CovidReportTest(TestCase):

    report = None

    EXPECTED_SECTION_HEADINGS = [
        "Original Project Information",
        "Recommendation",
        "Analysis",
        "Impact",
        "Mitigation",
    ]

    EXPECTED_OPI_HEADINGS = [
        "Project/Activity title",
        "Project ID",
        "Division",
        "Section",
        "Activity Type",
        "# of DFO staff involved",
        "# of non-DFO staff involved",
        "Location(s) of activity",
        "Original start date",
        "Original end date",
    ]

    EXPECTED_REC_HEADINGS = ["COVID Recommendation", "Drop dead start date", "Rationale"]
    EXPECTED_ANA_HEADINGS = ["Critical Service?", "Able to maintain social distance?", "Staffing?", "Travel?",
                             "External services?", "Timing"]
    EXPECTED_IMP_HEADINGS = ["Impact of Ministerial Advice", "Impact on Departmental Deliverables",
                             "Impact on Operations"]
    EXPECTED_MIT_HEADINGS = ["Other measures to reduce risk"]

    EXPECTED_WORKSHEETS = ["COVID Assessment"]

    def setUp(self) -> None:
        self.report = reports.CovidReport()

    def test_covid_generate(self):
        Factory.ProjectFactory(project_title="Test Project")
        Factory.ProjectFactory(project_title="Test Project 2")

        if os.path.exists(self.report.target_file_path):
            os.remove(self.report.target_file_path)

        self.assertFalse(os.path.exists(self.report.target_file_path))
        self.report.generate_spread_sheet()
        self.assertTrue(os.path.exists(self.report.target_file_path))

    def test_covid_create_worksheet(self):
        # As far as I can tell there is no way to retrieve a cell's data using the xlswriter API, therefore
        # there's no way to verify the column headers automatically
        self.report.create_worksheets()
        sheet = self.report.get_worksheet(title=self.EXPECTED_WORKSHEETS[0])

    def test_covid_get_worksheet(self):
        sheet = self.report.get_worksheet(title=self.EXPECTED_WORKSHEETS[0])
        self.assertIsNotNone(sheet)
        self.assertEquals(self.EXPECTED_WORKSHEETS[0], sheet.name)

    # create report sections for dividing up headings
    def test_covid_sections(self):
        sections = self.report.get_sections()

        # Test each section has the correct section title
        for i in range(0, len(self.EXPECTED_SECTION_HEADINGS)):
            self.assertEquals(sections[i]["title"], self.EXPECTED_SECTION_HEADINGS[i])

        # test subsections
        # OPI SECTION
        for i in range(0, len(self.EXPECTED_OPI_HEADINGS)):
            self.assertEquals(sections[0]["sub"][i]["title"], self.EXPECTED_OPI_HEADINGS[i])

        # Recommendations SECTION
        for i in range(0, len(self.EXPECTED_REC_HEADINGS)):
            self.assertEquals(sections[1]["sub"][i]["title"], self.EXPECTED_REC_HEADINGS[i])

        # Analysis SECTION
        for i in range(0, len(self.EXPECTED_ANA_HEADINGS)):
            self.assertEquals(sections[2]["sub"][i]["title"], self.EXPECTED_ANA_HEADINGS[i])

        # Impact SECTION
        for i in range(0, len(self.EXPECTED_IMP_HEADINGS)):
            self.assertEquals(sections[3]["sub"][i]["title"], self.EXPECTED_IMP_HEADINGS[i])

        # Mitigation SECTION
        for i in range(0, len(self.EXPECTED_MIT_HEADINGS)):
            self.assertEquals(sections[4]["sub"][i]["title"], self.EXPECTED_MIT_HEADINGS[i])
