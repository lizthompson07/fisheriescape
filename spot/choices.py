
AGREEMENT_DATABASE = (
    ('APGIS', "APGIS - Aboriginal Programs and Governance Information System"),
    ('UNKNOWN', "Unknown"),
    ('NOT APPLICABLE', "Not Applicable"),
    ('OTHER', "Other"),
)


FUNDING_SOURCES = (
    ('AFS', 'AFS – Aboriginal Fisheries Strategy'),
    ('AAROM', 'AAROM – Aboriginal Aquatic Resources and Oceans Management'),
    ('PST (TBG&C)',  'PST (TBG&C) – Pacific Salmon Treaty/Treasury Board Grants & Contributions'),
    ('SCIENCE',  'Science – Program funding redirected to a G&C agreement'),
    ('HSP', 'HSP – Habitat Stewardship Program'),
    ('BCSRIF', 'BCSRIF – British Columbia Salmon Restoration and Innovation Fund'),
    ('CNFASAR', 'CNFASAR – Canadian Nature Fund for Aquatic Species at Risk'),
    ('CRF', 'CRF – Coastal Restoration Fund'),
    ('FHRI', 'FHRI – Fisheries Habitat Restoration Initiative'),
    ('IHPP', 'IHPP – Indigenous Habitat Participation Program'),
    ('RFCPP', 'RFCPP – Recreational Fisheries Conservation Partnership Program'),
    ('PSSI', 'PSSI - Pacific Salmon Strategy Initiative'),
    ('AFSAR', 'AFSAR - Aboriginal Fund for Species at Risk'),
    ('SEP', 'SEP - Salmon Enhancement Program'),
    ('AHRF', 'AHRF - Aquatic Habitat Restoration Fund'),
    ('SSI', 'SSI- Salish Sea Initiative'),
    ('OTHER', 'Other – Add Name and Definition'),
    ('UNKNOWN', 'Unknown'),
)

AGREEMENT_TYPE = (
    ('FORMAL AGREEMENT', 'Formal Agreement'),
    ('AMENDMENT', 'Amendment'),
    ('FIRST NATIONS TREATY AGREEMENT', 'First Nations Treaty Agreement'),
    ('SUPPLY ARRANGEMENT', 'Supply Arrangement'),
    ('CONTRRACT', 'Contract'),
    ('UNKNOWN', 'Unknown'),
    ('NOT APPLICABLE', 'Not applicable'),
    ('OTHER', 'Other'),
)

LEAD_ORGANIZATION = (
    ('FIRST NATIONS', 'First Nations'),
    ('DFO', 'DFO'),
    ('COLLABORATIVE', 'Collaborative'),
    ('UNKNOWN', 'Unknown'),
    ('NOT APPLICABLE', 'Not applicable'),
    ('OTHER', 'Other')
)

REGION = (
    ('YUKON/TRANSBOUNDARY', 'Yukon/Transboundary'),
    ('NORTH COAST', 'North Coast'),
    ('SOUTH COAST', 'South Coast'),
    ('FRASER', 'Fraser'),
)

ECOSYSTEM_TYPE = (
    ('FRESHWATER', 'Freshwater'),
    ('ESTUARINE', 'Estuarine'),
    ('MARINE', 'Marine'),
    ('UNKNOWN', 'Unknown'),
    ('NOT APPLICABLE', 'Not applicable'),
    ('OTHER', 'Other'),
)

SMU_NAME = (
    ('BARKLEY/SOMASS SOCKEYE SALMON', 'Barkley/Somass Sockeye Salmon'),
    ('CHUM GENERAL', 'Chum general'),
    ('ECVI/MAINLAND INLET PINK SALMON', 'ECVI/Mainland Inlet Pink Salmon'),
    ('ECVI/MAINLAND INLET SOCKEYE SALMON', 'ECVI/Mainland Inlet Sockeye Salmon'),
    ('INNER SOUTH COAST CHUM SALMON', 'Inner South Coast Chum Salmon'),
    ('JST/MAINLAND INLET CHINOOK SALMON', 'JST/Mainland Inlet Chinook Salmon'),
    ('JST/MAINLAND INLETS COHO SALMON', 'JST/Mainland Inlets Coho Salmon'),
    ('LOWER STRAIT OF GEORGIA CHINOOK SALMON', 'Lower Strait of Georgia Chinook Salmon'),
    ('SOUTH COAST SOCKEYE GENERAL', 'South Coast Sockeye General'),
    ('STRAIT OF GEORGIA COHO SALMON', 'Strait of Georgia Coho Salmon'),
    ('UPPER STRAIT OF GEORGIA CHINOOK SALMON', 'Upper Strait of Georgia Chinook Salmon'),
    ('WCVI Chinook Salmon', 'WCVI Chinook Salmon'),
    ('WCVI CHUM SALMON', 'WCVI Chum Salmon'),
    ('WCVI COHO SALMON', 'WCVI Coho Salmon'),
    ('UNKNOWN', 'Unknown'),
    ('NOT APPLICABLE', 'Not applicable'),
    ('OTHER', 'Other'),
)

SPECIES = (
    ('CHINOOK', 'Chinook Salmon (Oncorhynchus tshawytscha)'),
    ('CHUM', 'Chum Salmon (Oncorhynchus keta)'),
    ('COHO', 'Coho Salmon (Oncorhynchus kisutch)'),
    ('PINK',  'Pink Salmon (Oncorhynchus gorbuscha)'),
    ('SOCKEYE',  'Sockeye Salmon (Oncorhynchus nerka)'),
    ('STEELHEAD', 'Steelhead (Oncorhynchus mykiss)'),
    ('UNKNOWN', 'Unknown'),
    ('NOT APPLICABLE', 'Not applicable'),
    ('OTHER', 'Other'),
)

SALMON_LIFE_CYCLE = (
    ('ADULT', 'Adult – adult salmon residing in the ocean; or are migrating in the river.'),
    ('JUVENILE', 'Juvenile – Fish in the fry, parr & smolt stage of life.'),
    ('SPAWNING', 'Spawning – a phase of the salmonid life cycle where male and female fish are in the spawning grounds, are mature and able to spawn.'),
    ('INCUBATION', 'Incubation – Inter-gravel development phase including the egg and alevin life cycle stages.'),
    ('UNKNOWN', 'Unknown'),
    ('NOT APPLICABLE', 'Not applicable'),
    ('OTHER', 'Other'),
)

PROJECT_STAGE = (
    ('PROPOSED', 'proposed'),
    ('DEVELOPING', 'Developing'),
    ('PILOT', 'Pilot'),
    ('ACTIVE', 'Active'),
    ('COMPLETED', 'Completed'),
    ('TERMINATED', 'Terminated'),
    ('UNKNOWN', 'Unknown'),
    ('NOT APPLICABLE', 'Not applicable'),
    ('OTHER', 'Other'),
)

PROJECT_TYPE = (
    ('POPULATION SCIENCE', 'Population Science'),
    ('HABITAT SCIENCE', 'Habitat Science'),
)

PROJECT_SUB_TYPE = (
    ('RESEARCH & DEVELOPMENT', 'Research & Development'),
    ('COMMUNITY', 'Community'),
    ('MONITORING', 'Monitoring'),
    ('SAMPLING', 'Sampling'),
    ('RECOVERY', 'Recovery'),
    ('RESTORATION', 'Restoration'),
    ('DESIGN & FEASIBILITY', 'Design & Feasibility'),
    ('DECOMMISSIONING', 'Decommissioning'),
    ('IMPLEMENTATION', 'Implementation'),
    ('MAINTENANCE', 'Maintenance'),
    ('STEWARDSHIP', 'Stewardship'),
    ('RESEARCH & MONITORING', 'Research & Monitoring'),
    ('UNKNOWN', 'Unknown'),
    ('NOT APPLICABLE', 'Not applicable'),
)

MONITORING_APPROACH = (
    ('INDICATOR', 'Indicator'),
    ('INTENSIVE', 'Intensive'),
    ('EXTENSIVE', 'Extensive'),
    ('UNKNOWN', 'Unknown'),
    ('NOT APPLICABLE', 'Not applicable'),
)

PROJECT_THEME = (
    ('ESCAPEMENT', 'Escapement'),
    ('CONSERVATION', 'Conservation'),
    ('CATCH (FIRST NATIONS)', 'Catch (First Nations)'),
    ('CATCH (RECREATIONAL)', 'Catch (Recreational)'),
    ('CATCH (COMMERCIAL)', 'Catch (Commercial)'),
    ('ENHANCEMENT', 'Enhancement'),
    ('ADMINISTRATION', 'Administration'),
    ('HABITAT', 'Habitat'),
    ('UNKNOWN', 'Unknown'),
    ('NOT APPLICABLE', 'Not applicable'),
)

PROJECT_CORE_ELEMENT = (
    ('PLANNING', 'Planning'),
    ('FIELD WORK', 'Field Work'),
    ('SAMPLE PROCESSING', 'Sample Processing'),
    ('DATA ENTRY', 'Data Entry'),
    ('DATA ANALYSIS', 'Data Analysis'),
    ('REPORTING', 'Reporting'),
)

SUPPORTIVE_COMPONENT = (
    ('WORKSHOP', 'Workshop'),
    ('DATA COLLECTION', 'Data Collection'),
    ('EVALUATION', 'Evaluation'),
    ('ASSESSMENT', 'Assessment'),
    ('COMMITTEE', 'Committee'),
    ('ADMINISTRATION', 'Administration'),
    ('TRAINING', 'Training'),
    ('STAFFING', 'Staffing'),
    ('MEETING', 'Meeting'),
    ('COMPUTER SUPPORT', 'Computer Support'),
    ('ADVICE & CONSULTATION', 'Advice & Consultation'),
    ('STUDY DESIGN', 'Study Design'),
    ('LITERATURE REVIEW', 'Literature Review'),
    ('EQUIPMENT SUPPORT', 'Equipment Support'),
    ('EQUIPMENT REPAIR/BUILDING', 'Equipment Repair/Building'),
    ('ANALYSIS OF CURRENT DATA', 'Analysis of Current Data'),
    ('ANALYSIS OF HISTORICAL DATA', 'Analysis of Historical Data'),
    ('Analysis - Other', 'Analysis - Other'),
    ('UNKNOWN', 'Unknown'),
    ('NOT APPLICABLE', 'Not applicable'),
)

PROJECT_PURPOSE = (
    ('Biological',
    (('POPULATION ESTIMATES', 'Population Estimates'),
    ('RUN RECONSTRUCTION', 'Run Reconstruction'),
    ('BIOLOGICAL ABUNDANCE BENCHMARKS', 'Biological Abundance Benchmarks'),
    ('TERMINAL ABUNDANCE', 'Terminal Abundance'),
    ('IN-RIVER ABUNDANCE', 'In-River Abundance'),
    ('CATCH ESTIMATES', 'Catch Estimates'),
    ('SMOLT ABUNDANCE', 'Smolt Abundance'),
    ('ADULT ABUNDANCE', 'Adult Abundance'),
    ('ADMINISTRATION', 'Administration'),
    ('RECOVERY', 'Recovery'),
    ('REBUILDING', 'Rebuilding'),
    ('ENHANCEMENT', 'Enhancement'))),

    ('Catch/Fisheries',
    (('FOODS, SOCIAL AND CEREMONIAL FISHERIES', 'Foods, Social and Ceremonial Fisheries'),
    ('FRASER RECREATIONAL', 'Fraser Recreational'),
    ('FRASER ECONOMIC OPPORTUNITY (EO)', 'Fraser Economic Opportunity (EO)'),
    ('FRASER COMMERCIAL (IN-RIVER PORTIONS OF AREA', 'Fraser Commercial (in-river portions of Area'),
    ('29E (GILLNET) AND AREA 29B (SEINE)', '29E (Gillnet) and Area 29B (Seine)'),
    ('FRASER TEST FISHERIES (ALBION, QUALARK)', 'Fraser Test Fisheries (Albion, Qualark)'),
    ('MARINE FISHERIES', 'Marine Fisheries'),
    ('JUAN DE FUCA RECREATIONAL', 'Juan de Fuca Recreational'),
    ('WEST COAST VANCOUVER ISLAND RECREATIONAL', 'West Coast Vancouver Island Recreational'),
    ('NORTHERN BRITISH COLUMBIA RECREATIONAL', 'Northern British Columbia Recreational'),
    ('WEST COAST VANCOUVER ISLAND COMMERCIAL', 'West Coast Vancouver Island Commercial'),
    ('TROLL', 'Troll'),
    ('NORTHERN BC COMMERCIAL TROLL', 'Northern BC Commercial Troll'),
    ('TAAQ-WIIHAK', 'Taaq-wiihak'),
    ('FISH PASSAGE', 'Fish Passage'))),

    ('Habitat',
    (('WATER LEVELS', 'Water Levels'),
    ('RIPARIAN', 'Riparian'),
    ('ESTUARINE', 'Estuarine'),
    ('NEARSHORE & MARINE', 'Nearshore & Marine'),
    ('INSTREAM STRUCTURE', 'Instream Structure'),
    ('FLOODPLAIN CONNECTIVITY', 'Floodplain connectivity'),
    ('WATERSHED', 'Watershed'),
    ('NUTRIENT SUPPLEMENTATION', 'Nutrient Supplementation'),
    ('HABITAT CONDITION', 'Habitat Condition'),
    ('UNKNOWN', 'Unknown'),
    ('NOT APPLICABLE', 'Not applicable'),
    ('OTHER', 'Other'))),
)

DFO_LINK = (
    ('FISHERIES MANAGEMENT', 'Fisheries Management'),
    ('COMMERCIAL FISHERIES', 'Commercial Fisheries'),
    ('RECREATIONAL FISHERIES', 'Recreational Fisheries'),
    ('ABORIGINAL PROG. & TREAT', 'Aboriginal Prog. & Treat'),
    ('AQUACULTURE MANAGEMENT', 'Aquaculture Management'),
    ('SALMONID ENHANCEMENT', 'Salmonid Enhancement'),
    ('INTERNATIONAL ENGAGEMENT', 'International Engagement'),
    ('SMALL CRAFT HARBOURS', 'Small Craft Harbours'),
    ('CONSERVATION & PROTECTION', 'Conservation & Protection'),
    ('AIR SURVEILLANCE', 'Air Surveillance'),
    ('AQUATIC ANIMAL HEALTH', 'Aquatic Animal Health'),
    ('BIOTECHNOLOGY & GENOMICS', 'Biotechnology & Genomics'),
    ('AQUACULTURE SCIENCE', 'Aquaculture Science'),
    ('FISHERIES SCIENCE', 'Fisheries Science'),
    ('FISH AND SEAFOOD SECTOR', 'Fish and Seafood Sector'),
    ('FISH & FISH HABITAT PROT.', 'Fish & Fish Habitat Prot.'),
    ('AQUATIC INVASIVE SPECIES', 'Aquatic Invasive Species'),
    ('SPECIES AT RISK', 'Species at Risk'),
    ('MARINE PLANNING & CONSER.', 'Marine Planning & Conser.'),
    ('AQUATIC ECOSYSTEM SCIENCE', 'Aquatic Ecosystem Science'),
    ('OCEANS & CLIM. CHNG. SCI.', 'Oceans & Clim. Chng. Sci.'),
    ('WATERWAYS MANAGEMENT', 'Waterways Management'),
    ('ENVIRONMENTAL RESPONSE', 'Environmental Response'),
    ('UNKNOWN', 'Unknown'),
    ('NOT APPLICABLE', 'Not applicable'),
)

GOVERNMENT_LINK = (
    ('MUNICIPALITY', 'Municipality'),
    ('PROVINCE OF BRITISH COLUMBIA', 'Province of British Columbia'),
    ('YUKON TERRITORY', 'Yukon Territory'),
    ('ENVIRONMENT CANADA', 'Environment Canada'),
    ('CLIMATE CHANGE CANADA', 'Climate Change Canada'),
    ('ALASKA DEPARTMENT OF FISH & GAME', 'Alaska Department of Fish & Game'),
    ('WASHINGTON STATE', 'Washington State'),
    ('UNKNOWN', 'Unknown'),
    ('NOT APPLICABLE', 'Not applicable'),
    ('OTHER', 'Other'),
)

ROLE = (
    ('CHIEF', 'Chief'),
    ('BIOLOGIST', 'Biologist'),
    ('AQUATICS MANAGER', 'Aquatics Manager'),
    ('TECHNICIAN', 'Technician'),
    ('DIRECTOR', 'Director'),
    ('FISHERIES MANAGER', 'Fisheries Manager'),
    ('REFUGE MANAGER', 'Refuge Manager'),
    ('SCIENTIST', 'Scientist'),
    ('STEWARDSHIP DIRECTOR', 'Stewardship Director'),
    ('UNKNOWN', 'Unknown'),
    ('OTHER', 'Other'),
)

COUNTRY_CHOICES = (
    ('CANADA', 'Canada'),
    ('USA', 'USA'),
)

PROVINCE_STATE_CHOICES = (
    ('ALBERTA', 'Alberta'),
    ('BRITISH COLUMBIA', 'British Columbia'),
    ('MANITOBA', 'Manitoba'),
    ('NEW BRUNSWICK', 'New Brunswick'),
    ('NEWFOUNDLAND & LABRADOR', 'Newfoundland & Labrador'),
    ('NOVA SCOTIA', 'Nova Scotia'),
    ('ONTARIO', 'Ontario'),
    ('PRINCE EDWARD ISLAND', 'Prince Edward Island'),
    ('QUEBEC', 'Quebec'),
    ('SASKATCHEWAN', 'Saskatchewan'),
    ('NORTHWEST TERRITORIES', 'Northwest Territories'),
    ('NUNAVUT', 'Nunavut'),
    ('YUKON', 'Yukon'),
    ('WASHINGTON', 'Washington'),
    ('ALASKA', 'Alaska'),
)

ORGANIZATION_TYPE = (
    ('FIRST NATION', 'First Nations'),
    ('COMPANY', 'Company'),
    ('GOVERNMENT ORGANIZATION', 'Government Organization'),
)

PLANNING_METHOD = (
    ('FEASIBILITY STUDY', 'Feasibility Study'),
    ('PROJECT DESIGN', 'Project Design'),
    ('RESOURCE ALLOCATION', 'Resource Allocation'),
    ('OBJECTIVE-SETTING', 'Objective-setting'),
    ('OTHER', 'Other'),
)

FIELD_WORK = (
    ('Biological - Visual',
    (('STREAM WALKS', 'Stream walks'),
    ('BOAT SURVEY', 'Boat survey'),
    ('SNORKLE SURVEY', 'Snorkle survey'),
    ('RAFT', 'Raft'),
    ('DEADPITCH', 'Deadpitch'),
    ('MICROTROLLING', 'Microtrolling'),
    ('ROVING', 'Roving'),
    ('FISHWHEEL', 'Fishwheel'),
    ('ELECTROFISHING', 'Electrofishing'))),

    ('Biological - Intensive Measure',
    (('WEIR', 'Weir'),
    ('FENCE', 'Fence'),
    ('FISHWAY-TUNNELS', 'Fishway-tunnels'))),

    ('Biological - Instrumentation',
    (('SONAR', 'Sonar'),
    ('DIDSON', 'DIDSON'),
    ('VIDEO', 'Video'),
    ('HYDROACOUSTIC', 'Hydroacoustic'),
    ('RESISTIVITY', 'Resistivity'),
    ('RIVER SURVEYOR', 'River Surveyor'))),

    ('Biological - Tagging',
    (('PIT', 'Pit'),
    ('CODED WIRE TAG', 'Coded Wire Tag'),
    ('HALLPRINT', 'Hallprint'),
    ('SPAGHETTI', 'Spaghetti'),
    ('RADIO', 'Radio'))),

    ('Biological - Biodata',
    (('SIZE', 'Size'),
    ('SEX', 'Sex'),
    ('AGE', 'Age'),
    ('DNA (GENETIC STOCK ID)', 'DNA (Genetic Stock ID)'),
    ('OTOLITHS', 'Otoliths'),
    ('HEALTH CONDITION', 'Health Condition'))),

    ('Biological - Aerial',
    (('PLANE', 'Plane'),
    ('HELICOPTER', 'Helicopter'),
    ('DRONE', 'Drone'))),

    ('Biological - Catch',
    (('CREEL', 'Creel'),
    ('OTHER', 'Other'))),

    ('Biological - Trapping',
    (('SMOLT', 'Smolt'),
    ('SEINES', 'Seines'),
    ('GILL NETTING', 'Gill Netting'))),

    ('Biological - Enhancement',
    (('BROODSTOCK TAKE', 'Broodstock Take'),
    ('OTHER', 'Other'))),

    ('Field Work - Habitat',
    (('PHYSICAL ANALYSIS', 'Physical Analysis'),
    ('CHEMICAL ANALYSIS', 'Chemical Analysis'),
    ('PLANKTON', 'Plankton'),
    ('RIPARIAN', 'Riparian'),
    ('OTHER', 'Other'))),

    ('Habitat - Restoration',
    (('AERIAL SURVEYS', 'Aerial Surveys'),
    ('EDNA', 'eDNA'),
    ('ELECTOFISHING', 'Electofishing'),
    ('HYDROLOGICAL MODELLING', 'Hydrological modelling'),
    ('INVASIVE SPECIES SURVEYS', 'Invasive species surveys'),
    ('PHYSICAL HABITAT SURVEYS', 'Physical habitat surveys'),
    ('vEGETATION SURVEYS', 'Vegetation Surveys'),
    ('NETS AND TRAPS', 'Nets and Traps'),
    ('PHOTO POINT MONITORING', 'Photo Point Monitoring'),
    ('PIT TAGGING AND TELEMETRY', 'PIT Tagging and Telemetry'),
    ('SNORKLE SURVEYS', 'Snorkle Surveys'),
    ('TEMPERATURE LOGGERS', 'Temperature Loggers'),
    ('HYDROMETER INSTALLMENTS', 'Hydrometer Installments'),
    ('WATER SAMPLING', 'Water Sampling'),
    ('QUALITATIVE VISUAL ASSESSMENT', 'Qualitative visual assessment'),
    ('OTHER', 'Other'))),
)

SAMPLE_PROCESSING = (
    ('AGING', 'Aging'),
    ('DNA (GENETIC STOCK ID)', 'DNA (Genetic Stock ID)'),
    ('INSTRUMENT DATA PROCESSING', 'Instrument data processing'),
    ('SCALES', 'Scales'),
    ('OTOLITHS', 'Otoliths'),
    ('DNA', 'DNA'),
    ('HEADS', 'Heads'),
    ('OTHER', 'Other'),
)

DATA_ENTRY = (
    ('DIRECT ENTRY INTO COMPUTER', 'Direct entry into computer'),
    ('DIRECT ENTRY INTO DATABASE', 'Direct entry into database'),
    ('PAPER, FOLLOWED BY ENTRY INTO COMPUTER', 'Paper, followed by entry into computer'),
    ('UNKNOWN', 'Unknown'),
    ('NOT APPLICABLE', 'Not applicable'),
    ('OTHER', 'Other'),
)

METHOD_DOCUMENT = (
    ('PROGRAM DOCUMENT', 'Program Document'),
    ('ADMINISTRATION DOCUMENT', 'Administration Document'),
    ('CONFERENCE', 'Conference'),
    ('BOOK', 'Book'),
    ('CSAS', 'CSAS'),
    ('CONTRACT', 'Contract'),
    ('STATEMENT OF WORK', 'Statement of Work '),
    ('TRAINING DOCUMENT', 'Training Document'),
    ('PROTOCOL', 'Protocol'),
    ('FIELD NOTES', 'Field Notes'),
    ('JOURNAL ARTICLE', 'Journal Article'),
    ('GUIDANCE DOCUMENT', 'Guidance Document'),
)

SAMPLES_COLLECTED = (

    ('Biological',
    (('FISH COUNTS', 'Fish counts (fence, catch, static)'),
    ('ESCAPEMENT ESTIMATE', 'Escapement estimate (non-expanded)'),
    ('SPAWNING DENSITY', 'Spawning density'),
    ('BROODSTOCK REMOVAL', 'Broodstock removal'),
    ('FISH AT LOCATION', 'Fish at location (by segment or area)'),
    ('SPAWNING LOCATION', 'Spawning location'),
    ('MIGRATION TIMING', 'Migration timing'),
    ('LENGTH', 'Length'),
    ('CLIP STATUS', 'Clip status'),
    ('TAG STATUS', 'Tag status'),
    ('HEAD COLLECTION', 'Head collection'),
    ('SCALE SAMPLES ', 'Scale samples '),
    ('SMEAR SAMPLES', 'Smear samples'),
    ('OTOLITHS', 'Otoliths'),
    ('OTHER', 'Other'))),

    ('Habitat',
    (('DISSOLVED OXYGEN', 'Dissolved oxygen'),
    ('TEMPERATURE', 'Temperature'),
    ('SALINITY', 'Salinity'),
    ('WATER FLOW', 'Water flow'),
    ('TURBIDITY', 'Turbidity'),
    ('WEATHER CONDITIONS', 'Weather conditions'),
    ('ZOOPLANKTON', 'Zooplankton'),
    ('INVERTEBRATES', 'Invertebrates'),
    ('OTHER', 'Other'))),

    ('Restoration',
    (('AERIAL SURVEYS', 'Aerial surveys'),
    ('eDNA', 'eDNA'),
    ('ELECTROFISHING', 'Electrofishing'),
    ('HYDROLOGICAL MODELLING', 'Hydrological modelling'),
    ('INVASIVE SPECIES SURVEYS', 'Invasive species surveys'),
    ('PHYSICAL HABITAT SURVEYS', 'Physical habitat surveys'),
    ('VEGETATION SURVEYS', 'Vegetation surveys'),
    ('NETS AND TRAPS', 'Nets and traps'),
    ('PHOTO POINT MONITORING', 'Photo point monitoring'),
    ('PIT TAGGING AND TELEMETRY', 'PIT tagging and telemetry'),
    ('SNORKEL SURVEYS', 'Snorkel surveys'),
    ('TEMPERATURE LOGGERS', 'Temperature loggers'),
    ('HYDROMETER INSTALLMENTS', 'Hydrometer installments'),
    ('WATER SAMPLING', 'Water sampling'),
    ('QUALITATIVE VISUAL ASSESSMENT', 'Qualitative visual assessment'),
    ('OTHER', 'Other'))),
)

DATABASE = (
    ('ADF&G ZANDER', 'ADF&G Zander'),
    ('PSMFC CWT', 'PSMFC CWT'),
    ('ADF&G REGION 1', 'ADF&G Region 1'),
    ('ADF&G CWT ONLINE RELEASE', 'ADF&G CWT Online Release'),
    ('ADF&G SF RESEARCH AND TECHNICAL SERVICES', 'ADF&G SF Research and Technical Services'),
    ('NUSEDS', 'NuSEDs'),
    ('IREC', 'iREC'),
    ('KREST', 'KREST'),
    ('FIRST NATIONS DATABASES', 'First Nations Databases'),
    ('SHARED DFO DRIVES', 'Shared DFO drives'),
    ('FIRST NATIONS HARVEST (AHMS)', 'First Nations Harvest (AHMS)'),
    ('FISHERY OPERATIONS SYSTEM (FOS)', 'Fishery Operations System (FOS)'),
    ('MARK RECOVERY PROGRAM (MRPRO)', 'Mark Recovery Program (MRPRO)'),
    ('CLOCKWORK', 'Clockwork'),
    ('BIODATABASE (SOUTH COAST DFO)', 'Biodatabase (South Coast DFO)'),
    ('PADS', 'PADS'),
    ('OTOMANAGER', 'Otomanager'),
    ('PACIFIC SALMON COMMISSION', 'Pacific Salmon Commission'),
    ('GENETICS GROUP (PBS)', 'Genetics Group (PBS)'),
    ('INDIVIDUAL COMPUTER', 'Individual computer'),
    ('PACIFIC STATES MARINE FISHERIES COMMISSION (WWW.RMPC.ORG)', 'Pacific States Marine Fisheries Commission (www.rmpc.org)'),
    ('CENTRAL COAST FSC CATCH', 'Central Coast FSC Catch'),
    ('PRIVATE', 'Private'),
    ('PIT TAG INFORMATION SYSTEM (PTAGIS)', 'PIT Tag Information System (PTAGIS)'),
    ('NOT APPLICABLE', 'Not applicable'),
    ('OTHER', 'Other'),
)

SAMPLE_BARRIER = (
    ('WEATHER', 'Weather'),
    ('SITE ACCESS', 'Site Access'),
    ('EQUIPMENT FAILURE', 'Equipment failure'),
    ('EQUIPMENT NOT AVAILABLE', 'Equipment not available'),
    ('STAFFING UNAVAILABLE', 'Staffing unavailable'),
    ('STAFFING NOT TRAINED', 'Staffing not trained'),
    ('UNKNOWN', 'Unknown'),
    ('NOT APPLICABLE', 'Not applicable'),
    ('OTHER', 'Other'),
)

DATA_BARRIER = (
    ('NO PERSON AVAILABLE', 'No person available'),
    ('SAMPLE DATA REQUIRES MORE WORK BEFORE IT CAN BE ENTERED INTO DATABASE', 'Sample data requires more work before it can be entered into database'),
    ('PERSON AVAILABLE BUT LACK OF TRAINING', 'Person available but lack of training'),
    ('EQUIPMENT IS AVAILABLE BUT NOT WORKING', 'Equipment is available but not working'),
    ('EQUIPMENT IS NOT AVAILABLE', 'Equipment is not available'),
    ('IT ISSUES', 'IT issues'),
    ('NETWORK CONNECTION ISSUES', 'Network connection issues'),
    ('UNKNOWN', 'Unknown'),
    ('NOT APPLICABLE', 'Not applicable'),
    ('OTHER', 'Other'),
)

SAMPLE_FORMAT = (
    ('EXCEL', 'Excel'),
    ('PAPER', 'Paper'),
    ('LOG BOOKS', 'Log Books'),
    ('WORD', 'Word'),
    ('PDF FILES', 'PDF Files'),
    ('SIL-HARDCOPY', 'SIL-hardcopy'),
    ('SIL-DIGITIZED', 'SIL-digitized'),
    ('INSTRUMENT FILES', 'Instrument Files'),
    ('DATABASE FILED', 'Database Filed'),
    ('SENS', 'SENS'),
    ('WET NOTES', 'Wet Notes'),
    ('NOT APPLICABLE', 'Not applicable'),
    ('OTHER', 'Other'),
)

DATA_PRODUCTS = (
    ('RELATIVE ABUNDANCE', 'Relative Abundance'),
    ('ESCAPEMENT ESTIMATE – EXPANDED/FINAL', 'Escapement Estimate – expanded/final'),
    ('ESCAPEMENT ESTIMATE – UNEXPANDED/PRELIMINARY', 'Escapement Estimate – unexpanded/preliminary'),
    ('HABITAT DATA', 'Habitat data'),
    ('HARVEST RATE', 'Harvest rate'),
    ('STOCK RECRUITMENT', 'Stock Recruitment'),
    ('SURVIVAL RATE', 'Survival Rate'),
    ('MARKED STATUS', 'Marked status'),
    ('PROPORTION OF SAMPLED FISH EFFORT/TIME', 'Proportion of sampled fish effort/time'),
    ('PROPORTION OF IN-RIVER SALMON DESTINED FOR SPAWNING', 'Proportion of in-river salmon destined for spawning'),
    ('SEX COMPOSITION', 'Sex Composition'),
    ('AGE COMPOSITION DATA', 'Age Composition Data'),
    ('STOCK COMPOSITION (GSI / DNA)DATA', 'Stock composition (GSI / DNA)Data'),
    ('CONDITION OF FISH (DNA BASED)', 'Condition of Fish (DNA based)'),
    ('RATIO OF CATCHABILITY', 'Ratio of catchability'),
    ('OTHER', 'Other'),
)

DATA_PROGRAMS = (
    ('R', 'R'),
    ('VIDESC', 'VidEsc'),
    ('STRATIFIED POPULATION ANALYSIS SYSTEM', 'Stratified Population Analysis System'),
    ('BAYESIAN TIME STRATIFIED PETERSEN ANALYSIS SYSTEM', 'Bayesian Time Stratified Petersen Analysis System'),
    ('MICROSOFT EXCEL', 'Microsoft Excel'),
)

DATA_COMMUNICATION = (
    ('PRESENTATIONS', 'Presentations'),
    ('WORKSHOPS', 'Workshops'),
    ('REPORTS', 'Reports'),
    ('DATA SUMMARIES', 'Data Summaries'),
    ('BULLETINS', 'Bulletins'),
    ('UNKNOWN', 'Unknown'),
    ('NOT APPLICABLE', 'Not applicable'),
    ('OTHER', 'Other'),
)

REPORT_TIMELINE = (
    ('PROGRESS REPORT', 'Progress Report'),
    ('FINAL REPORT', 'Final Report'),
    ('NOT APPLICABLE', 'Not applicable'),
    ('OTHER', 'Other'),
)

REPORT_TYPE = (
    ('PROJECT', 'Project'),
    ('CATCH', 'Catch'),
    ('POPULATION', 'Population'),
    ('SAMPLING', 'Sampling'),
    ('METHODS', 'Sampling'),
    ('HABITAT', 'Habitat'),
    ('RECOVERY', 'Recovery'),
    ('ENHANCEMENT', 'Enhancement'),
    ('R&D', 'R&D'),
    ('ADMINISTRATION', 'Administration'),
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
    ('Biological',
    (('ADIPOSE CLIPS', 'Adipose Clips'),
    ('AGE', 'Age'),
    ('CATCH MONITORING', 'Catch Monitoring (Counts)'),
    ('CATCH EFFORT', 'Catch Effort'),
    ('AUXILIARY APPENDAGE CLIPS', 'Auxiliary Appendage Clips'),
    ('CWT TAGGING', 'CWT Tagging'),
    ('CWT RECOVERY', 'CWT Recovery(Heads)'),
    ('COUNT', 'Count(Enumeration)'),
    ('DNA', 'DN(foGenetiStocIdentification)'),
    ('FICLIPS', 'FiClips'),
    ('HEALTCONDITION', 'HealtCondition'),
    ('SIZE', 'Size'),
    ('PIT TAGGING', 'PIT Tagging'),
    ('PIT RECOVERY', 'PIT Recovery'),
    ('OTOLITHS', 'Otoliths'),
    ('SELICCOUNTS', 'SeLicCounts'),
    ('SECONDARMARKS', 'SecondarMarks'),
    ('SEX', 'Sex'),
    ('SPAGHETTI TAGGING', 'Spaghetti Tagging'),
    ('SPAGHETTI TAG RECOVERY', 'Spaghetti Tag Recovery'),
    ('SPAWNING SUCCESS', 'Spawning Success'),
    ('SPECIES COMPOSITION', 'Species Composition'),
    ('TAG LOSS DATA', 'Tag Loss Data'),
    ('TISSUE COLLECTION', 'Tissue Collection (Disease)'),
    ('EGG CHARACTERISTICS', 'Egg Characteristics'),
    ('ENHANCEMENT', 'Enhancement'),
    ('BROOD COLLECTION', 'Brood Collection'),
    ('OTHER', 'Other'))),

    ('Habitat - Monitoring',
    (('TEMPERATURE', 'Temperature'),
    ('WATER QUALITY', 'Water Quality'),
    ('WATER FLOW', 'Water Flow'),
    ('STREAM DEBRIS', 'Stream Debris'),
    ('PLANKTON', 'Plankton'),
    ('OTHER', 'Other'))),

    ('Habitat - Restoration',
    (('FISH PASSAGE', 'Fish Passage'),
    ('WATER LEVELS', 'Water Levels'),
    ('RIPARIAN', 'Riparian'),
    ('ESTUARINE', 'Estuarine'),
    ('NEARSHORE MARINE', 'Nearshore Marine'),
    ('INSTREAM STRUCTURE', 'Instream Structure'),
    ('FLOODPLAIN CONNECTIVITY', 'Floodplain connectivity'),
    ('WATERSHED', 'Watershed'),
    ('NUTRIENT SUPPLEMENTATION', 'Nutrient Supplementation'),
    ('OTHER', 'Other'))),
)

OUTCOMES = (
    ('SUBMITTED SAMPLES', 'Submitted samples'),
    ('LIVE COLLECTION', 'Live Collection'),
    ('SUMMARIZED DATA', 'Summarized data'),
    ('RAW DATA', 'Raw Data'),
    ('Stream Inspection Log', 'Stream Inspection Log'),
    ('ANALYZED DATA - NON-EXPANDED ESTIMATES', 'Analyzed data - non-expanded estimates'),
    ('ANALYZED DATA - EXPANDED ESTIMATES', 'Analyzed data - expanded estimates'),
    ('ANALYZED DATA - OTHER', 'Analyzed data - other'),
    ('ANNUAL STREAM REPORT', 'Annual Stream Report'),
    ('REPORT DOCUMENT', 'Report document'),
    ('SUMMARY OF ACTIVITIES', 'Summary of Activities'),
    ('MEETING SUMMARY', 'Meeting Summary'),
    ('OTHER', 'Other'),
)

REPORT_SENT = (
    ('GOVERNMENT FUNDING AGENCY', 'Government funding agency'),
    ('DFO STAFF', 'DFO staff'),
    ('EXTERNAL ORGANIZATIONS', 'External organizations'),
    ('UNKNOWN', 'Unknown'),
    ('NOT APPLICABLE', 'Not applicable'),
    ('OTHER', 'Other'),
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
    ('LEVEL 1', 'Level 1 (Very High Quality)'),
    ('LEVEL 2', 'LEVEL 2 (High Quality)'),
    ('Level 3', 'Level 3 (Good Quality)'),
    ('LEVEL 4', 'Level 4 (Moderate Quality)'),
    ('LEVEL 5', 'Level 5 (Low Quality)'),
    ('UNKNOWN', 'Unknown'),
    ('NOT APPLICABLE', 'Not applicable'),
)

OUTCOME_BARRIER = (
    ('SITE ACCESS', 'Site Access'),
    ('EQUIPMENT FAILURE', 'Equipment failure'),
    ('EQUIPMENT NOT AVAILABLE', 'Equipment not available'),
    ('STAFFING UNAVAILABLE', 'Staffing unavailable'),
    ('STAFFING NOT TRAINED', 'Staffing not trained'),
    ('WEATHER', 'Weather'),
)

SUBJECT = (
    ('PEOPLE', 'People'),
    ('PROJECTS', 'Projects'),
    ('OBJECTIVES', 'Objectives'),
    ('METHODS', 'Methods'),
    ('DATA', 'Data'),
    ('ORGANIZATIONS', 'Organizations'),
    ('OTHER', 'Other'),
)

FN_COMMUNICATIONS = (
    ('PRESENTATIONS', 'Presentations'),
    ('WORKSHOPS', 'Workshops'),
    ('REPORTS', 'Reports'),
    ('DATA SUMMARIES', 'Data Summaries'),
    ('BULLETINS', 'Bulletins'),
    ('OTHER', 'Other'),
    ('NOT APPLICABLE', 'Not Applicable'),
)