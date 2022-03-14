import os
from datetime import datetime, timedelta

from django.test import tag
from faker import Faker

from bio_diversity.test import BioFactoryFloor
from bio_diversity import utils
from django.test import TestCase
from random import randint


faker = Faker()

fixtures_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fixtures')
standard_fixtures = [file for file in os.listdir(fixtures_dir)]


def setup_view(view, request, *args, **kwargs):
    view.request = request
    view.args = args
    view.kwargs = kwargs
    return view


@tag("Grp", "Move", "Utils")
class TestGrpMove(TestCase):
    fixtures = ["initial_data.json"]

    def setUp(self):
        super().setUp()  # used to import fixtures

        # create group, tank and evnt
        self.grp = BioFactoryFloor.GrpFactory()
        self.evnt = BioFactoryFloor.EvntFactory()
        self.tank = BioFactoryFloor.TankFactory()
        self.tank.facic_id = self.evnt.facic_id
        self.tank.save()
        self.move_date = utils.naive_to_aware(datetime.now().date())
        self.final_tank = BioFactoryFloor.TankFactory()
        self.final_tank.facic_id = self.evnt.facic_id
        self.final_tank.save()
        self.cleaned_data = {
            "facic_id": self.evnt.facic_id,
            "evnt_id": self.evnt,
            "created_by": self.evnt.created_by,
            "created_date": self.evnt.created_date,
        }

    def test_grp_in_cont(self):
        # test a group with a moveDet is in one and only one tank:
        utils.enter_move(self.cleaned_data, None, self.tank, self.move_date, grp_pk=self.grp.pk)
        self.assertEqual(self.grp.current_cont()[0], self.tank)
        self.assertEqual(len(self.grp.current_cont()), 1)

    def test_cont_has_grp(self):
        # test a tank with a moveDet has one and only one group in it:
        utils.enter_move(self.cleaned_data, None, self.tank, self.move_date, grp_pk=self.grp.pk)
        indv_list, grp_list = self.tank.fish_in_cont()
        self.assertEqual(len(grp_list), 1)
        self.assertIn(self.grp, grp_list)

    def test_move_grp(self):
        # grp in one tank, gets moved, is in second tank and not in first tank
        utils.enter_move(self.cleaned_data, None, self.tank, self.move_date, grp_pk=self.grp.pk)
        indv_list, grp_list = self.tank.fish_in_cont()
        self.assertIn(self.grp, grp_list)
        utils.enter_move(self.cleaned_data, self.tank, self.final_tank, self.move_date, grp_pk=self.grp.pk)
        indv_list, grp_list = self.tank.fish_in_cont()
        self.assertNotIn(self.grp, grp_list)
        indv_list, grp_list = self.final_tank.fish_in_cont()
        self.assertIn(self.grp, grp_list)

    def test_two_grps_one_tank(self):
        #  put two grps into a single tank, make sure both are located:
        second_grp = BioFactoryFloor.GrpFactory()
        utils.enter_move(self.cleaned_data, None, self.tank, self.move_date, grp_pk=self.grp.pk)
        utils.enter_move(self.cleaned_data, None, self.tank, self.move_date, grp_pk=second_grp.pk)
        indv_list, grp_list = self.tank.fish_in_cont()
        self.assertEqual(len(grp_list), 2)
        self.assertIn(self.grp, grp_list)
        self.assertIn(second_grp, grp_list)

    def test_fix_jumped_tanks(self):
        # simulate accidentally recording group in wrong tank and correcting:
        # ie A->B, C->D (fish is in both B and D) ->E should correct this
        tank_a = BioFactoryFloor.TankFactory(name="A")
        tank_a.facic_id = self.evnt.facic_id
        tank_a.save()
        tank_b = BioFactoryFloor.TankFactory(name="B")
        tank_b.facic_id = self.evnt.facic_id
        tank_b.save()
        tank_c = BioFactoryFloor.TankFactory(name="C")
        tank_c.facic_id = self.evnt.facic_id
        tank_c.save()
        tank_d = BioFactoryFloor.TankFactory(name="D")
        tank_d.facic_id = self.evnt.facic_id
        tank_d.save()
        tank_e = BioFactoryFloor.TankFactory(name="E")
        tank_e.facic_id = self.evnt.facic_id
        tank_e.save()
        # need three dates to ensure unique moving events, to keep django test env happy
        move_a_date = (datetime.now() - timedelta(days=2)).date()
        move_b_date = (datetime.now() - timedelta(days=1)).date()
        move_c_date = datetime.now().date()

        utils.enter_move(self.cleaned_data, tank_a, tank_b, move_a_date, grp_pk=self.grp.pk)
        utils.enter_move(self.cleaned_data, tank_c, tank_d, move_b_date, grp_pk=self.grp.pk)
        self.assertIn(tank_b, self.grp.current_cont())
        self.assertIn(tank_d, self.grp.current_cont())
        utils.enter_move(self.cleaned_data, None, tank_e, move_c_date, grp_pk=self.grp.pk)
        self.assertIn(tank_e, self.grp.current_cont())
        self.assertNotIn(tank_c, self.grp.current_cont())
        self.assertNotIn(tank_d, self.grp.current_cont())

    def test_origin_only_tank(self):
        #  move group with only origin, make sure group is still in original tank
        utils.enter_move(self.cleaned_data, None, self.tank, self.move_date, grp_pk=self.grp.pk)
        utils.enter_move(self.cleaned_data, self.tank, None, self.move_date, grp_pk=self.grp.pk)
        indv_list, grp_list = self.tank.fish_in_cont()
        self.assertIn(self.grp, grp_list)

    def test_origin_destination_tank(self):
        #  move group with origin == destination, make sure group is in original tank:
        utils.enter_move(self.cleaned_data, None, self.tank, self.move_date, grp_pk=self.grp.pk)
        utils.enter_move(self.cleaned_data, self.tank, self.tank, self.move_date, grp_pk=self.grp.pk)

        indv_list, grp_list = self.tank.fish_in_cont()
        self.assertIn(self.grp, grp_list)


@tag("Grp", "Move", "Cnt", "Utils")
class TestGrpMoveCnt(TestCase):
    fixtures = ["initial_data.json"]

    def setUp(self):
        super().setUp()  # used to import fixtures

        # create group, tank and evnt
        self.grp = BioFactoryFloor.GrpFactory()
        self.final_grp = BioFactoryFloor.GrpFactory()
        self.evnt = BioFactoryFloor.EvntFactory()
        self.tank = BioFactoryFloor.TankFactory()
        self.tank.facic_id = self.evnt.facic_id
        self.tank.save()
        self.move_date = utils.naive_to_aware(datetime.now().date())
        self.final_tank = BioFactoryFloor.TankFactory()
        self.final_tank.facic_id = self.evnt.facic_id
        self.final_tank.save()
        self.cleaned_data = {
            "facic_id": self.evnt.facic_id,
            "evnt_id": self.evnt,
            "created_by": self.evnt.created_by,
            "created_date": self.evnt.created_date,
        }

    def test_whole_grp(self):
        # Move whole group, record count:
        cnt_val = randint(0, 100)
        utils.enter_move_cnts(self.cleaned_data, self.tank, self.final_tank, self.move_date, nfish=cnt_val,
                              start_grp_id=self.grp, whole_grp=True)
        self.assertEqual(self.grp.count_fish_in_group(), cnt_val)

    def test_partial_grp(self):
        # Move partial group, record counts:
        cnt_val = randint(0, 100)
        start_cnt, end_cnt, data_entered = utils.enter_move_cnts(self.cleaned_data, self.tank, self.final_tank, self.move_date, nfish=cnt_val,
                                                                 start_grp_id=self.grp, whole_grp=False)
        end_grp = end_cnt.anix_id.grp_id
        self.assertEqual(self.grp.count_fish_in_group(), -cnt_val)  # fish taken out of this group
        self.assertEqual(end_grp.count_fish_in_group(), cnt_val)

    def test_whole_grp_with_end_grp(self):
        # Move whole group into new end group. record counts, make sure original group is invalid:
        cnt_val = randint(0, 100)
        utils.enter_move_cnts(self.cleaned_data, self.tank, self.final_tank, self.move_date, nfish=cnt_val,
                              start_grp_id=self.grp, end_grp_id=self.final_grp, whole_grp=True)
        self.assertEqual(self.grp.grp_end_date, self.move_date)
        self.assertEqual(self.final_grp.count_fish_in_group(), cnt_val)

    def test_partial_grp_with_end_grp(self):
        # Move partial group into new group, record counts:
        cnt_val = randint(0, 100)
        utils.enter_move_cnts(self.cleaned_data, self.tank, self.final_tank, self.move_date, nfish=cnt_val,
                              start_grp_id=self.grp, end_grp_id=self.final_grp, whole_grp=False)
        self.assertEqual(self.grp.count_fish_in_group(), -cnt_val)  # fish taken out of this group
        self.assertEqual(self.final_grp.count_fish_in_group(), cnt_val)


@tag("Grp", "Cnt", "Utils")
class TestGrpCnt(TestCase):
    fixtures = ["initial_data.json"]

    def setUp(self):
        super().setUp()  # used to import fixtures

        # create group, put them in a tank:
        self.grp = BioFactoryFloor.GrpFactory()
        self.evnt = BioFactoryFloor.EvntFactory()
        self.tank = BioFactoryFloor.TankFactory()
        self.tank.facic_id = self.evnt.facic_id
        self.tank.save()
        self.final_tank = BioFactoryFloor.TankFactory()
        self.final_tank.facic_id = self.evnt.facic_id
        self.final_tank.save()
        self.cleaned_data = {
            "facic_id": self.evnt.facic_id,
            "evnt_id": self.evnt,
            "created_by": self.evnt.created_by,
            "created_date": self.evnt.created_date,
        }
        self.anix, self.contx, data_entered = utils.enter_contx(self.tank, self.cleaned_data, grp_pk=self.grp.pk,
                                                                final_flag=True, return_anix=True)

    def test_zero_cnt(self):
        # test that with no details present, count returns zero
        self.assertEqual(self.grp.count_fish_in_group(), 0)

    def test_simple_cnt(self):
        # test groups record a single count correctly
        cnt_val = randint(0, 100)
        utils.enter_cnt(self.cleaned_data, cnt_val, self.evnt.start_date, anix_pk=self.anix.pk, cnt_code="Fish in Container")
        self.assertEqual(self.grp.count_fish_in_group(), cnt_val)

    def test_two_cnts_one_grp(self):
        # add two counts in different containers and make sure group record proper count
        cnt_val = randint(0, 100)
        utils.enter_cnt(self.cleaned_data, cnt_val, self.evnt.start_date, self.anix.pk, cnt_code="Fish in Container")
        # sometimes factories will reuse an event/tank which will prevent new contx's and cnt's from being entered.
        # this loop ensures that new data does get added
        data_entered = False
        while not data_entered:
            anix, contx, data_entered = utils.enter_contx(self.final_tank, self.cleaned_data, grp_pk=self.grp.pk, final_flag=True, return_anix=True)

        utils.enter_cnt(self.cleaned_data, cnt_val, self.evnt.start_date, anix.pk, cnt_code="Fish in Container")
        self.assertEqual(self.grp.count_fish_in_group(), 2 * cnt_val)

    def test_program_grp_cnt(self):
        #  take two types of eggs from group in same event.
        init_cnt = randint(300, 500)
        cnt_one_val = randint(0, 100)
        cnt_two_val = randint(0, 100)
        utils.enter_cnt(self.cleaned_data, init_cnt, self.evnt.start_date, self.anix.pk, cnt_code="Eggs Added")
        cnt = utils.enter_cnt(self.cleaned_data, 0, self.evnt.start_date, self.anix.pk, cnt_code="Eggs Removed")[0]
        utils.enter_cnt_det(self.cleaned_data, cnt, cnt_one_val, "Program Group Split", "EQU")
        utils.enter_cnt_det(self.cleaned_data, cnt, cnt_two_val, "Program Group Split", "PEQU")
        self.assertEqual(self.grp.count_fish_in_group(), init_cnt - cnt_one_val - cnt_two_val)

    def test_aboslute_cnt(self):
        #  take eggs from a group and then record absolute count the following day.
        init_cnt = randint(300, 500)
        cnt_one_val = randint(5, 100)
        cnt_final_val = randint(0, 5)
        next_day_evnt = BioFactoryFloor.EvntFactory()
        next_day_evnt.facic_id = self.evnt.facic_id
        next_day_evnt.start_datetime = self.evnt.start_datetime + timedelta(days=1)
        next_day_evnt.save()
        new_cleaned_data = self.cleaned_data.copy()
        new_cleaned_data["evnt_id"] = next_day_evnt
        end_anix, end_contx, data_entered = utils.enter_contx(self.tank, new_cleaned_data, final_flag=None,
                                                              grp_pk=self.grp.pk, return_anix=True)

        utils.enter_cnt(self.cleaned_data, init_cnt, self.evnt.start_date, self.anix.pk, cnt_code="Eggs Added")
        cnt = utils.enter_cnt(self.cleaned_data, 0, self.evnt.start_date, self.anix.pk, cnt_code="Eggs Removed")[0]
        utils.enter_cnt_det(self.cleaned_data, cnt, cnt_one_val, "Program Group Split", "EQU")
        utils.enter_cnt(new_cleaned_data, cnt_final_val, next_day_evnt.start_date, end_anix.pk, cnt_code="Egg Count")
        self.assertEqual(self.grp.count_fish_in_group(), cnt_final_val)


@tag("Utils")
class TestCollGetter(TestCase):
    fixtures = ["initial_data.json"]

    def setUp(self):
        super().setUp()  # used to import fixtures

    def test_ints_found(self):
        coll_id = utils.coll_getter("FP")
        self.assertIsNotNone(coll_id)

    def test_name_found(self):
        coll_id = utils.coll_getter("Fall Parr")
        self.assertIsNotNone(coll_id)

    def test_WP_found(self):
        # WP is redundent case, appears in both Wild Parr and wild pre smolt
        coll_id = utils.coll_getter("WP")
        self.assertEqual(coll_id.name, "Wild Parr (WP)", coll_id.name)
