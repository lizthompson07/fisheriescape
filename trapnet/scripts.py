from . import models
from shared_models import models as shared_models


def population_parents():
    for river in shared_models.River.objects.all():
        if river.parent_cgndb_id:
            # get the river, if it exists
            try:
                parent_river = shared_models.River.objects.get(cgndb=river.parent_cgndb_id)
            except shared_models.River.DoesNotExist:
                pass
            else:
                river.parent_river = parent_river
                river.save()

