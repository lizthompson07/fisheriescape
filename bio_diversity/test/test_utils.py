import datetime

from django.test import tag
from bio_diversity.test import BioFactoryFloor
from bio_diversity import models, utils
from shared_models.test.common_tests import CommonTest
from random import randint


@tag("Grp", "Move", "Utils")
class TestGrpMove(CommonTest):
    fixtures = ["initial_data.json"]

    def setUp(self):
        super().setUp()  # used to import fixtures

        # create group, tank and evnt
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

    def test_grp_in_cont(self):
        # test a group with a contx is in one and only one tank:
        utils.enter_contx(self.tank, self.cleaned_data, True, grp_pk=self.grp.pk)
        self.assertEqual(self.grp.current_cont()[0], self.tank)
        self.assertEqual(len(self.grp.current_cont()), 1)

    def test_cont_has_grp(self):
        # test a tank with a contx has one and only one group in it:
        utils.enter_contx(self.tank, self.cleaned_data, True, grp_pk=self.grp.pk)
        indv_list, grp_list = self.tank.fish_in_cont()
        self.assertEqual(len(grp_list), 1)
        self.assertIn(self.grp, grp_list)

    def test_move_grp(self):
        # grp in one tank, gets moved, is in second tank and not in first tank
        utils.enter_contx(self.tank, self.cleaned_data, True, grp_pk=self.grp.pk)
        indv_list, grp_list = self.tank.fish_in_cont()
        self.assertIn(self.grp, grp_list)
        move_date = datetime.datetime.now().date()
        utils.create_movement_evnt(self.tank, self.final_tank, self.cleaned_data, move_date, grp_pk=self.grp.pk)
        indv_list, grp_list = self.tank.fish_in_cont()
        self.assertNotIn(self.grp, grp_list)
        indv_list, grp_list = self.final_tank.fish_in_cont()
        self.assertIn(self.grp, grp_list)

    def test_two_grps_one_tank(self):
        #  put two grps into a single tank, make sure both are located:
        second_grp = BioFactoryFloor.GrpFactory()
        utils.enter_contx(self.tank, self.cleaned_data, True, grp_pk=self.grp.pk)
        utils.enter_contx(self.tank, self.cleaned_data, True, grp_pk=second_grp.pk)
        indv_list, grp_list = self.tank.fish_in_cont()
        self.assertEqual(len(grp_list), 2)
        self.assertIn(self.grp, grp_list)
        self.assertIn(second_grp, grp_list)


@tag("Grp", "Cnt", "Utils")
class TestGrpCnts(CommonTest):
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
        self.contx = utils.enter_contx(self.tank, self.cleaned_data, True, grp_pk=self.grp.pk, return_contx=True)

    def test_zero_cnt(self):
        # test that with no details present count returns zero
        self.assertEqual(self.grp.count_fish_in_group(), 0)

    def test_simple_cnt(self):
        # test groups record a single count correctly
        cnt_val = randint(0, 100)
        utils.enter_cnt(self.cleaned_data, cnt_val, self.contx.pk, cnt_code="Fish in Container")
        self.assertEqual(self.grp.count_fish_in_group(), cnt_val)

    def test_two_cnts_one_grp(self):
        # add two counts in different containers and make sure group record proper count
        cnt_val = randint(0, 100)
        utils.enter_cnt(self.cleaned_data, cnt_val, self.contx.pk, cnt_code="Fish in Container")
        contx = utils.enter_contx(self.final_tank, self.cleaned_data, True, grp_pk=self.grp.pk, return_contx=True)
        utils.enter_cnt(self.cleaned_data, cnt_val, contx.pk, cnt_code="Fish in Container")
        self.assertEqual(self.grp.count_fish_in_group(), 2 * cnt_val)

