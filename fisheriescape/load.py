# To use this file:
# python manage.py shell
# from fisheriescape import load
# load.run()
# exit()

import os

from django.contrib.gis.utils import LayerMapping

from .models import FisheryArea, Hexagon, Score, NAFOArea

# For NAFO_select.shp
nafo_select_shp_mapping = {
    'layer_id': 'layer_id',
    'name': 'Area',
    'polygon': 'MULTIPOLYGON',
}

nafo_select_shp = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'data', 'NAFO_select.shp'),
)


def nafo_select_shp_run(verbose=True):
    lm = LayerMapping(NAFOArea, nafo_select_shp, nafo_select_shp_mapping, transform=False)
    lm.save(strict=True, verbose=verbose)


# For NAFO_subzones.shp
nafo_shp_mapping = {
    'layer_id': 'layer_id',
    'name': 'ZONE',
    'polygon': 'MULTIPOLYGON',
}

nafo_shp = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'data', 'NAFO_subzones.shp'),
)


def nafo_shp_run(verbose=True):
    lm = LayerMapping(FisheryArea, nafo_shp, nafo_shp_mapping, transform=False)
    lm.save(strict=True, verbose=verbose)


# For Snow Crab.shp
crab_shp_mapping = {
    'layer_id': 'Fishery',
    'name': 'AreaID',
    'polygon': 'MULTIPOLYGON',
}

crab_shp = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'data', 'Snow Crab.shp'),
)


def crab_shp_run(verbose=True):
    lm = LayerMapping(FisheryArea, crab_shp, crab_shp_mapping, transform=False)
    lm.save(strict=True, verbose=verbose)


## For Lobster.shp
lobster_shp_mapping = {
    'layer_id': 'Fishery',
    'name': 'AreaID',
    'polygon': 'MULTIPOLYGON',
}

lobster_shp = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'data', 'Lobster.shp'),
)


def lobster_shp_run(verbose=True):
    lm = LayerMapping(FisheryArea, lobster_shp, lobster_shp_mapping, transform=False)
    lm.save(strict=True, verbose=verbose)


## For Groundfish.shp
groundfish_shp_mapping = {
    'layer_id': 'Fishery',
    'name': 'AreaID',
    'polygon': 'MULTIPOLYGON',
}

groundfish_shp = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'data', 'Groundfish.shp'),
)


def groundfish_shp_run(verbose=True):
    lm = LayerMapping(FisheryArea, groundfish_shp, groundfish_shp_mapping, transform=False)
    lm.save(strict=True, verbose=verbose)


## For Herring.shp
herring_shp_mapping = {
    'layer_id': 'Fishery',
    'name': 'AreaID',
    'polygon': 'MULTIPOLYGON',
}

herring_shp = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'data', 'Herring.shp'),
)


def herring_shp_run(verbose=True):
    lm = LayerMapping(FisheryArea, herring_shp, herring_shp_mapping, transform=False)
    lm.save(strict=True, verbose=verbose)


# For hexagons
hexagon_shp_mapping = {
    'grid_id': 'GRID_ID',
    'polygon': 'MULTIPOLYGON',
}

hexagon_shp = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'data', 'Master_Grid_4T.shp'),
)


def hexagon_shp_run(verbose=True):
    lm = LayerMapping(Hexagon, hexagon_shp, hexagon_shp_mapping, transform=False)
    lm.save(strict=True, verbose=verbose)


# For hexagon scores from a shapefile
site_score_shp_mapping = {
    'hexagon': {'grid_id': 'grid_id'},
    'species': {'english_name': 'species'},
    'week': {'week_number': 'week'},
    'site_score': 'ss',
    'ceu_score': 'ceu',
    'fs_score': 'fs',
}

site_score_shp = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'data', 'FALL HERRING FINAL DF.shp'),
)


def site_score_shp_run(verbose=True):
    lm = LayerMapping(Score, site_score_shp, site_score_shp_mapping, transform=False)
    lm.save(strict=True, verbose=verbose)


def run():
    try:
        print('Import nafo_select_shp ...')
        nafo_select_shp_run()
        print('✅ nafo_select_shp imported')
    except Exception as e:
        print(f'❌ nafo_select_shp import failed : {e}')

    try:
        print('Import nafo_shp ...')
        nafo_shp_run()
        print('✅ nafo_shp imported')
    except Exception as e:
        print(f'❌ nafo_shp import failed : {e}')

    try:
        print('Import crab_shp ...')
        crab_shp_run()
        print('✅ crab_shp imported')
    except Exception as e:
        print(f'❌ crab_shp import failed : {e}')

    try:
        print('Import lobster_shp ...')
        lobster_shp_run()
        print('✅ lobster_shp imported')
    except Exception as e:
        print(f'❌ lobster_shp import failed : {e}')

    try:
        print('Import groundfish_shp ...')
        groundfish_shp_run()
        print('✅ groundfish_shp imported')
    except Exception as e:
        print(f'❌ groundfish_shp import failed : {e}')

    try:
        print('Import herring_shp ...')
        herring_shp_run()
        print('✅ herring_shp imported')
    except Exception as e:
        print(f'❌ herring_shp import failed : {e}')


    try:
        print('Import hexagon_shp ...')
        hexagon_shp_run()
        print('✅ hexagon_shp imported')
    except Exception as e:
        print(f'❌ hexagon_shp import failed : {e}')

    try:
        print('Import site_score_shp ...')
        site_score_shp_run()
        print('✅ site_score_shp imported')
    except Exception as e:
        print(f'❌ site_score_shp import failed : {e}')
