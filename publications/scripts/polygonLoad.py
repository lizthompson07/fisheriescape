from publications import models


def rename_remove_geoscope(src_name, dest_name):
    print("Updating " + src_name)
    try:
        bb_geo = models.GeographicScope.objects.get(name=src_name)
        nbb_geo = models.GeographicScope.objects.get(name=dest_name)
        projects = models.Project.objects.filter(geographic_scope=bb_geo)

        print("updating projects: ")
        print(projects)

        for proj in projects:
            proj.geographic_scope.remove(bb_geo)
            proj.geographic_scope.add(nbb_geo)
            proj.save()

        try:
            bb_poly = models.Polygon.objects.filter(geoscope=bb_geo)
            print("deleting polygons: ")
            print(bb_poly)
            for p in bb_poly:
                p.delete()
        except models.Polygon.DoesNotExist:
            print("No polygon, no problem")

        print("deleting geoscope: " + str(bb_geo))
        bb_geo.delete()
    except models.GeographicScope.DoesNotExist:
        print("BANQUEREAU was already removed")


scope_names = [scope.name for scope in models.GeographicScope.objects.all()]

input_file_name = 'publications/scripts/data/polygons.csv'
file = open(file=input_file_name, mode='r', encoding='UTF-8')

lines = file.readlines()
lines.pop(0)
polygons = [line.strip('\n').split(", ") for line in lines]
for poly in polygons:
    if not poly[0] in scope_names:
        gs = models.GeographicScope(name=poly[0].upper())
        gs.save()

        models.Polygon(geoscope=gs, order=1, latitude=poly[3], longitude=poly[2]).save()
        models.Polygon(geoscope=gs, order=1, latitude=poly[4], longitude=poly[2]).save()
        models.Polygon(geoscope=gs, order=1, latitude=poly[4], longitude=poly[1]).save()
        models.Polygon(geoscope=gs, order=1, latitude=poly[3], longitude=poly[1]).save()

        polygone = models.Polygon.objects.filter(geoscope=gs)
        print(poly[0] + ": " + str(polygone))
    else:
        print("found: " + str(poly[0]))
        scope = models.GeographicScope.objects.get(name=poly[0])
        polygon = models.Polygon.objects.filter(geoscope=scope)
        if not polygon:
            print("adding: " + poly[0])
            models.Polygon(geoscope=scope, order=1, latitude=poly[3], longitude=poly[2]).save()
            models.Polygon(geoscope=scope, order=1, latitude=poly[4], longitude=poly[2]).save()
            models.Polygon(geoscope=scope, order=1, latitude=poly[4], longitude=poly[1]).save()
            models.Polygon(geoscope=scope, order=1, latitude=poly[3], longitude=poly[1]).save()
        else:
            print(str(poly))
            print(str(polygon))

# BANQUEREAU BANK: <QuerySet [<Polygon: 1: [-57.249, 43.897]>, <Polygon: 1: [-57.249, 45.131]>, <Polygon: 1: [-60.13, 45.131]>, <Polygon: 1: [-60.13, 43.897]>]>
rename_remove_geoscope(src_name="BANQUEREAU", dest_name="BANQUEREAU BANK")

# HAY ISLAND: <QuerySet [<Polygon: 1: [-59.668, 46.008]>, <Polygon: 1: [-59.668, 46.032]>, <Polygon: 1: [-59.703, 46.032]>, <Polygon: 1: [-59.703, 46.008]>]>
rename_remove_geoscope(src_name="HAY", dest_name="HAY ISLAND")

# SABLE ISLAND: <QuerySet [<Polygon: 1: [-59.657, 43.879]>, <Polygon: 1: [-59.657, 44.046]>, <Polygon: 1: [-60.16, 44.046]>, <Polygon: 1: [-60.16, 43.879]>]>
rename_remove_geoscope(src_name="SABLE", dest_name="SABLE ISLAND")

# CONTINENTAL SHELF(US MIDATLANTIC COAST): <QuerySet [<Polygon: 1: [-68.659, 30.013]>, <Polygon: 1: [-68.659, 41.831]>, <Polygon: 1: [-81.373, 41.831]>, <Polygon: 1: [-81.373, 30.013]>]>
rename_remove_geoscope(src_name="CONTINENTAL SHELF OFF THE MIDATLANTIC COAST OF THE USA", dest_name="CONTINENTAL SHELF(US MIDATLANTIC COAST)")

# LAKES IN THE UPPER PETITE RIVIÈRE WATERSHED: <QuerySet [<Polygon: 1: [-64.52, 44.229]>, <Polygon: 1: [-64.52, 44.368]>, <Polygon: 1: [-64.664, 44.368]>, <Polygon: 1: [-64.664, 44.229]>]>
rename_remove_geoscope(src_name="LAKES IN THE UPPER PETITE RIVIÈRE WATERSHED IN SOUTHWEST NOVA SCOTIA", dest_name="LAKES IN THE UPPER PETITE RIVIÈRE WATERSHED")

# NFLD: <QuerySet [<Polygon: 1: [-51.7, 46.4]>, <Polygon: 1: [-51.7, 51.786]>, <Polygon: 1: [-59.6, 51.786]>, <Polygon: 1: [-59.6, 46.4]>]>

rename_remove_geoscope(src_name="NEWFOUNDLAND", dest_name="NFLD")

nnfld = models.GeographicScope.objects.get(name="NFLD")
nnfld.name = "NEWFOUNDLAND"
nnfld.save()

