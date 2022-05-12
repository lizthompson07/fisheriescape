from django.db import models
from django.utils.translation import gettext_lazy as _


YES_NO_UNKNOWN = (
    ('Yes', 'Yes'),
    ('No', 'No'),
    ('Unknown', 'Unknown'),
    ('Not Applicable', 'Not Applicable')
)

YES_NO = (
    ('Yes', 'Yes'),
    ('No', 'No'),
    ('Flag for archive', 'Flag for archive'),
    ('Flag for scanning', 'Flag for scanning'),

)

YES_NO_FLAG = (
    ('Yes', 'Yes'),
    ('No', 'No'),
)

AGREEMENT_DATABASE = (
    ('APGIS', 'APGIS'),
    ('AAROM Shared Drive', 'AAROM Shared Drive'),
    ('South Coast Shared Drive', 'South Coast Shared Drive'),
    ('North Coast Shared Drive', 'North Coast Shared Drive'),
    ('Fraser/Interior Shared Drive', 'Fraser/Interior Shared Drive'),
    ('Yukon/Transboundary Shared Drive', 'Yukon/Transboundary Shared Drive'),
    ('SEP Shared Drive', 'SEP Shared Drive'),
    ('Unknown', 'Unknown'),
    ('Not Applicable', 'Not Applicable'),
    ('Other', 'Other'),
    ('None', 'None'),
)

AGREEMENT_TYPE = (
    ('Primary Agreement', 'Primary Agreement'),
    ('Amendment', 'Amendment'),
    ('First Nations Treaty Agreement', 'First Nations Treaty Agreement'),
    ('Supply Arrangement', 'Supply Arrangement'),
    ('Contract', 'Contract'),
    ('Unknown', 'Unknown'),
    ('Not applicable', 'Not applicable'),
    ('Other', 'Other'),
)

LEAD_ORGANIZATION = (
    ('First Nations', 'First Nations'),
    ('Stewardship Society', 'Stewardship Society'),
    ('DFO', 'DFO'),
    ('Collaborative', 'Collaborative'),
    ('Unknown', 'Unknown'),
    ('Not applicable', 'Not applicable'),
    ('Other', 'Other')
)

AREA = (
    ("YTRA", "YTRA"),
    ("NCA", "NCA"),
    ("SCA", "SCA"),
    ("FIA", "FIA"),)


PROJECT_STAGE = (
    ('Proposed', 'Proposed'),
    ('Planning', 'Planning'),
    ('Pilot', 'Pilot'),
    ('Active', 'Active'),
    ('Complete', 'Complete'),
    ('Terminated', 'Terminated'),
    ('Unknown', 'Unknown'),
    ('Not applicable', 'Not applicable'),
    ('Other', 'Other'),
)

PROJECT_TYPE = (
    ('Population Science', 'Population Science'),
    ('Habitat Science', 'Habitat Science'),
    ('Infrastructure', 'Infrastructure'),
)

GOVERNMENT_LINK = (
    ('Municipality', 'Municipality'),
    ('Province of British Columbia', 'Province of British Columbia'),
    ('Yukon Territory', 'Yukon Territory'),
    ('Environment Canada', 'Environment Canada'),
    ('Climate Change Canada', 'Climate Change Canada'),
    ('Alaska Department of Fish & Game', 'Alaska Department of Fish & Game'),
    ('Washington State', 'Washington State'),
    ('Unknown', 'Unknown'),
    ('Not Applicable', 'Not Applicable'),
    ('Other', 'Other'),
)

ROLE = (
    ('Chief', 'Chief'),
    ('Biologist', 'Biologist'),
    ('Aquatics Manager', 'Aquatics Manager'),
    ('Technician', 'Technician'),
    ('Director', 'Director'),
    ('Fisheries Manager', 'Fisheries Manager'),
    ('Refuge Manager', 'Refuge Manager'),
    ('Scientist', 'Scientist'),
    ('Stewardship Director', 'Stewardship Director'),
    ('Unknown', 'Unknown'),
    ('Other', 'Other'),
)

COUNTRY_CHOICES = (
    ('Canada', 'Canada'),
    ('United States of America', 'United States of America'),
)

PROVINCE_STATE_CHOICES = (
    ('Alberta', 'Alberta'),
    ('British Columbia', 'British Columbia'),
    ('Manitoba', 'Manitoba'),
    ('New Brunswick', 'New Brunswick'),
    ('Newfoundland & Labrador', 'Newfoundland & Labrador'),
    ('Nova Scotia', 'Nova Scotia'),
    ('Ontario', 'Ontario'),
    ('Prince Edward Island', 'Prince Edward Island'),
    ('Quebec', 'Quebec'),
    ('Saskatchewan', 'Saskatchewan'),
    ('Northwest Territories', 'Northwest Territories'),
    ('Nunavut', 'Nunavut'),
    ('Yukon', 'Yukon'),
    ('Washington', 'Washington'),
    ('Alaska', 'Alaska'),
    ('Oregon', 'Oregon'),
)

ORGANIZATION_TYPE = (
    ('First Nation', 'First Nation'),
    ('Company', 'Company'),
    ('Government', 'Government'),
    ('Non-Profit Organization', 'Non-Profit Organization'),
    ('University', 'University'),
)

PLANNING_METHOD = (
    ('Feasibility Study', 'Feasibility Study'),
    ('Project Design', 'Project Design'),
    ('Resouce Allocation', 'Resouce Allocation'),
    ('Objective-setting', 'Objective-setting'),
    ('Other', 'Other'),
    ('Meeting summary', 'Meeting summary'),
    ('Priority setting', 'Priority setting'),
    ('Not applicable', 'Not applicable'),
)

FIELD_WORK = (
    ('Stream Walks', 'Stream Walks'),
    ('Microtrolling', 'Microtrolling'),
    ('Boat', 'Boat'),
    ('Snorkle', 'Snorkle'),
    ('Roving', 'Roving'),
    ('Raft', 'Raft'),
    ('Deadpitch', 'Deadpitch'),
    ('Floats', 'Floats'),
    ('Electrofishing', 'Electrofishing'),
    ('Fishwheel', 'Fishwheel'),
    ('Weir', 'Weir'),
    ('Fence', 'Fence'),
    ('Fishway-tunnels', 'Fishway-tunnels'),
    ('Sonar', 'Sonar'),
    ('Sonar-DIDSON', 'Sonar-DIDSON'),
    ('Video', 'Video'),
    ('Hydroacoustic', 'Hydroacoustic'),
    ('Resistivity', 'Resistivity'),
    ('River Surveyor', 'River Surveyor'),
    ('Coded Wire Tagging', 'Coded Wire Tagging'),
    ('Coded Wire Tag Recovery', 'Coded Wire Tag Recovery'),
    ('PIT Tagging', 'PIT Tagging'),
    ('Hallprint Tagging', 'Hallprint Tagging'),
    ('Spaghetti Tagging', 'Spaghetti Tagging'),
    ('Radio Tagging', 'Radio Tagging'),
    ('Mark-Recapture-other', 'Mark-Recapture-other'),
    ('Finclips', 'Finclips'),
    ('BioData-Physical Measurement', 'BioData-Physical Measurement'),
    ('BioData-Tissue Collection', 'BioData-Tissue Collection'),
    ('BioData-Visual Observation', 'BioData-Visual Observation'),
    ('BioData-Unspecified', 'BioData-Unspecified'),
    ('Fish Health Condition', 'Fish Health Condition'),
    ('Plane', 'Plane'),
    ('Helicopter', 'Helicopter'),
    ('Drone', 'Drone'),
    ('Flight-Unspecified', 'Flight-Unspecified'),
    ('Creel', 'Creel'),
    ('Plankton Sampling', 'Plankton Sampling'),
    ('Riparian Monitoring', 'Riparian Monitoring'),
    ('Habitat Monitoring-General', 'Habitat Monitoring-General'),
    ('Habitat Monitoring-Spawning', 'Habitat Monitoring-Spawning'),
    ('Smolt Trapping', 'Smolt Trapping'),
    ('Seine Trapping', 'Seine Trapping'),
    ('Gill Net Trapping', 'Gill Net Trapping'),
    ('Brood Collection', 'Brood Collection'),
    ('Egg Collection', 'Egg Collection'),
    ('Fish Culture', 'Fish Culture'),
    ('Pond Fry', 'Pond Fry'),
    ('Fry Release', 'Fry Release'),
    ('Spawn Brood', 'Spawn Brood'),
    ('Gamete Incubation', 'Gamete Incubation'),
    ('Temperature Logging', 'Temperature Logging'),
    ('Oxygen Monitoring', 'Oxygen Monitoring'),
    ('Physical Analysis', 'Physical Analysis'),
    ('Water Sampling-Chemical', 'Water Sampling-Chemical'),
    ('Water Sampling-Biological', 'Water Sampling-Biological'),
    ('Invasive Species Survey', 'Invasive Species Survey'),
    ('Vegetation Survey', 'Vegetation Survey'),
    ('Photo Point', 'Photo Point'),
    ('Habitat Modifications', 'Habitat Modifications'),
    ('Data Management', 'Data Management'),
    ('Traditional Ecological Knowledge', 'Traditional Ecological Knowledge'),
    ('Other', 'Other'),

)

SAMPLE_PROCESSING = (
    ('Scales', 'Scales'),
    ('Otoliths', 'Otoliths'),
    ('DNA', 'DNA'),
    ('eDNA', 'eDNA'),
    ('Heads', 'Heads'),
    ('Instrument Data Processing', 'Instrument Data Processing'),
    ('Unknown', 'Unknown'),
    ('Other', 'Other'),
    ('Not applicable', 'Not applicable'),
)

DATA_ENTRY = (
    ('Direct entry into computer', 'Direct entry into computer'),
    ('Direct entry into database', 'Direct entry into database'),
    ('Direct entry into database', 'Paper, Followed by Entry into Computer'),
    ('Unknown', 'Unknown'),
    ('Not applicable', 'Not applicable'),
    ('Other', 'Other'),
)

METHOD_DOCUMENT = (
    ('Program Document', 'Program Document'),
    ('Administration Document', 'Administration Document'),
    ('Conference - Conference paper/abstract', 'Conference - Conference paper/abstract'),
    ('Book', 'Book'),
    ('CSAS Document', 'CSAS Document'),
    ('Contract', 'Contract'),
    ('Statement of Work', 'Statement of Work '),
    ('Training Document', 'Training Document'),
    ('Protocol', 'Protocol'),
    ('Field Notes', 'Field Notes'),
    ('Journal Article', 'Journal Article'),
    ('Guidance Document', 'Guidance Document'),
    ('Unknown', 'Unknown'),
    ('Not applicable', 'Not applicable'),
    ('Other', 'Other'),
)


DATABASE = (
    ('ADF&G Zander ', 'ADF&G Zander '),
    ('PSMFC CWT', 'PSMFC CWT'),
    ('ADF&G Rergion 1', 'ADF&G Rergion 1'),
    ('ADF&G CWT Online Release', 'ADF&G CWT Online Release'),
    ('ADF&G SF Research and Technical Services', 'ADF&G SF Research and Technical Services'),
    ('NuSEDs', 'NuSEDs'),
    ('iREC', 'iREC'),
    ('KREST', 'KREST'),
    ('First Nations databases', 'First Nations databases'),
    ('Shared DFO drives', 'Shared DFO drives'),
    ('First Nations Harvest (AHMS)', 'First Nations Harvest (AHMS)'),
    ('Fishery Operations System (FOS)', 'Fishery Operations System (FOS)'),
    ('Mark Recovery Program (MRPRO)', 'Mark Recovery Program (MRPRO)'),
    ('Clockwork', 'Clockwork'),
    ('Biodatabase (South Coast DFO)', 'Biodatabase (South Coast DFO)'),
    ('PADS', 'PADS'),
    ('Otomanager', 'Otomanager'),
    ('Pacific Salmon Commission', 'Pacific Salmon Commission'),
    ('Genetics Group (PBS)', 'Genetics Group (PBS)'),
    ('Individual computer', 'Individual computer'),
    ('Pacific States Marine Fisheries Commission (www.rmpc.org)',
     'Pacific States Marine Fisheries Commission (www.rmpc.org)'),
    ('Central Coast FSC Catch', 'Central Coast FSC Catch'),
    ('Private', 'Private'),
    ('PIT Tag Information System (PTAGIS)', 'PIT Tag Information System (PTAGIS)'),
    ('Not Applicable', 'Not Applicable'),
    ('Other', 'Other'),
    ('CREST', 'CREST'),
    ('EPADS', 'EPADS'),
)

SAMPLE_BARRIER = (
    ('Weather', 'Weather'),
    ('Site Access', 'Site Access'),
    ('Equipment Failure', 'Equipment Failure'),
    ('Equipment Not Available', 'Equipment Not Available'),
    ('Staffing Unavailable', 'Staffing Unavailable'),
    ('Staffing Not Trained', 'Staffing Not Trained'),
    ('Unknown', 'Unknown'),
    ('Not Applicable', 'Not Applicable'),
    ('Other', 'Other'),
)

DATA_BARRIER = (
    ('No Person Available', 'No Person Available'),
    ('Sample Data Requires More Work Before it can be Entered into Database', 'Sample Data Requires More Work Before it can be Entered into Database'),
    ('Person Available but Lack of Training', 'Person Available but Lack of Training'),
    ('Equipment is Available but not Working', 'Equipment is Available but not Working'),
    ('Equipment is not Available', 'Equipment is not Available'),
    ('IT Issues', 'IT Issues'),
    ('Network Connection Issues', 'Network Connection Issues'),
    ('UNKNOWN', 'Unknown'),
    ('Not Applicable', 'Not Applicable'),
    ('Other', 'Other'),
)

SAMPLE_FORMAT = (
    ('Excel', 'Excel'),
    ('Paper', 'Paper'),
    ('Log Books', 'Log Books'),
    ('Word', 'Word'),
    ('SIL-hardcopy', 'SIL-hardcopy'),
    ('SIL-digitized', 'SIL-digitized'),
    ('Instrument Program', 'Instrument Program'),
    ('Direct Entry into Computer', 'Direct Entry into Computer'),
    ('SENS', 'SENS'),
    ('Not Applicable', 'Not Applicable'),
    ('Other', 'Other'),
)

DATA_PRODUCTS = (
    ('Relative Abundance', 'Relative Abundance'),
    ('Escapement Estimate - expanded/final', 'Escapement Estimate - expanded/final'),
    ('Escapement Estimate -unexpanded/preliminary', 'Escapement Estimate -unexpanded/preliminary'),
    ('Habitat data', 'Habitat data'),
    ('Harvest rate', 'Harvest rate'),
    ('Stock Recruitment', 'Stock Recruitment'),
    ('Survival Rate ', 'Survival Rate '),
    ('Marked status', 'Marked status'),
    ('Proportion of sampled fish effort/time', 'Proportion of sampled fish effort/time'),
    ('Proportion of in-river salmon destined for spawning', 'Proportion of in-river salmon destined for spawning'),
    ('Sex Composition', 'Sex Composition'),
    ('Age Composition Data', 'Age Composition Data'),
    ('Stock composition (GSI / DNA)Data', 'Stock composition (GSI / DNA)Data'),
    ('Condition of Fish - (DNA based)', 'Condition of Fish - (DNA based)'),
    ('Ratio of catchability', 'Ratio of catchability'),
    ('ESSR Targets', 'ESSR Targets'),
    ('Production', 'Production'),
    ('Biomass Data', 'Biomass Data'),
    ('Spawning Success', 'Spawning Success'),
    ('Fish Passage Data', 'Fish Passage Data'),
    ('Predation rates', 'Predation rates'),
    ('Other', 'Other'),
)

DATA_COMMUNICATION = (
    ('Presentations', 'Presentations'),
    ('Workshops', 'Workshops'),
    ('Reports', 'Reports'),
    ('Data Summaries', 'Data Summaries'),
    ('Bulletins', 'Bulletins'),
    ('Unknown', 'Unknown'),
    ('Not Applicable', 'Not Applicable'),
    ('Other', 'Other'),
)

REPORT_TIMELINE = (
    ('Progress Report', 'Progress Report'),
    ('Final Report', 'Final Report'),
    ('Not Applicable', 'Not Applicable'),
    ('Other', 'Other'),
)

REPORT_TYPE = (
    ('Annual Funding Report', 'Annual Funding Report'),
    ('Final Funding Report', 'Final Funding Report'),
    ('Stream Summary', 'Stream Summary'),
    ('Website', 'Website'),
    ('Community Report', 'Community Report'),
    ('Bulletin', 'Bulletin'),
    ('Project Report-General', 'Project Report-General'),
    ('Other Publication', 'Other Publication'),
    ('Administration Report', 'Administration Report'),
    ('Method Report', 'Method Report'),
    ('CSAS Report', 'CSAS Report'),
    ('Committee Report', 'Committee Report'),
    ('PSC Report', 'PSC Report'),
    ('Area Annual Report', 'Area Annual Report'),
    ('Schedule 7', 'Schedule 7'),
    ('Schedule E', 'Schedule E'),
    ('Unknown', 'Unknown'),

)

KEY_ELEMENT = (
    ('A', 'A'),
    ('B', 'B'),
    ('C', 'B'),
    ('D', 'D'),
    ('OTHER', 'Other'),
)

ACTIVITY_NUMBER = (
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
    ('6', '6'),
    ('7', '7'),
    ('8', '8'),
    ('9', '9'),
    ('10', '10'),
    ('11', '11'),
    ('12', '12'),
    ('13', '13'),
    ('14', '14'),
    ('15', '15'),
    ('16', '16'),
    ('17', '17'),
    ('18', '18'),
    ('19', '19'),
    ('20', '20'),
    ('OTHER', 'Other'),
)

SAMPLE_TYPE_OUTCOMES = (
   ('Adipose clips', 'Adipose clips'),
   ('Administration', 'Administration'),
   ('Auxillary Appendage Clips', 'Auxillary Appendage Clips'),
   ('Biodata-Unspecified', 'Biodata-Unspecified'),
   ('Water Samples-Biotoxin', 'Water Samples-Biotoxin'),
   ('Brood Collection', 'Brood Collection'),
   ('Catch Count', 'Catch Count'),
   ('Catch Effort', 'Catch Effort'),
   ('Counts', 'Counts'),
   ('Coded Wire Tag Recovery', 'Coded Wire Tag Recovery'),
   ('Coded Wire Tagging', 'Coded Wire Tagging'),
   ('Egg Collection', 'Egg Collection'),
   ('Enhancement-Unspecified', 'Enhancement-Unspecified'),
   ('Fin Clips', 'Fin Clips'),
   ('Fish Health Condition', 'Fish Health Condition'),
   ('Length', 'Length'),
   ('Mark/Tagging-Unspecified', 'Mark/Tagging-Unspecified'),
   ('Not Specified', 'Not Specified'),
   ('Otoliths', 'Otoliths'),
   ('PIT Tagging', 'PIT Tagging'),
   ('Scales', 'Scales'),
   ('Sea Lice Count', 'Sea Lice Count'),
   ('Secondary Marks', 'Secondary Marks'),
   ('Sex', 'Sex'),
   ('Spaghetti Tagging', 'Spaghetti Tagging'),
   ('Species Identification', 'Species Identification'),
   ('Tag Recovery-Unspecified', 'Tag Recovery-Unspecified'),
   ('Tissue Collection-Unspecified', 'Tissue Collection-Unspecified'),
   ('Tissue Collection-DNA', 'Tissue Collection-DNA'),
   ('Unknown', 'Unknown'),
   ('Weight', 'Weight'),
   ('Predation', 'Predation'),
   ('Dissolved Oxygen', 'Dissolved Oxygen'),
   ('Water Samples-eDNA', 'Water Samples-eDNA'),
   ('Water Samples-Unspecified', 'Water Samples-Unspecified'),
   ('Forestry Data-Unspecified', 'Forestry Data-Unspecified'),
   ('Habitat Condition-General', 'Habitat Condition-General'),
   ('Habitat Use', 'Habitat Use'),
   ('Hydrology-Discharge/Flow', 'Hydrology-Discharge/Flow'),
   ('Water Samples-Toxicology', 'Water Samples-Toxicology'),
   ('Water Temperature', 'Water Temperature'),
   ('Land Use Planning', 'Land Use Planning'),
   ('Restoration Activities', 'Restoration Activities'),
   ('Water Samples-Microscopic Examination', 'Water Samples-Microscopic Examination'),
   ('Incubation Data', 'Incubation Data'),
   ('Enhancement Targets', 'Enhancement Targets'),
   ('Egg Characteristics', 'Egg Characteristics'),
   ('Other', 'Other'),
)

REPORT_OUTCOMES = (
    ('Submitted samples', 'Submitted samples'),
    ('Summarized data', 'Summarized data'),
    ('Raw Data', 'Raw Data'),
    ('Stream Inspection Log', 'Stream Inspection Log'),
    ('Analyzed data - non-expanded estimates', 'Analyzed data - non-expanded estimates'),
    ('Analyzed data - expanded estimates', 'Analyzed data - expanded estimates'),
    ('Analyzed data - other', 'Analyzed data - other'),
    ('Annual Stream Report', 'Annual Stream Report'),
    ('Report document', 'Report document'),
    ('Summary of Activities', 'Summary of Activities'),
    ('Meeting Summary', 'Meeting Summary'),
    ('Live Collection', 'Live Collection'),
    ('Other', 'Other'),
    ('Events/Clinics/Workshops held', 'Events/Clinics/Workshops held'),
    ('School events', 'School events'),
    ('New Staff Trained', 'New Staff Trained'),
    ('Staff Maintained', 'Staff Maintained'),
    ('Biological activities performed', 'Biological activities performed'),
    ('Habitat activities performed', 'Habitat activities performed'),
    ('Infrastructure activities performed', 'Infrastructure activities performed'),
    ('General Outcome Metric', 'General Outcome Metric'),
    ('Habitat Restored', 'Habitat Restored'),
    ('Instream Habitat Treated', 'Instream Habitat Treated'),
    ('Metres Surveyed', 'Metres Surveyed'),
    ('Monitoring Effort', 'Monitoring Effort'),
    ('Metric on staff maintained', 'Metric on staff maintained'),
    ('Metric on stream activities that were complete', 'Metric on stream activities that were complete'),
    ('Metric on techincal capactity improved', 'Metric on techincal capactity improved'),
    ('Year End Narrative Report', 'Year End Narrative Report'),
    ('Metric on volunteer activities', 'Metric on volunteer activities'),
)

CAPACITY = (
    ('NEW TRAINING', 'New Training'),
    ('NEW STAFF INTEREST', 'New staff interest'),
    ('VOLUNTEERS SHOWED INTEREST', 'Volunteers showed interest'),
    ('COMMUNITY CONNECTIONS MADE', 'Community connections made'),
    ('PUBLIC ENGAGEMENT', 'Public engagement'),
    ('PREVIOUS STAFF TRAINING UPGRADED', 'Previous Staff Training upgraded'),
    ('EQUIPMENT RESOURCES IMPROVED', 'Equipment resources improved'),
    ('IMPROVED FISHERIES KNOWLEDGE AMONG COMMUNITY', 'Improved fisheries knowledge among community'),
    ('IMPROVED COMMUNICATION BETWEEN DFO AND FUNDING RECIPIENT', 'Improved communication between DFO and funding recipient'),
)

DATA_QUALITY = (
    ('Level 1 (Very High Quality)', 'Level 1 (Very High Quality)'),
    ('LEVEL 2 (High Quality)', 'LEVEL 2 (High Quality)'),
    ('Level 3 (Good Quality)', 'Level 3 (Good Quality)'),
    ('Level 4 (Moderate Quality)', 'Level 4 (Moderate Quality)'),
    ('Level 5 (Low Quality)', 'Level 5 (Low Quality)'),
    ('Unknown', 'Unknown'),
    ('Not Applicable', 'Not Applicable'),
)

OUTCOME_BARRIER = (
    ('Site Access', 'Site Access'),
    ('Equipment Failure', 'Equipment Failure'),
    ('Equipment not Available', 'Equipment not Available'),
    ('Staffing Unavailable', 'Staffing Unavailable'),
    ('Staffing not Trained', 'Staffing not Trained'),
    ('Weather', 'Weather'),
)

SUBJECT = (
    ('People', 'People'),
    ('Projects', 'Projects'),
    ('Objectives', 'Objectives'),
    ('Methods', 'Methods'),
    ('Data', 'Data'),
    ('Organizations', 'Organizations'),
    ('Other', 'Other'),
)

FN_COMMUNICATIONS = (
    ('Presentations', 'Presentations'),
    ('Workshops', 'Workshops'),
    ('Reports', 'Reports'),
    ('Data Summaries', 'Data Summaries'),
    ('Bulletins', 'Bulletins'),
    ('Other', 'Other'),
    ('Not Applicable', 'Not Applicable'),
)

ELEMENT_TITLE = (
    ('Aquatic Resource Management and Stewardship', 'Aquatic Resource Management and Stewardship'),
    ('Food, Social and Ceremonial (FSC) Fisheries Manangement', 'Food, Social and Ceremonial (FSC) Fisheries Manangement'),
    ('Economic Opportunities', 'Economic Opportunities'),
    ('Aquatic Resource Management Compliance and Accountability', 'Aquatic Resource Management Compliance and Accountability'),
    ('Annual Work Plan', 'Annual Work Plan'),
    ('Unknown', 'Unknown'),
    ('Not Applicable', 'Not Applicable'),

)

FUNDING_YEARS = (
    ('2017', '2017'),
    ('2018', '2018'),
    ('2019', '2019'),
    ('2020', '2020'),
    ('2021', '2021'),
    ('2022', '2022'),
    ('2023', '2023'),
    ('2024', '2024'),
    ('2025', '2025'),
    ('2026', '2026'),
    ('2027', '2027'),
    ('2028', '2028'),
    ('2029', '2029'),
    ('2030', '2030'),
    ('2031', '2031'),
    ('2032', '2032'),
    ('2033', '2033'),
    ('2034', '2034'),
    ('2035', '2035'),
    ('2036', '2036'),
    ('2037', '2037'),
    ('2038', '2038'),
    ('2039', '2039'),
    ('2040', '2040'),
    ('2041', '2041'),
    ('2042', '2042'),
    ('2043', '2043'),
    ('2044', '2044'),
    ('2045', '2045'),
    ('2046', '2046'),
    ('2047', '2047'),
    ('2048', '2048'),
    ('2049', '2049'),
    ('2050', '2050'),
)

POLICY_PROGRAM = (
    ('Strategic Species At Risk Act (SARA) Recovery Plans', 'Strategic Species At Risk Act (SARA) Recovery Plans'),
    ('COSEWIC Assessed Populations', 'COSEWIC Assessed Populations'),
    ('WSP Implementation', 'WSP Implementation'),
    ('Fisheries Act Rebuilding Plans', 'Fisheries Act Rebuilding Plans'),
    ('Southern BC Chinook Initiative', 'Southern BC Chinook Initiative'),
    ('Pacific Salmon Treaty', 'Pacific Salmon Treaty'),
    ('Pacific Salmon Strategy Initiative', 'Pacific Salmon Strategy Initiative'),
    ('Unknown', 'Unknown'),
    ('Not Applicable', 'Not Applicable'),
    ('Other', 'Other'),
)
