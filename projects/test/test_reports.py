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
        report = reports.CovidReport()
        Factory.ProjectFactory(project_title="Test Project")
        Factory.ProjectFactory(project_title="Test Project 2")

        if os.path.exists(report.target_file_path):
            os.remove(report.target_file_path)

        self.assertFalse(os.path.exists(report.target_file_path))
        report.generate_spread_sheet()
        self.assertTrue(os.path.exists(report.target_file_path))

    def assertSharedStringArray(self, strings_array, string_table, offset, section_heading, heading_array):
        self.assertEquals(strings_array._get_shared_string(string_table[0][offset].string), section_heading)

        for i in range(0, len(heading_array)):
            self.assertEquals(strings_array._get_shared_string(string_table[1][i+offset].string),
                              heading_array[i])

    def test_covid_create_worksheet(self):
        self.report.create_worksheets()
        sheet = self.report.get_worksheet(title=self.EXPECTED_WORKSHEETS[0])
        strings_array = sheet.str_table
        table = sheet.table

        # worksheets have a string table that is accessed by [row][column], it has two values
        # .string - an index into a string array
        # .format - the xlswriter.format.Format object describing how to format the cell

        # The SharedStringTable stores strings for the xlswriter, but it hast to be "sorted" before strings can be
        # retirieved from it.
        strings_array._sort_string_data()

        # use to skip blank columns that have been merged for the section heading
        section_offset = 0
        section_heading = self.EXPECTED_SECTION_HEADINGS[0]
        self.assertSharedStringArray(strings_array, table, section_offset, section_heading, self.EXPECTED_OPI_HEADINGS)

        section_offset += len(self.EXPECTED_OPI_HEADINGS)
        section_heading = self.EXPECTED_SECTION_HEADINGS[1]
        self.assertSharedStringArray(strings_array, table, section_offset, section_heading, self.EXPECTED_REC_HEADINGS)

        section_offset += len(self.EXPECTED_REC_HEADINGS)
        section_heading = self.EXPECTED_SECTION_HEADINGS[2]
        self.assertSharedStringArray(strings_array, table, section_offset, section_heading, self.EXPECTED_ANA_HEADINGS)

        section_offset += len(self.EXPECTED_ANA_HEADINGS)
        section_heading = self.EXPECTED_SECTION_HEADINGS[3]
        self.assertSharedStringArray(strings_array, table, section_offset, section_heading, self.EXPECTED_IMP_HEADINGS)

        section_offset += len(self.EXPECTED_IMP_HEADINGS)
        section_heading = self.EXPECTED_SECTION_HEADINGS[4]
        self.assertSharedStringArray(strings_array, table, section_offset, section_heading, self.EXPECTED_MIT_HEADINGS)

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
