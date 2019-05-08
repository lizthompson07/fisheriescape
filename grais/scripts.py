from .import models


def resave_all():
    for obj in models.GCSample.objects.all():
        obj.save()

def reconcile_spp():
    '''do not run this twice!!! I am greying out for safe-keeping'''
    # trap_id, number_to_add, species_id
    # crab_list = [
    #     [1501, 3, 26, ],
    #     [1499, 3, 26, ],
    #     [1295, 6, 26, ],
    #     [1278, 16, 26, ],
    #     [1296, 17, 26, ],
    #     [1323, 18, 26, ],
    #     [1283, 23, 26, ],
    #     [1351, 26, 26, ],
    #     [1317, 35, 26, ],
    #     [1294, 36, 26, ],
    #     [1324, 44, 26, ],
    #     [1259, 75, 26, ],
    #     [1190, 2, 27, ],
    #     [985, 1, 98, ],
    #     [1038, 1, 98, ],
    #     [1045, 1, 98, ],
    #     [1058, 1, 98, ],
    #     [1173, 1, 98, ],
    #     [1361, 1, 98, ],
    #     [930, 2, 98, ],
    #     [938, 2, 98, ],
    #     [970, 2, 98, ],
    #     [983, 2, 98, ],
    #     [1094, 2, 98, ],
    #     [1015, 4, 98, ],
    #     [1201, 4, 98, ],
    #     [1221, 4, 98, ],
    #     [1165, 5, 98, ],
    #     [1386, 5, 98, ],
    #     [1054, 6, 98, ],
    #     [1047, 7, 98, ],
    #     [1138, 7, 98, ],
    #     [1043, 8, 98, ],
    #     [1381, 8, 98, ],
    #     [966, 9, 98, ],
    #     [1142, 10, 98, ],
    #     [1213, 10, 98, ],
    #     [1370, 10, 98, ],
    #     [1385, 10, 98, ],
    #     [1025, 11, 98, ],
    #     [1149, 11, 98, ],
    #     [1374, 11, 98, ],
    #     [1011, 12, 98, ],
    #     [1022, 18, 98, ],
    #
    # ]
    # for crab in crab_list:
    #     my_trap = models.Trap.objects.get(pk=crab[0])
    #     number_to_add = crab[1]
    #     for i in range(0, number_to_add):
    #         print("adding species {} to trap {}".format(crab[2], crab[0]))
    #         my_crab = models.Crab.objects.create(trap=my_trap, species_id=crab[2])
    #         my_crab.save()
    pass



