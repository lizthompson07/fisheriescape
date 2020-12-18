from django.test import tag

from bio_diversity import forms
from bio_diversity.test import BioFactoryFloor
# from ..test.common_tests import CommonProjectTest as CommonTest
from shared_models.test.common_tests import CommonTest


class TestEvntForm(CommonTest):

    def setUp(self):
        super().setUp()  # used to import fixutres
        self.Form = forms.EvntForm

    @tag("Evnt", 'forms')
    def test_valid_data(self):
        # get valid data
        data = BioFactoryFloor.EvntFactory.build_valid_data()
        invalid_data = data
        self.assert_form_valid(self.Form, data=data)

        # cannot use invalid personnel code
        non_valid_perc = BioFactoryFloor.PercFactory(perc_valid=False)
        invalid_data['perc_id'] = non_valid_perc.pk
        self.assert_form_invalid(self.Form, data=invalid_data)
        invalid_data = data

        # cannot use invalid program
        non_valid_prog = BioFactoryFloor.ProgFactory(valid=False)
        invalid_data['prog_id'] = non_valid_prog.pk
        self.assert_form_invalid(self.Form, data=invalid_data)


class TestIndvForm(CommonTest):

    def setUp(self):
        super().setUp()  # used to import fixutres
        self.Form = forms.IndvForm

    @tag("Indv", 'forms')
    def test_valid_data(self):
        # get valid data
        data = BioFactoryFloor.IndvFactory.build_valid_data()
        self.assert_form_valid(self.Form, data=data)

        # cannot use invalid group code
        non_valid_grp = BioFactoryFloor.GrpFactory(grp_valid=False)
        data['grp_id'] = non_valid_grp.pk
        self.assert_form_invalid(self.Form, data=data)


class TestPairForm(CommonTest):

    def setUp(self):
        super().setUp()  # used to import fixutres
        self.Form = forms.PairForm

    @tag("Pair", 'forms')
    def test_valid_data(self):
        # get valid data
        data = BioFactoryFloor.PairFactory.build_valid_data()
        invalid_data = data
        self.assert_form_valid(self.Form, data=data)

        # cannot use invalid individual code
        non_valid_indv = BioFactoryFloor.IndvFactory(indv_valid=False)
        invalid_data['indv_id'] = non_valid_indv.pk
        self.assert_form_invalid(self.Form, data=invalid_data)
        invalid_data = data

        # cannot use individual code with null ufid
        non_valid_indv = BioFactoryFloor.IndvFactory(ufid="")
        invalid_data['indv_id'] = non_valid_indv.pk
        self.assert_form_invalid(self.Form, data=invalid_data)


class TestProtForm(CommonTest):

    def setUp(self):
        super().setUp()  # used to import fixutres
        self.Form = forms.ProtForm

    @tag("Prot", 'forms')
    def test_valid_data(self):
        # get valid data
        data = BioFactoryFloor.ProtFactory.build_valid_data()
        self.assert_form_valid(self.Form, data=data)

        # cannot use invalid program
        non_valid_prog = BioFactoryFloor.ProgFactory(valid=False)
        data['prog_id'] = non_valid_prog.pk
        self.assert_form_invalid(self.Form, data=data)


class TestProtfForm(CommonTest):

    def setUp(self):
        super().setUp()  # used to import fixutres
        self.Form = forms.ProtfForm

    @tag("Protf", 'forms')
    def test_valid_data(self):
        # get valid data
        data = BioFactoryFloor.ProtfFactory.build_valid_data()
        self.assert_form_valid(self.Form, data=data)

        # cannot use invalid protocol
        non_valid_prot = BioFactoryFloor.ProtFactory(valid=False)
        data['prot_id'] = non_valid_prot.pk
        self.assert_form_invalid(self.Form, data=data)


class TestSireForm(CommonTest):

    def setUp(self):
        super().setUp()  # used to import fixutres
        self.Form = forms.SireForm

    @tag("Sire", 'forms')
    def test_valid_data(self):
        # get valid data
        data = BioFactoryFloor.SireFactory.build_valid_data()
        invalid_data = data
        self.assert_form_valid(self.Form, data=data)

        # cannot use invalid pair code
        non_valid_pair = BioFactoryFloor.PairFactory(valid=False)
        invalid_data['pair_id'] = non_valid_pair.pk
        self.assert_form_invalid(self.Form, data=invalid_data)
        invalid_data = data

        # cannot use invalid individual code
        non_valid_indv = BioFactoryFloor.IndvFactory(indv_valid=False)
        invalid_data['indv_id'] = non_valid_indv.pk
        self.assert_form_invalid(self.Form, data=invalid_data)
        invalid_data = data

        # cannot use individual code with null ufid
        non_valid_indv = BioFactoryFloor.IndvFactory(ufid="")
        invalid_data['indv_id'] = non_valid_indv.pk
        self.assert_form_invalid(self.Form, data=invalid_data)


class TestSpwnForm(CommonTest):

    def setUp(self):
        super().setUp()  # used to import fixutres
        self.Form = forms.SpwnForm

    @tag("Spwn", 'forms')
    def test_valid_data(self):
        # get valid data
        data = BioFactoryFloor.SpwnFactory.build_valid_data()
        self.assert_form_valid(self.Form, data=data)

        # cannot use invalid pair code
        non_valid_pair = BioFactoryFloor.PairFactory(valid=False)
        data['pair_id'] = non_valid_pair.pk
        self.assert_form_invalid(self.Form, data=data)


class TestTeamForm(CommonTest):

    def setUp(self):
        super().setUp()  # used to import fixutres
        self.Form = forms.TeamForm

    @tag("Team", 'forms')
    def test_valid_data(self):
        # get valid data
        data = BioFactoryFloor.TeamFactory.build_valid_data()
        self.assert_form_valid(self.Form, data=data)

        # cannot use invalid personnel code
        non_valid_perc = BioFactoryFloor.PercFactory(perc_valid=False)
        data['perc_id'] = non_valid_perc.pk
        self.assert_form_invalid(self.Form, data=data)
