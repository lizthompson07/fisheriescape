import os
import json

from django.core import serializers

from bio_diversity import models


def export_fixtures(models_to_export, output_path=None):
    """ a simple function to export the important lookup tables. These fixtures will be used for testing and also for
    seeding new instances"""
    if not output_path:
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')
        if not os.path.isdir(output_path):
            os.mkdir(output_path)

    open(output_path, 'w').close()
    for model in models_to_export:
        data = serializers.serialize("json", model.objects.all())
        parsed = json.loads(data)
        f = open(output_path, 'a', encoding='utf-8')
        f.write(json.dumps(parsed, indent=4, sort_keys=True))
        f.close()


fixture_file = r'./bio_diversity/fixtures/initial_data.json'

model_export = [models.AnimalDetCode,
                models.AniDetSubjCode,
                models.Collection,
                models.CountCode,
                models.Cup,
                models.Drawer,
                models.EnvCode,
                models.EnvSubjCode,
                models.EnvTreatCode,
                models.EventCode,
                models.EventFileCode,
                models.FacilityCode,
                models.FeedCode,
                models.FeedMethod,
                models.HeathUnit,
                models.HelpText,
                models.ImageCode,
                models.IndTreatCode,
                models.Instrument,
                models.InstrumentCode,
                models.InstDetCode,
                models.LocCode,
                models.LocationDetCode,
                models.LocDetSubjCode,
                models.Organization,
                models.PersonnelCode,
                models.PriorityCode,
                models.Program,
                models.ProgAuthority,
                models.Protocol,
                models.ProtoCode,
                models.QualCode,
                models.ReleaseSiteCode,
                models.RiverCode,
                models.RoleCode,
                models.SampleCode,
                models.SpawnDetCode,
                models.SpawnDetSubjCode,
                models.SpeciesCode,
                models.StockCode,
                models.SubRiverCode,
                models.Tank,
                models.Tray,
                models.Trough,
                models.Tributary,
                models.UnitCode,
                ]


from bio_diversity.scripts import *
export_fixtures(model_export, fixture_file)
