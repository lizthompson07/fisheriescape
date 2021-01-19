import os
from django.contrib.gis.utils import LayerMapping
from .models import FisheryArea

mapping = {
    'id': 'OBJECTID',
    'name': 'LFA',
    'polygon': 'MULTIPOLYGON',
}

lobster_shp = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'data', 'lobster_polygons.shp'),
)


def run(verbose=True):
    lm = LayerMapping(FisheryArea, lobster_shp, mapping, transform=False)
    lm.save(strict=True, verbose=verbose)
