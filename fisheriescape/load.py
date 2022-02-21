# To use this file:
# python manage.py shell
# from fisheriescape import load
# load.run()
# exit()

import os
from django.contrib.gis.utils import LayerMapping
from .models import FisheryArea, Hexagon, Score

# For NAFO.shp
# mapping = {
#     'layer_id': 'Layer_id',
#     'name': 'ZONE',
#     'polygon': 'MULTIPOLYGON',
# }
#
# nafo_shp = os.path.abspath(
#     os.path.join(os.path.dirname(__file__), 'data', 'NAFO_Atlantic.shp'),
# )
#
#
# def run(verbose=True):
#     lm = LayerMapping(FisheryArea, nafo_shp, mapping, transform=False)
#     lm.save(strict=True, verbose=verbose)


# For SnowCrab_polygons.shp
# mapping = {
#     'layer_id': 'Layer_id',
#     'name': 'ZONE_1',
#     'polygon': 'MULTIPOLYGON',
# }
#
# crab_shp = os.path.abspath(
#     os.path.join(os.path.dirname(__file__), 'data', 'SnowCrab_polygons.shp'),
# )
#
#
# def run(verbose=True):
#     lm = LayerMapping(FisheryArea, crab_shp, mapping, transform=False)
#     lm.save(strict=True, verbose=verbose)

## For Lobster_polygons.shp
# mapping = {
#     'layer_id': 'Layer_id',
#     'name': 'LFA',
#     'polygon': 'MULTIPOLYGON',
# }
#
# lobster_shp = os.path.abspath(
#     os.path.join(os.path.dirname(__file__), 'data', 'Lobster_polygons.shp'),
# )
#
#
# def run(verbose=True):
#     lm = LayerMapping(FisheryArea, lobster_shp, mapping, transform=False)
#     lm.save(strict=True, verbose=verbose)

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

## For hexagon scores from a shapefile
mapping = {
    'hexagon': {'grid_id': 'grid_id'},
    'species': {'english_name': 'species'},
    'week': {'week_number': 'week'},
    'site_score': 'mean_score',
}

site_score_shp = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'data', 'site_score_test.shp'),
)


def run(verbose=True):
    lm = LayerMapping(Score, site_score_shp, mapping, transform=False)
    lm.save(strict=True, verbose=verbose)
