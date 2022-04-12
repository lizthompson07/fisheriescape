# To use this file:
# python manage.py shell
# from fisheriescape import load
# load.run()
# exit()

import os
from django.contrib.gis.utils import LayerMapping
from .models import FisheryArea, Hexagon, Score, NAFOArea

# # For NAFO_select.shp
# mapping = {
#     'layer_id': 'layer_id',
#     'name': 'Area',
#     'polygon': 'MULTIPOLYGON',
# }
#
# nafo_select_shp = os.path.abspath(
#     os.path.join(os.path.dirname(__file__), 'data', 'NAFO_select.shp'),
# )
#
#
# def run(verbose=True):
#     lm = LayerMapping(NAFOArea, nafo_select_shp, mapping, transform=False)
#     lm.save(strict=True, verbose=verbose)
#

# # For NAFO_subzones.shp
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
#     lm = LayerMapping(FisheryArea, nafo_shp, mapping, transform=False)
#     lm.save(strict=True, verbose=verbose)

# # For Snow Crab.shp
# mapping = {
#     'layer_id': 'Fishery',
#     'name': 'AreaID',
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

# ## For Lobster.shp
# mapping = {
#     'layer_id': 'Fishery',
#     'name': 'AreaID',
#     'polygon': 'MULTIPOLYGON',
# }
#
# lobster_shp = os.path.abspath(
#     os.path.join(os.path.dirname(__file__), 'data', 'Lobster.shp'),
# )
#
#
# def run(verbose=True):
#     lm = LayerMapping(FisheryArea, lobster_shp, mapping, transform=False)
#     lm.save(strict=True, verbose=verbose)

# ## For Groundfish.shp
# mapping = {
#     'layer_id': 'Fishery',
#     'name': 'AreaID',
#     'polygon': 'MULTIPOLYGON',
# }
#
# groundfish_shp = os.path.abspath(
#     os.path.join(os.path.dirname(__file__), 'data', 'Groundfish.shp'),
# )
#
#
# def run(verbose=True):
#     lm = LayerMapping(FisheryArea, groundfish_shp, mapping, transform=False)
#     lm.save(strict=True, verbose=verbose)

# ## For Herring.shp
# mapping = {
#     'layer_id': 'Fishery',
#     'name': 'AreaID',
#     'polygon': 'MULTIPOLYGON',
# }
#
# herring_shp = os.path.abspath(
#     os.path.join(os.path.dirname(__file__), 'data', 'Herring.shp'),
# )
#
#
# def run(verbose=True):
#     lm = LayerMapping(FisheryArea, herring_shp, mapping, transform=False)
#     lm.save(strict=True, verbose=verbose)

# # For hexagons
# mapping = {
#     'grid_id': 'GRID_ID',
#     'polygon': 'MULTIPOLYGON',
# }
#
# hexagon_shp = os.path.abspath(
#     os.path.join(os.path.dirname(__file__), 'data', 'Master_Grid_4T.shp'),
# )
#
#
# def run(verbose=True):
#     lm = LayerMapping(Hexagon, hexagon_shp, mapping, transform=False)
#     lm.save(strict=True, verbose=verbose)

## For hexagon scores from a shapefile
# mapping = {
#     'hexagon': {'grid_id': 'grid_id'},
#     'species': {'english_name': 'species'},
#     'week': {'week_number': 'week'},
#     'site_score': 'ss',
#     'ceu_score': 'ceu',
#     'fs_score': 'fs',
# }
#
# site_score_shp = os.path.abspath(
#     os.path.join(os.path.dirname(__file__), 'data', 'FALL HERRING FINAL DF.shp'),
# )
#
#
# def run(verbose=True):
#     lm = LayerMapping(Score, site_score_shp, mapping, transform=False)
#     lm.save(strict=True, verbose=verbose)
