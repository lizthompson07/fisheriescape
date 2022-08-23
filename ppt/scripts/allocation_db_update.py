from django.db import transaction

from ppt import models


def allocation_mover():
    return 0
    with transaction.atomic():
        for rev in models.Review.objects.all():
            if rev.allocated_budget:
                # check if any amount are already allocated:
                if rev.project_year.allocations:
                    pass
                else:
                    alloc_obj = models.OMAllocation(
                        project_year=rev.project_year,
                        amount=rev.allocated_budget,
                        funding_source=rev.project_year.project.default_funding_source
                    )
                    alloc_obj.clean()
                    alloc_obj.save()
    return 0
