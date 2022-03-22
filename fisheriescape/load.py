# To use this file:
# python manage.py shell
# from fisheriescape import load
# load.run()
# exit()

import os
from django.contrib.gis.utils import LayerMapping
from .models import FisheryArea, Hexagon, Score, NAFOArea

# For NAFO_subzones.shp
# mapping = {
#     'layer_id': 'layer_id',
#     'name': 'ZONE',
#     'polygon': 'MULTIPOLYGON',
# }
#
# nafo_shp = os.path.abspath(
#     os.path.join(os.path.dirname(__file__), 'data', 'NAFO_subzones.shp'),
# )
#
#
# def run(verbose=True):
#     lm = LayerMapping(NAFOArea, nafo_shp, mapping, transform=False)
#     lm.save(strict=True, verbose=verbose)

# For Snow Crab.shp
# mapping = {
#     'layer_id': 'Fishery',
#     'name': 'Area',
#     'polygon': 'MULTIPOLYGON',
# }
#
# crab_shp = os.path.abspath(
#     os.path.join(os.path.dirname(__file__), 'data', 'Snow Crab.shp'),
# )
#
#
# def run(verbose=True):
#     lm = LayerMapping(FisheryArea, crab_shp, mapping, transform=False)
#     lm.save(strict=True, verbose=verbose)

## For Lobster.shp
mapping = {
    'layer_id': 'Fishery',
    'name': 'Area',
    'polygon': 'MULTIPOLYGON',
}

lobster_shp = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'data', 'Lobster.shp'),
)


def run(verbose=True):
    lm = LayerMapping(FisheryArea, lobster_shp, mapping, transform=False)
    lm.save(strict=True, verbose=verbose)

## For hexagons
# mapping = {
#     'grid_id': 'grid_id',
#     'polygon': 'MULTIPOLYGON',
# }
#
# hexagon_shp = os.path.abspath(
#     os.path.join(os.path.dirname(__file__), 'data', 'hexagon_test_transformed.shp'),
# )
#
#
# def run(verbose=True):
#     lm = LayerMapping(Hexagon, hexagon_shp, mapping, transform=False)
#     lm.save(strict=True, verbose=verbose)

# ## For hexagon scores from a shapefile
# mapping = {
#     'hexagon': {'grid_id': 'grid_id'},
#     'species': {'english_name': 'species'},
#     'week': {'week_number': 'week'},
#     'site_score': 'mean_score',
# }
#
# site_score_shp = os.path.abspath(
#     os.path.join(os.path.dirname(__file__), 'data', 'site_score_test.shp'),
# )
#
#
# def run(verbose=True):
#     lm = LayerMapping(Score, site_score_shp, mapping, transform=False)
#     lm.save(strict=True, verbose=verbose)