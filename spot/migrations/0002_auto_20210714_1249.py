# Generated by Django 3.1.2 on 2021-07-14 19:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('spot', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ObjectiveOutcome',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('outcome_category', models.CharField(blank=True, choices=[('SUBMITTED SAMPLES', 'Submitted samples'), ('SUMMARIZED DATA', 'Summarized data'), ('RAW DATA', 'Raw Data'), ('Stream Inspection Log', 'Stream Inspection Log'), ('ANALYZED DATA - NON-EXPANDED ESTIMATES', 'Analyzed data - non-expanded estimates'), ('ANALYZED DATA - EXPANDED ESTIMATES', 'Analyzed data - expanded estimates'), ('ANALYZED DATA - OTHER', 'Analyzed data - other'), ('ANNUAL STREAM REPORT', 'Annual Stream Report'), ('REPORT DOCUMENT', 'Report document'), ('SUMMARY OF ACTIVITIES', 'Summary of Activities'), ('MEETING SUMMARY', 'Meeting Summary'), ('OTHER', 'Other')], max_length=64, null=True, verbose_name='outcomes category')),
            ],
            options={
                'ordering': ['report_reference'],
            },
        ),
        migrations.DeleteModel(
            name='Region',
        ),
        migrations.AlterModelOptions(
            name='objectivedatatypequality',
            options={'ordering': ['sample_type']},
        ),
        migrations.RemoveField(
            model_name='data',
            name='data_communication_recipient',
        ),
        migrations.RemoveField(
            model_name='objective',
            name='report_reference',
        ),
        migrations.RemoveField(
            model_name='objective',
            name='sample_type',
        ),
        migrations.RemoveField(
            model_name='objectivedatatypequality',
            name='outcome_deliverable',
        ),
        migrations.AddField(
            model_name='data',
            name='data_communication',
            field=models.CharField(blank=True, choices=[('PRESENTATIONS', 'Presentations'), ('WORKSHOPS', 'Workshops'), ('REPORTS', 'Reports'), ('DATA SUMMARIES', 'Data Summaries'), ('BULLETINS', 'Bulletins'), ('UNKNOWN', 'Unknown'), ('N/A', 'Not applicable'), ('OTHER', 'Other')], default=None, max_length=32, null=True, verbose_name='how was data communicated to recipient'),
        ),
        migrations.AddField(
            model_name='objective',
            name='outcome_deadline',
            field=models.DateField(blank=True, null=True, verbose_name='outcome deadline'),
        ),
        migrations.AddField(
            model_name='objectivedatatypequality',
            name='sample_type',
            field=models.CharField(blank=True, choices=[('Biological', (('ADIPOSE CLIPS', 'Adipose Clips'), ('AGE', 'Age'), ('CATCH MONITORING', 'Catch Monitoring (Counts)'), ('CATCH EFFORT', 'Catch Effort'), ('AUXILIARY APPENDAGE CLIPS', 'Auxiliary Appendage Clips'), ('CWT TAGGING', 'CWT Tagging'), ('CWT RECOVERY', 'CWT Recovery(Heads)'), ('COUNT', 'Count(Enumeration)'), ('DNA', 'DN(foGenetiStocIdentification)'), ('FICLIPS', 'FiClips'), ('HEALTCONDITION', 'HealtCondition'), ('SIZE', 'Size'), ('PIT TAGGING', 'PIT Tagging'), ('PIT RECOVERY', 'PIT Recovery'), ('OTOLITHS', 'Otoliths'), ('SELICCOUNTS', 'SeLicCounts'), ('SECONDARMARKS', 'SecondarMarks'), ('SEX', 'Sex'), ('SPAGHETTI TAGGING', 'Spaghetti Tagging'), ('SPAGHETTI TAG RECOVERY', 'Spaghetti Tag Recovery'), ('SPAWNING SUCCESS', 'Spawning Success'), ('SPECIES COMPOSITION', 'Species Composition'), ('TAG LOSS DATA', 'Tag Loss Data'), ('TISSUE COLLECTION', 'Tissue Collection (Disease)'), ('EGG CHARACTERISTICS', 'Egg Characteristics'), ('ENHANCEMENT', 'Enhancement'), ('BROOD COLLECTION', 'Brood Collection'), ('OTHER', 'Other'))), ('Habitat - Monitoring', (('TEMPERATURE', 'Temperature'), ('WATER QUALITY', 'Water Quality'), ('WATER FLOW', 'Water Flow'), ('STREAM DEBRIS', 'Stream Debris'), ('PLANKTON', 'Plankton'), ('OTHER', 'Other'))), ('Habitat - Restoration', (('FISH PASSAGE', 'Fish Passage'), ('WATER LEVELS', 'Water Levels'), ('RIPARIAN', 'Riparian'), ('ESTUARINE', 'Estuarine'), ('NEARSHORE MARINE', 'Nearshore Marine'), ('INSTREAM STRUCTURE', 'Instream Structure'), ('FLOODPLAIN CONNECTIVITY', 'Floodplain connectivity'), ('WATERSHED', 'Watershed'), ('NUTRIENT SUPPLEMENTATION', 'Nutrient Supplementation'), ('OTHER', 'Other')))], default=None, max_length=64, null=True, verbose_name='sample type/specific data item'),
        ),
        migrations.AlterField(
            model_name='data',
            name='barrier_data_check_entry',
            field=models.CharField(blank=True, choices=[('NO PERSON AVAILABLE', 'No person available'), ('SAMPLE DATA REQUIRES MORE WORK BEFORE IT CAN BE ENTERED INTO DATABASE', 'Sample data requires more work before it can be entered into database'), ('PERSON AVAILABLE BUT LACK OF TRAINING', 'Person available but lack of training'), ('EQUIPMENT IS AVAILABLE BUT NOT WORKING', 'Equipment is available but not working'), ('EQUIPMENT IS NOT AVAILABLE', 'Equipment is not available'), ('IT ISSUES', 'IT issues'), ('NETWORK CONNECTION ISSUES', 'Network connection issues'), ('UNKNOWN', 'Unknown'), ('N/A', 'Not applicable'), ('OTHER', 'Other')], default=None, max_length=128, null=True, verbose_name='Barriers to data checks/entry to database?'),
        ),
        migrations.AlterField(
            model_name='data',
            name='data_products',
            field=models.CharField(blank=True, choices=[('RELATIVE ABUNDANCE', 'Relative Abundance'), ('ESCAPEMENT ESTIMATE – EXPANDED/FINAL', 'Escapement Estimate – expanded/final'), ('ESCAPEMENT ESTIMATE – UNEXPANDED/PRELIMINARY', 'Escapement Estimate – unexpanded/preliminary'), ('HABITAT DATA', 'Habitat data'), ('HARVEST RATE', 'Harvest rate'), ('STOCK RECRUITMENT', 'Stock Recruitment'), ('SURVIVAL RATE', 'Survival Rate'), ('MARKED STATUS', 'Marked status'), ('PROPORTION OF SAMPLED FISH EFFORT/TIME', 'Proportion of sampled fish effort/time'), ('PROPORTION OF IN-RIVER SALMON DESTINED FOR SPAWNING', 'Proportion of in-river salmon destined for spawning'), ('SEX COMPOSITION', 'Sex Composition'), ('AGE COMPOSITION DATA', 'Age Composition Data'), ('STOCK COMPOSITION (GSI / DNA)DATA', 'Stock composition (GSI / DNA)Data'), ('CONDITION OF FISH (DNA BASED)', 'Condition of Fish (DNA based)'), ('RATIO OF CATCHABILITY', 'Ratio of catchability'), ('OTHER', 'Other')], default=None, max_length=64, null=True, verbose_name='data products'),
        ),
        migrations.AlterField(
            model_name='data',
            name='data_products_database',
            field=models.CharField(blank=True, choices=[('ADF&G ZANDER', 'ADF&G Zander'), ('PSMFC CWT', 'PSMFC CWT'), ('ADF&G REGION 1', 'ADF&G Region 1'), ('ADF&G CWT ONLINE RELEASE', 'ADF&G CWT Online Release'), ('ADF&G SF RESEARCH AND TECHNICAL SERVICES', 'ADF&G SF Research and Technical Services'), ('NUSEDS', 'NuSEDs'), ('IREC', 'iREC'), ('KREST', 'KREST'), ('FIRST NATIONS DATABASES', 'First Nations Databases'), ('SHARED DFO DRIVES', 'Shared DFO drives'), ('FIRST NATIONS HARVEST (AHMS)', 'First Nations Harvest (AHMS)'), ('FISHERY OPERATIONS SYSTEM (FOS)', 'Fishery Operations System (FOS)'), ('MARK RECOVERY PROGRAM (MRPRO)', 'Mark Recovery Program (MRPRO)'), ('CLOCKWORK', 'Clockwork'), ('BIODATABASE (SOUTH COAST DFO)', 'Biodatabase (South Coast DFO)'), ('PADS', 'PADS'), ('OTOMANAGER', 'Otomanager'), ('PACIFIC SALMON COMMISSION', 'Pacific Salmon Commission'), ('GENETICS GROUP (PBS)', 'Genetics Group (PBS)'), ('INDIVIDUAL COMPUTER', 'Individual computer'), ('PACIFIC STATES MARINE FISHERIES COMMISSION (WWW.RMPC.ORG)', 'Pacific States Marine Fisheries Commission (www.rmpc.org)'), ('CENTRAL COAST FSC CATCH', 'Central Coast FSC Catch'), ('PRIVATE', 'Private'), ('PIT TAG INFORMATION SYSTEM (PTAGIS)', 'PIT Tag Information System (PTAGIS)'), ('N/A', 'Not applicable'), ('OTHER', 'Other')], default=None, max_length=64, null=True, verbose_name='data products database'),
        ),
        migrations.AlterField(
            model_name='data',
            name='data_programs',
            field=models.CharField(blank=True, choices=[('R', 'R'), ('VIDESC', 'VidEsc'), ('STRATIFIED POPULATION ANALYSIS SYSTEM', 'Stratified Population Analysis System'), ('BAYESIAN TIME STRATIFIED PETERSEN ANALYSIS SYSTEM', 'Bayesian Time Stratified Petersen Analysis System'), ('MICROSOFT EXCEL', 'Microsoft Excel')], default=None, max_length=64, null=True, verbose_name='data programs'),
        ),
        migrations.AlterField(
            model_name='data',
            name='sample_barrier',
            field=models.CharField(blank=True, choices=[('WEATHER', 'Weather'), ('SITE ACCESS', 'Site Access'), ('EQUIPMENT FAILURE', 'Equipment failure'), ('EQUIPMENT NOT AVAILABLE', 'Equipment not available'), ('STAFFING UNAVAILABLE', 'Staffing unavailable'), ('STAFFING NOT TRAINED', 'Staffing not trained'), ('UNKNOWN', 'Unknown'), ('N/A', 'Not applicable'), ('OTHER', 'Other')], default=None, max_length=64, null=True, verbose_name='barriers to sample collection'),
        ),
        migrations.AlterField(
            model_name='data',
            name='sample_format',
            field=models.CharField(blank=True, choices=[('EXCEL', 'Excel'), ('PAPER', 'Paper'), ('LOG BOOKS', 'Log Books'), ('WORD', 'Word'), ('PDF FILES', 'PDF Files'), ('SIL-HARDCOPY', 'SIL-hardcopy'), ('SIL-DIGITIZED', 'SIL-digitized'), ('INSTRUMENT FILES', 'Instrument Files'), ('DATABASE FILED', 'Database Filed'), ('SENS', 'SENS'), ('WET NOTES', 'Wet Notes'), ('N/A', 'Not applicable'), ('OTHER', 'Other')], default=None, max_length=32, null=True, verbose_name='sample format'),
        ),
        migrations.AlterField(
            model_name='data',
            name='samples_collected',
            field=models.CharField(blank=True, choices=[('Biological', (('FISH COUNTS', 'Fish counts (fence, catch, static)'), ('ESCAPEMENT ESTIMATE', 'Escapement estimate (non-expanded)'), ('SPAWNING DENSITY', 'Spawning density'), ('BROODSTOCK REMOVAL', 'Broodstock removal'), ('FISH AT LOCATION', 'Fish at location (by segment or area)'), ('SPAWNING LOCATION', 'Spawning location'), ('MIGRATION TIMING', 'Migration timing'), ('LENGTH', 'Length'), ('CLIP STATUS', 'Clip status'), ('TAG STATUS', 'Tag status'), ('HEAD COLLECTION', 'Head collection'), ('SCALE SAMPLES ', 'Scale samples '), ('SMEAR SAMPLES', 'Smear samples'), ('OTOLITHS', 'Otoliths'), ('OTHER', 'Other'))), ('Habitat', (('DISSOLVED OXYGEN', 'Dissolved oxygen'), ('TEMPERATURE', 'Temperature'), ('SALINITY', 'Salinity'), ('WATER FLOW', 'Water flow'), ('TURBIDITY', 'Turbidity'), ('WEATHER CONDITIONS', 'Weather conditions'), ('ZOOPLANKTON', 'Zooplankton'), ('INVERTEBRATES', 'Invertebrates'), ('OTHER', 'Other'))), ('Restoration', (('AERIAL SURVEYS', 'Aerial surveys'), ('eDNA', 'eDNA'), ('ELECTROFISHING', 'Electrofishing'), ('HYDROLOGICAL MODELLING', 'Hydrological modelling'), ('INVASIVE SPECIES SURVEYS', 'Invasive species surveys'), ('PHYSICAL HABITAT SURVEYS', 'Physical habitat surveys'), ('VEGETATION SURVEYS', 'Vegetation surveys'), ('NETS AND TRAPS', 'Nets and traps'), ('PHOTO POINT MONITORING', 'Photo point monitoring'), ('PIT TAGGING AND TELEMETRY', 'PIT tagging and telemetry'), ('SNORKEL SURVEYS', 'Snorkel surveys'), ('TEMPERATURE LOGGERS', 'Temperature loggers'), ('HYDROMETER INSTALLMENTS', 'Hydrometer installments'), ('WATER SAMPLING', 'Water sampling'), ('QUALITATIVE VISUAL ASSESSMENT', 'Qualitative visual assessment'), ('OTHER', 'Other')))], default=None, max_length=64, null=True, verbose_name='sameples collected'),
        ),
        migrations.AlterField(
            model_name='data',
            name='samples_collected_database',
            field=models.CharField(blank=True, choices=[('ADF&G ZANDER', 'ADF&G Zander'), ('PSMFC CWT', 'PSMFC CWT'), ('ADF&G REGION 1', 'ADF&G Region 1'), ('ADF&G CWT ONLINE RELEASE', 'ADF&G CWT Online Release'), ('ADF&G SF RESEARCH AND TECHNICAL SERVICES', 'ADF&G SF Research and Technical Services'), ('NUSEDS', 'NuSEDs'), ('IREC', 'iREC'), ('KREST', 'KREST'), ('FIRST NATIONS DATABASES', 'First Nations Databases'), ('SHARED DFO DRIVES', 'Shared DFO drives'), ('FIRST NATIONS HARVEST (AHMS)', 'First Nations Harvest (AHMS)'), ('FISHERY OPERATIONS SYSTEM (FOS)', 'Fishery Operations System (FOS)'), ('MARK RECOVERY PROGRAM (MRPRO)', 'Mark Recovery Program (MRPRO)'), ('CLOCKWORK', 'Clockwork'), ('BIODATABASE (SOUTH COAST DFO)', 'Biodatabase (South Coast DFO)'), ('PADS', 'PADS'), ('OTOMANAGER', 'Otomanager'), ('PACIFIC SALMON COMMISSION', 'Pacific Salmon Commission'), ('GENETICS GROUP (PBS)', 'Genetics Group (PBS)'), ('INDIVIDUAL COMPUTER', 'Individual computer'), ('PACIFIC STATES MARINE FISHERIES COMMISSION (WWW.RMPC.ORG)', 'Pacific States Marine Fisheries Commission (www.rmpc.org)'), ('CENTRAL COAST FSC CATCH', 'Central Coast FSC Catch'), ('PRIVATE', 'Private'), ('PIT TAG INFORMATION SYSTEM (PTAGIS)', 'PIT Tag Information System (PTAGIS)'), ('N/A', 'Not applicable'), ('OTHER', 'Other')], default=None, max_length=64, null=True, verbose_name='samples collected database'),
        ),
        migrations.AlterField(
            model_name='data',
            name='species_data',
            field=models.CharField(blank=True, choices=[('CH', 'Chinook Salmon (Oncorhynchus tshawytscha)'), ('CM', 'Chum Salmon (Oncorhynchus keta)'), ('CO', 'Coho Salmon (Oncorhynchus kisutch)'), ('PK', 'Pink Salmon (Oncorhynchus gorbuscha)'), ('SK', 'Sockeye Salmon (Oncorhynchus nerka)'), ('ST', 'Steelhead (Oncorhynchus mykiss)'), ('UNKNOWN', 'Unknown'), ('N/A', 'Not applicable'), ('OTHER', 'Other')], default=None, max_length=32, null=True, verbose_name='species data'),
        ),
        migrations.RemoveField(
            model_name='method',
            name='data_entry_method_type',
        ),
        migrations.AddField(
            model_name='method',
            name='data_entry_method_type',
            field=models.CharField(blank=True, choices=[('DIRECT ENTRY INTO COMPUTER', 'Direct entry into computer'), ('DIRECT ENTRY INTO DATABASE', 'Direct entry into database'), ('PAPER, FOLLOWED BY ENTRY INTO COMPUTER', 'Paper, followed by entry into computer'), ('UNKNOWN', 'Unknown'), ('N/A', 'Not applicable'), ('OTHER', 'Other')], default=None, max_length=64, verbose_name='data entry method type'),
        ),
        migrations.RemoveField(
            model_name='method',
            name='field_work_method_type',
        ),
        migrations.AddField(
            model_name='method',
            name='field_work_method_type',
            field=models.CharField(blank=True, choices=[('Biological - Visual', (('STREAM WALKS', 'Stream walks'), ('BOAT SURVEY', 'Boat survey'), ('SNORKLE SURVEY', 'Snorkle survey'), ('RAFT', 'Raft'), ('DEADPITCH', 'Deadpitch'), ('MICROTROLLING', 'Microtrolling'), ('ROVING', 'Roving'), ('FISHWHEEL', 'Fishwheel'), ('ELECTROFISHING', 'Electrofishing'))), ('Biological - Intensive Measure', (('WEIR', 'Weir'), ('FENCE', 'Fence'), ('FISHWAY-TUNNELS', 'Fishway-tunnels'))), ('Biological - Instrumentation', (('SONAR', 'Sonar'), ('DIDSON', 'DIDSON'), ('VIDEO', 'Video'), ('HYDROACOUSTIC', 'Hydroacoustic'), ('RESISTIVITY', 'Resistivity'), ('RIVER SURVEYOR', 'River Surveyor'))), ('Biological - Tagging', (('PIT', 'Pit'), ('CODED WIRE TAG', 'Coded Wire Tag'), ('HALLPRINT', 'Hallprint'), ('SPAGHETTI', 'Spaghetti'), ('RADIO', 'Radio'))), ('Biological - Biodata', (('SIZE', 'Size'), ('SEX', 'Sex'), ('AGE', 'Age'), ('DNA (GENETIC STOCK ID)', 'DNA (Genetic Stock ID)'), ('OTOLITHS', 'Otoliths'), ('HEALTH CONDITION', 'Health Condition'))), ('Biological - Aerial', (('PLANE', 'Plane'), ('HELICOPTER', 'Helicopter'), ('DRONE', 'Drone'))), ('Biological - Catch', (('CREEL', 'Creel'), ('OTHER', 'Other'))), ('Biological - Trapping', (('SMOLT', 'Smolt'), ('SEINES', 'Seines'), ('GILL NETTING', 'Gill Netting'))), ('Biological - Enhancement', (('BROODSTOCK TAKE', 'Broodstock Take'), ('OTHER', 'Other'))), ('Field Work - Habitat', (('PHYSICAL ANALYSIS', 'Physical Analysis'), ('CHEMICAL ANALYSIS', 'Chemical Analysis'), ('PLANKTON', 'Plankton'), ('RIPARIAN', 'Riparian'), ('OTHER', 'Other'))), ('Habitat - Restoration', (('AERIAL SURVEYS', 'Aerial Surveys'), ('EDNA', 'eDNA'), ('ELECTOFISHING', 'Electofishing'), ('HYDROLOGICAL MODELLING', 'Hydrological modelling'), ('INVASIVE SPECIES SURVEYS', 'Invasive species surveys'), ('PHYSICAL HABITAT SURVEYS', 'Physical habitat surveys'), ('vEGETATION SURVEYS', 'Vegetation Surveys'), ('NETS AND TRAPS', 'Nets and Traps'), ('PHOTO POINT MONITORING', 'Photo Point Monitoring'), ('PIT TAGGING AND TELEMETRY', 'PIT Tagging and Telemetry'), ('SNORKLE SURVEYS', 'Snorkle Surveys'), ('TEMPERATURE LOGGERS', 'Temperature Loggers'), ('HYDROMETER INSTALLMENTS', 'Hydrometer Installments'), ('WATER SAMPLING', 'Water Sampling'), ('QUALITATIVE VISUAL ASSESSMENT', 'Qualitative visual assessment'), ('OTHER', 'Other')))], default=None, max_length=64, verbose_name='field work methods type/class'),
        ),
        migrations.RemoveField(
            model_name='method',
            name='planning_method_type',
        ),
        migrations.AddField(
            model_name='method',
            name='planning_method_type',
            field=models.CharField(blank=True, choices=[('FEASIBILITY STUDY', 'Feasibility Study'), ('PROJECT DESIGN', 'Project Design'), ('RESOURCE ALLOCATION', 'Resource Allocation'), ('OBJECTIVE-SETTING', 'Objective-setting'), ('OTHER', 'Other')], default=None, max_length=64, verbose_name='planning method type'),
        ),
        migrations.RemoveField(
            model_name='method',
            name='sample_processing_method_type',
        ),
        migrations.AddField(
            model_name='method',
            name='sample_processing_method_type',
            field=models.CharField(blank=True, choices=[('AGING', 'Aging'), ('DNA (GENETIC STOCK ID)', 'DNA (Genetic Stock ID)'), ('INSTRUMENT DATA PROCESSING', 'Instrument data processing'), ('SCALES', 'Scales'), ('OTOLITHS', 'Otoliths'), ('DNA', 'DNA'), ('HEADS', 'Heads'), ('OTHER', 'Other')], default=None, max_length=64, verbose_name='sample processing method type'),
        ),
        migrations.AlterField(
            model_name='objective',
            name='activity',
            field=models.CharField(blank=True, choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'), ('11', '11'), ('12', '12'), ('13', '13'), ('14', '14'), ('15', '15'), ('16', '16'), ('17', '17'), ('18', '18'), ('19', '19'), ('20', '20'), ('OTHER', 'Other')], max_length=10, null=True, verbose_name='activity'),
        ),
        migrations.AlterField(
            model_name='objective',
            name='capacity_building',
            field=models.CharField(blank=True, choices=[('NEW TRAINING', 'New Training'), ('NEW STAFF INTEREST', 'New staff interest'), ('VOLUNTEERS SHOWED INTEREST', 'Volunteers showed interest'), ('COMMUNITY CONNECTIONS MADE', 'Community connections made'), ('PUBLIC ENGAGEMENT', 'Public engagement'), ('PREVIOUS STAFF TRAINING UPGRADED', 'Previous Staff Training upgraded'), ('EQUIPMENT RESOURCES IMPROVED', 'Equipment resources improved'), ('IMPROVED FISHERIES KNOWLEDGE AMONG COMMUNITY', 'Improved fisheries knowledge among community'), ('IMPROVED COMMUNICATION BETWEEN DFO AND FUNDING RECIPIENT', 'Improved communication between DFO and funding recipient')], default=None, max_length=64, null=True, verbose_name='what capacity building did this project provide'),
        ),
        migrations.AlterField(
            model_name='objective',
            name='key_element',
            field=models.CharField(blank=True, choices=[('A', 'A'), ('B', 'B'), ('C', 'B'), ('D', 'D'), ('OTHER', 'Other')], max_length=10, null=True, verbose_name='key element'),
        ),
        migrations.AlterField(
            model_name='objective',
            name='objective_category',
            field=models.CharField(blank=True, choices=[('ESCAPEMENT', 'Escapement'), ('CONSERVATION', 'Conservation'), ('CATCH (FIRST NATIONS)', 'Catch (First Nations)'), ('CATCH (RECREATIONAL)', 'Catch (Recreational)'), ('CATCH (COMMERCIAL)', 'Catch (Commercial)'), ('ENHANCEMENT', 'Enhancement'), ('ADMINISTRATION', 'Administration'), ('UNKNOWN', 'Unknown'), ('N/A', 'Not applicable')], default=None, max_length=64, null=True, verbose_name='Objective Category'),
        ),
        migrations.AlterField(
            model_name='objective',
            name='outcome_barrier',
            field=models.CharField(blank=True, choices=[('SITE ACCESS', 'Site Access'), ('EQUIPMENT FAILURE', 'Equipment failure'), ('EQUIPMENT NOT AVAILABLE', 'Equipment not available'), ('STAFFING UNAVAILABLE', 'Staffing unavailable'), ('STAFFING NOT TRAINED', 'Staffing not trained'), ('WEATHER', 'Weather')], default=None, max_length=64, null=True, verbose_name='barrier to achieve outcomes?'),
        ),
        migrations.AlterField(
            model_name='objective',
            name='outcome_deadline_met',
            field=models.BooleanField(default=False, verbose_name='was the outcome deadline met?'),
        ),
        migrations.AlterField(
            model_name='objective',
            name='species',
            field=models.CharField(blank=True, choices=[('CH', 'Chinook Salmon (Oncorhynchus tshawytscha)'), ('CM', 'Chum Salmon (Oncorhynchus keta)'), ('CO', 'Coho Salmon (Oncorhynchus kisutch)'), ('PK', 'Pink Salmon (Oncorhynchus gorbuscha)'), ('SK', 'Sockeye Salmon (Oncorhynchus nerka)'), ('ST', 'Steelhead (Oncorhynchus mykiss)'), ('UNKNOWN', 'Unknown'), ('N/A', 'Not applicable'), ('OTHER', 'Other')], default=None, max_length=10, null=True, verbose_name='species'),
        ),
        migrations.AlterField(
            model_name='objective',
            name='target_sample_number',
            field=models.TextField(blank=True, max_length=1000, null=True, verbose_name='target sample number'),
        ),
        migrations.AlterField(
            model_name='objectivedatatypequality',
            name='outcome_quality',
            field=models.CharField(blank=True, choices=[('LEVEL 1', 'Level 1 (Very High Quality)'), ('LEVEL 2', 'LEVEL 2 (High Quality)'), ('Level 3', 'Level 3 (Good Quality)'), ('LEVEL 4', 'Level 4 (Moderate Quality)'), ('LEVEL 5', 'Level 5 (Low Quality)'), ('UNKNOWN', 'Unknown'), ('N/A', 'Not applicable')], default=None, max_length=64, null=True, verbose_name='quality of outcome'),
        ),
        migrations.AlterField(
            model_name='objectivedatatypequality',
            name='report_sent_to',
            field=models.CharField(blank=True, choices=[('GOVERNMENT FUNDING AGENCY', 'Government funding agency'), ('DFO STAFF', 'DFO staff'), ('EXTERNAL ORGANIZATIONS', 'External organizations'), ('UNKNOWN', 'Unknown'), ('N/A', 'Not applicable'), ('OTHER', 'Other')], default=None, max_length=64, null=True, verbose_name='reporting sent to'),
        ),
        migrations.AlterField(
            model_name='organization',
            name='country',
            field=models.CharField(blank=True, choices=[('CANADA', 'Canada'), ('USA', 'USA')], max_length=64, null=True, verbose_name='country'),
        ),
        migrations.AlterField(
            model_name='organization',
            name='organization_type',
            field=models.CharField(blank=True, choices=[('FIRST NATION', 'First Nations'), ('COMPANY', 'Company'), ('GOVERNMENT ORGANIZATION', 'Government Organization')], default=None, max_length=32, null=True, verbose_name='organization type'),
        ),
        migrations.AlterField(
            model_name='organization',
            name='province',
            field=models.CharField(blank=True, choices=[('ALBERTA', 'Alberta'), ('BRITISH COLUMBIA', 'British Columbia'), ('MANITOBA', 'Manitoba'), ('NEW BRUNSWICK', 'New Brunswick'), ('NEWFOUNDLAND & LABRADOR', 'Newfoundland & Labrador'), ('NOVA SCOTIA', 'Nova Scotia'), ('ONTARIO', 'Ontario'), ('PRINCE EDWARD ISLAND', 'Prince Edward Island'), ('QUEBEC', 'Quebec'), ('SASKATCHEWAN', 'Saskatchewan'), ('NORTHWEST TERRITORIES', 'Northwest Territories'), ('NUNAVUT', 'Nunavut'), ('YUKON', 'Yukon'), ('WASHINGTON', 'Washington'), ('ALASKA', 'Alaska')], max_length=64, null=True, verbose_name='province/state'),
        ),
        migrations.AlterField(
            model_name='person',
            name='province',
            field=models.CharField(blank=True, choices=[('ALBERTA', 'Alberta'), ('BRITISH COLUMBIA', 'British Columbia'), ('MANITOBA', 'Manitoba'), ('NEW BRUNSWICK', 'New Brunswick'), ('NEWFOUNDLAND & LABRADOR', 'Newfoundland & Labrador'), ('NOVA SCOTIA', 'Nova Scotia'), ('ONTARIO', 'Ontario'), ('PRINCE EDWARD ISLAND', 'Prince Edward Island'), ('QUEBEC', 'Quebec'), ('SASKATCHEWAN', 'Saskatchewan'), ('NORTHWEST TERRITORIES', 'Northwest Territories'), ('NUNAVUT', 'Nunavut'), ('YUKON', 'Yukon'), ('WASHINGTON', 'Washington'), ('ALASKA', 'Alaska')], max_length=64, null=True, verbose_name='province/state'),
        ),
        migrations.AlterField(
            model_name='person',
            name='role',
            field=models.CharField(blank=True, choices=[('CHIEF', 'Chief'), ('BIOLOGIST', 'Biologist'), ('AQUATICS MANAGER', 'Aquatics Manager'), ('TECHNICIAN', 'Technician'), ('DIRECTOR', 'Director'), ('FISHERIES MANAGER', 'Fisheries Manager'), ('REFUGE MANAGER', 'Refuge Manager'), ('SCIENTIST', 'Scientist'), ('STEWARDSHIP DIRECTOR', 'Stewardship Director'), ('UNKNOWN', 'Unknown'), ('OTHER', 'Other')], default=None, max_length=64, null=True, verbose_name='role'),
        ),
        migrations.AlterField(
            model_name='project',
            name='DFO_link',
            field=models.CharField(blank=True, choices=[('FISHERIES MANAGEMENT', 'Fisheries Management'), ('COMMERCIAL FISHERIES', 'Commercial Fisheries'), ('RECREATIONAL FISHERIES', 'Recreational Fisheries'), ('ABORIGINAL PROG. & TREAT', 'Aboriginal Prog. & Treat'), ('AQUACULTURE MANAGEMENT', 'Aquaculture Management'), ('SALMONID ENHANCEMENT', 'Salmonid Enhancement'), ('INTERNATIONAL ENGAGEMENT', 'International Engagement'), ('SMALL CRAFT HARBOURS', 'Small Craft Harbours'), ('CONSERVATION & PROTECTION', 'Conservation & Protection'), ('AIR SURVEILLANCE', 'Air Surveillance'), ('AQUATIC ANIMAL HEALTH', 'Aquatic Animal Health'), ('BIOTECHNOLOGY & GENOMICS', 'Biotechnology & Genomics'), ('AQUACULTURE SCIENCE', 'Aquaculture Science'), ('FISHERIES SCIENCE', 'Fisheries Science'), ('FISH AND SEAFOOD SECTOR', 'Fish and Seafood Sector'), ('FISH & FISH HABITAT PROT.', 'Fish & Fish Habitat Prot.'), ('AQUATIC INVASIVE SPECIES', 'Aquatic Invasive Species'), ('SPECIES AT RISK', 'Species at Risk'), ('MARINE PLANNING & CONSER.', 'Marine Planning & Conser.'), ('AQUATIC ECOSYSTEM SCIENCE', 'Aquatic Ecosystem Science'), ('OCEANS & CLIM. CHNG. SCI.', 'Oceans & Clim. Chng. Sci.'), ('WATERWAYS MANAGEMENT', 'Waterways Management'), ('ENVIRONMENTAL RESPONSE', 'Environmental Response'), ('UNKNOWN', 'Unknown'), ('N/A', 'Not applicable')], default=None, max_length=64, null=True, verbose_name='other DFO project link'),
        ),
        migrations.RemoveField(
            model_name='project',
            name='core_component',
        ),
        migrations.AddField(
            model_name='project',
            name='core_component',
            field=models.CharField(blank=True, choices=[('PLANNING', 'Planning'), ('FIELD WORK', 'Field Work'), ('SAMPLE PROCESSING', 'Sample Processing'), ('DATA ENTRY', 'Data Entry'), ('DATA ANALYSIS', 'Data Analysis'), ('REPORTING', 'Reporting')], max_length=32, verbose_name='core component'),
        ),
        migrations.AlterField(
            model_name='project',
            name='ecosystem_type',
            field=models.CharField(blank=True, choices=[('FRESHWATER', 'Freshwater'), ('ESTUARINE', 'Estuarine'), ('MARINE', 'Marine'), ('UNKNOWN', 'Unknown'), ('N/A', 'Not applicable'), ('OTHER', 'Other')], default=None, max_length=32, null=True, verbose_name='eco system type'),
        ),
        migrations.AlterField(
            model_name='project',
            name='government_organization',
            field=models.CharField(blank=True, choices=[('MUNICIPALITY', 'Municipality'), ('PROVINCE OF BRITISH COLUMBIA', 'Province of British Columbia'), ('YUKON TERRITORY', 'Yukon Territory'), ('ENVIRONMENT CANADA', 'Environment Canada'), ('CLIMATE CHANGE CANADA', 'Climate Change Canada'), ('ALASKA DEPARTMENT OF FISH & GAME', 'Alaska Department of Fish & Game'), ('WASHINGTON STATE', 'Washington State'), ('UNKNOWN', 'Unknown'), ('N/A', 'Not applicable'), ('OTHER', 'Other')], max_length=64, null=True, verbose_name='government organization'),
        ),
        migrations.AlterField(
            model_name='project',
            name='monitoring_approach',
            field=models.CharField(blank=True, choices=[('INDICATOR', 'Indicator'), ('INTENSIVE', 'Intensive'), ('EXTENSIVE', 'Extensive'), ('UNKNOWN', 'Unknown'), ('NOT APPLICABLE', 'Not applicable')], max_length=32, null=True, verbose_name='monitoring approach'),
        ),
        migrations.AlterField(
            model_name='project',
            name='primary_first_nations_contact_role',
            field=models.CharField(blank=True, choices=[('CHIEF', 'Chief'), ('BIOLOGIST', 'Biologist'), ('AQUATICS MANAGER', 'Aquatics Manager'), ('TECHNICIAN', 'Technician'), ('DIRECTOR', 'Director'), ('FISHERIES MANAGER', 'Fisheries Manager'), ('REFUGE MANAGER', 'Refuge Manager'), ('SCIENTIST', 'Scientist'), ('STEWARDSHIP DIRECTOR', 'Stewardship Director'), ('UNKNOWN', 'Unknown'), ('OTHER', 'Other')], default=None, max_length=32, null=True, verbose_name='primary first nations contact role'),
        ),
        migrations.AlterField(
            model_name='project',
            name='project_purpose',
            field=models.CharField(blank=True, choices=[('Biological', (('POPULATION ESTIMATES', 'Population Estimates'), ('RUN RECONSTRUCTION', 'Run Reconstruction'), ('BIOLOGICAL ABUNDANCE BENCHMARKS', 'Biological Abundance Benchmarks'), ('TERMINAL ABUNDANCE', 'Terminal Abundance'), ('IN-RIVER ABUNDANCE', 'In-River Abundance'), ('CATCH ESTIMATES', 'Catch Estimates'), ('SMOLT ABUNDANCE', 'Smolt Abundance'), ('ADULT ABUNDANCE', 'Adult Abundance'), ('ADMINISTRATION', 'Administration'), ('RECOVERY', 'Recovery'), ('REBUILDING', 'Rebuilding'), ('ENHANCEMENT', 'Enhancement'))), ('Catch/Fisheries', (('FOODS, SOCIAL AND CEREMONIAL FISHERIES', 'Foods, Social and Ceremonial Fisheries'), ('FRASER RECREATIONAL', 'Fraser Recreational'), ('FRASER ECONOMIC OPPORTUNITY (EO)', 'Fraser Economic Opportunity (EO)'), ('FRASER COMMERCIAL (IN-RIVER PORTIONS OF AREA', 'Fraser Commercial (in-river portions of Area'), ('29E (GILLNET) AND AREA 29B (SEINE)', '29E (Gillnet) and Area 29B (Seine)'), ('FRASER TEST FISHERIES (ALBION, QUALARK)', 'Fraser Test Fisheries (Albion, Qualark)'), ('MARINE FISHERIES', 'Marine Fisheries'), ('JUAN DE FUCA RECREATIONAL', 'Juan de Fuca Recreational'), ('WEST COAST VANCOUVER ISLAND RECREATIONAL', 'West Coast Vancouver Island Recreational'), ('NORTHERN BRITISH COLUMBIA RECREATIONAL', 'Northern British Columbia Recreational'), ('WEST COAST VANCOUVER ISLAND COMMERCIAL', 'West Coast Vancouver Island Commercial'), ('TROLL', 'Troll'), ('NORTHERN BC COMMERCIAL TROLL', 'Northern BC Commercial Troll'), ('TAAQ-WIIHAK', 'Taaq-wiihak'), ('FISH PASSAGE', 'Fish Passage'))), ('Habitat', (('WATER LEVELS', 'Water Levels'), ('RIPARIAN', 'Riparian'), ('ESTUARINE', 'Estuarine'), ('NEARSHORE & MARINE', 'Nearshore & Marine'), ('INSTREAM STRUCTURE', 'Instream Structure'), ('FLOODPLAIN CONNECTIVITY', 'Floodplain connectivity'), ('WATERSHED', 'Watershed'), ('NUTRIENT SUPPLEMENTATION', 'Nutrient Supplementation'), ('HABITAT CONDITION', 'Habitat Condition'), ('UNKNOWN', 'Unknown'), ('N/A', 'Not applicable'), ('OTHER', 'Other')))], max_length=64, null=True, verbose_name='project purpose'),
        ),
        migrations.RemoveField(
            model_name='project',
            name='project_sub_type',
        ),
        migrations.AddField(
            model_name='project',
            name='project_sub_type',
            field=models.CharField(blank=True, choices=[('RESEARCH & DEVELOPMENT', 'Research & Development'), ('MONITORING', 'Monitoring'), ('SAMPLING', 'Sampling'), ('RECOVERY', 'Recovery'), ('RESTORATION', 'Restoration'), ('DESIGN & FEASIBILITY', 'Design & Feasibility'), ('DECOMMISSIONING', 'Decommissioning'), ('IMPLEMENTATION', 'Implementation'), ('MAINTENANCE', 'Maintenance'), ('STEWARDSHIP', 'Stewardship'), ('RESEARCH & MONITORING', 'Research & Monitoring'), ('UNKNOWN', 'Unknown'), ('N/A', 'Not applicable')], default=None, max_length=32, verbose_name='project sub type'),
        ),
        migrations.RemoveField(
            model_name='project',
            name='project_theme',
        ),
        migrations.AddField(
            model_name='project',
            name='project_theme',
            field=models.CharField(blank=True, choices=[('ESCAPEMENT', 'Escapement'), ('CONSERVATION', 'Conservation'), ('CATCH (FIRST NATIONS)', 'Catch (First Nations)'), ('CATCH (RECREATIONAL)', 'Catch (Recreational)'), ('CATCH (COMMERCIAL)', 'Catch (Commercial)'), ('ENHANCEMENT', 'Enhancement'), ('ADMINISTRATION', 'Administration'), ('UNKNOWN', 'Unknown'), ('N/A', 'Not applicable')], default=None, max_length=32, verbose_name='project theme'),
        ),
        migrations.AlterField(
            model_name='project',
            name='project_type',
            field=models.CharField(blank=True, choices=[('POPULATION SCIENCE', 'Population Science'), ('HABITAT SCIENCE', 'Habitat Science')], default=None, max_length=64, null=True, verbose_name='project type'),
        ),
        migrations.AlterField(
            model_name='project',
            name='smu_name',
            field=models.CharField(blank=True, choices=[('BARKLEY/SOMASS SOCKEYE SALMON', 'Barkley/Somass Sockeye Salmon'), ('CHUM GENERAL', 'Chum general'), ('ECVI/MAINLAND INLET PINK SALMON', 'ECVI/Mainland Inlet Pink Salmon'), ('ECVI/MAINLAND INLET SOCKEYE SALMON', 'ECVI/Mainland Inlet Sockeye Salmon'), ('INNER SOUTH COAST CHUM SALMON', 'Inner South Coast Chum Salmon'), ('JST/MAINLAND INLET CHINOOK SALMON', 'JST/Mainland Inlet Chinook Salmon'), ('JST/MAINLAND INLETS COHO SALMON', 'JST/Mainland Inlets Coho Salmon'), ('LOWER STRAIT OF GEORGIA CHINOOK SALMON', 'Lower Strait of Georgia Chinook Salmon'), ('SOUTH COAST SOCKEYE GENERAL', 'South Coast Sockeye General'), ('STRAIT OF GEORGIA COHO SALMON', 'Strait of Georgia Coho Salmon'), ('UPPER STRAIT OF GEORGIA CHINOOK SALMON', 'Upper Strait of Georgia Chinook Salmon'), ('WCVI Chinook Salmon', 'WCVI Chinook Salmon'), ('WCVI CHUM SALMON', 'WCVI Chum Salmon'), ('WCVI COHO SALMON', 'WCVI Coho Salmon'), ('UNKNOWN', 'Unknown'), ('N/A', 'Not applicable'), ('OTHER', 'Other')], default=None, max_length=64, null=True, verbose_name='SMU name'),
        ),
        migrations.RemoveField(
            model_name='project',
            name='supportive_component',
        ),
        migrations.AddField(
            model_name='project',
            name='supportive_component',
            field=models.CharField(blank=True, choices=[('WORKSHOP', 'Workshop'), ('EVALUATION', 'Evaluation'), ('ASSESSMENT', 'Assessment'), ('COMMITTEE', 'Committee'), ('ADMINISTRATION', 'Administration'), ('TRAINING', 'Training'), ('STAFFING', 'Staffing'), ('MEETING', 'Meeting'), ('COMPUTER SUPPORT', 'Computer Support'), ('ADVICE & CONSULTATION', 'Advice & Consultation'), ('STUDY DESIGN', 'Study Design'), ('LITERATURE REVIEW', 'Literature Review'), ('EQUIPMENT SUPPORT', 'Equipment Support'), ('EQUIPMENT REPAIR/BUILDING', 'Equipment Repair/Building'), ('ANALYSIS OF CURRENT DATA', 'Analysis of Current Data'), ('ANALYSIS OF HISTORICAL DATA', 'Analysis of Historical Data'), ('Analysis - Other', 'Analysis - Other'), ('UNKNOWN', 'Unknown'), ('N/A', 'Not applicable')], max_length=64, verbose_name='supportive component'),
        ),
        migrations.AlterField(
            model_name='reports',
            name='report_timeline',
            field=models.CharField(blank=True, choices=[('PROGRESS REPORT', 'Progress Report'), ('FINAL REPORT', 'Final Report'), ('N/A', 'Not applicable'), ('OTHER', 'Other')], default=None, max_length=32, null=True, verbose_name='report timeline'),
        ),
        migrations.AlterField(
            model_name='reports',
            name='report_type',
            field=models.CharField(blank=True, choices=[('PROJECT', 'Project'), ('CATCH', 'Catch'), ('POPULATION', 'Population'), ('SAMPLING', 'Sampling'), ('METHODS', 'Sampling'), ('HABITAT', 'Habitat'), ('RECOVERY', 'Recovery'), ('ENHANCEMENT', 'Enhancement'), ('R&D', 'R&D'), ('ADMINISTRATION', 'Administration')], default=None, max_length=32, null=True, verbose_name='report type'),
        ),
        migrations.AddField(
            model_name='objectiveoutcome',
            name='objective',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='objective_outcome', to='spot.objective', verbose_name='objective'),
        ),
        migrations.AddField(
            model_name='objectiveoutcome',
            name='report_reference',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='objective_outcome', to='spot.reports', verbose_name='report reference'),
        ),
    ]
