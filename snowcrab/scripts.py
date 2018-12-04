from . import models


def convert_lat_long():
    sets = models.Set.objects.all()
    for set in sets:
        run_save = False
        fields = [
            "latitude_start_logbook",
            "latitude_end_logbook",
            "longitude_start_logbook",
            "longitude_end_logbook",
        ]

        for field in fields:
            my_coord = str(getattr(set, field)).split(".")[0]
            if len(my_coord) > 2:
                new_val = int(my_coord[:2]) + float("{}.{}".format(my_coord[2:4],my_coord[4:7]))/60
                setattr(set, field, new_val)
                run_save = True
            elif my_coord.startswith("6"):
                setattr(set, field, -getattr(set, field))
                run_save = True

        if run_save:
            set.save()


