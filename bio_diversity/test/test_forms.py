from django.test import tag

from bio_diversity import forms
from bio_diversity.test import BioFactoryFloor
# from ..test.common_tests import CommonProjectTest as CommonTest
from shared_models.test.common_tests import CommonTest


@tag("Env", 'forms')
class TestEnvForm(CommonTest):

    def setUp(self):
        super().setUp()  # used to import fixtures
        self.Form = forms.EnvForm
        self.data = BioFactoryFloor.EnvFactory.build_valid_data()

    def test_valid_data(self):
        # get valid data
        self.assert_form_valid(self.Form, data=self.data)

    def test_invalid_val(self):
        # cannot use values outside of envc min-max range
        invalid_data = self.data

        test_envc = BioFactoryFloor.EnvcFactory(max_val=(invalid_data['env_val'] - 1))
        invalid_data['envc_id'] = test_envc.pk
        self.assert_form_invalid(self.Form, data=invalid_data)

        test_envc = BioFactoryFloor.EnvcFactory(min_val=(invalid_data['env_val'] + 1))
        invalid_data['envc_id'] = test_envc.pk
        self.assert_form_invalid(self.Form, data=invalid_data)


@tag("Evnt", 'forms')
class TestEvntForm(CommonTest):

    def setUp(self):
        super().setUp()  # used to import fixtures
        self.Form = forms.EvntForm
        self.data = BioFactoryFloor.EvntFactory.build_valid_data()

    def test_valid_data(self):
        # get valid data
        self.assert_form_valid(self.Form, data=self.data)

    def test_invalid_perc(self):
        # cannot use invalid personnel code
        invalid_data = self.data
        non_valid_perc = BioFactoryFloor.PercFactory(perc_valid=False)
        invalid_data['perc_id'] = non_valid_perc.pk
        self.assert_form_invalid(self.Form, data=invalid_data)

    def test_invalid_prog(self):
        # cannot use invalid program
        invalid_data = self.data
        non_valid_prog = BioFactoryFloor.ProgFactory(valid=False)
        invalid_data['prog_id'] = non_valid_prog.pk
        self.assert_form_invalid(self.Form, data=invalid_data)


@tag("Indv", 'forms')
class TestIndvForm(CommonTest):

    def setUp(self):
        super().setUp()  # used to import fixtures
        self.data = BioFactoryFloor.IndvFactory.build_valid_data()
        self.Form = forms.IndvForm

    def test_valid_data(self):
        # get valid data
        self.assert_form_valid(self.Form, data=self.data)

    def test_invalid_grp(self):
        # cannot use invalid group code
        invalid_data = self.data
        non_valid_grp = BioFactoryFloor.GrpFactory(grp_valid=False)
        invalid_data['grp_id'] = non_valid_grp.pk
        self.assert_form_invalid(self.Form, data=invalid_data)


@tag("Pair", 'forms')
class TestPairForm(CommonTest):

    def setUp(self):
        super().setUp()  # used to import fixtures
        self.data = BioFactoryFloor.PairFactory.build_valid_data()
        self.Form = forms.PairForm

    def test_valid_data(self):
        # get valid data
        self.assert_form_valid(self.Form, data=self.data)

    def test_invalid_indv(self):
        # cannot use invalid individual code
        invalid_data = self.data
        non_valid_indv = BioFactoryFloor.IndvFactory(indv_valid=False)
        invalid_data['indv_id'] = non_valid_indv.pk
        self.assert_form_invalid(self.Form, data=invalid_data)

        # cannot use individual code with null ufid
        non_valid_indv = BioFactoryFloor.IndvFactory(ufid="")
        invalid_data['indv_id'] = non_valid_indv.pk
        self.assert_form_invalid(self.Form, data=invalid_data)


@tag("Prot", 'forms')
class TestProtForm(CommonTest):

    def setUp(self):
        super().setUp()  # used to import fixtures
        self.data = BioFactoryFloor.ProtFactory.build_valid_data()
        self.Form = forms.ProtForm

    def test_valid_data(self):
        # get valid data
        self.assert_form_valid(self.Form, data=self.data)

    def test_invalid_prog(self):
        # cannot use invalid program
        invalid_data = self.data
        non_valid_prog = BioFactoryFloor.ProgFactory(valid=False)
        invalid_data['prog_id'] = non_valid_prog.pk
        self.assert_form_invalid(self.Form, data=invalid_data)


@tag("Protf", 'forms')
class TestProtfForm(CommonTest):

    def setUp(self):
        super().setUp()  # used to import fixtures
        self.data = BioFactoryFloor.ProtfFactory.build_valid_data()
        self.Form = forms.ProtfForm

    def test_valid_data(self):
        # get valid data
        self.assert_form_valid(self.Form, data=self.data)

    def test_invalid_prot(self):
        # cannot use invalid protocol
        invalid_data = self.data
        non_valid_prot = BioFactoryFloor.ProtFactory(valid=False)
        invalid_data['prot_id'] = non_valid_prot.pk
        self.assert_form_invalid(self.Form, data=invalid_data)


@tag("Sire", 'forms')
class TestSireForm(CommonTest):

    def setUp(self):
        super().setUp()  # used to import fixtures
        self.data = BioFactoryFloor.SireFactory.build_valid_data()
        self.Form = forms.SireForm

    def test_valid_data(self):
        # get valid data
        self.assert_form_valid(self.Form, data=self.data)

    def test_invalid_pair(self):
        # cannot use invalid pair code
        invalid_data = self.data
        non_valid_pair = BioFactoryFloor.PairFactory(valid=False)
        invalid_data['pair_id'] = non_valid_pair.pk
        self.assert_form_invalid(self.Form, data=invalid_data)

    def test_invalid_indv(self):
        # cannot use invalid individual code
        invalid_data = self.data
        non_valid_indv = BioFactoryFloor.IndvFactory(indv_valid=False)
        invalid_data['indv_id'] = non_valid_indv.pk
        self.assert_form_invalid(self.Form, data=invalid_data)

        # cannot use individual code with null ufid
        non_valid_indv = BioFactoryFloor.IndvFactory(ufid="")
        invalid_data['indv_id'] = non_valid_indv.pk
        self.assert_form_invalid(self.Form, data=invalid_data)


@tag("Spwn", 'forms')
class TestSpwnForm(CommonTest):

    def setUp(self):
        super().setUp()  # used to import fixtures
        self.data = BioFactoryFloor.SpwnFactory.build_valid_data()
        self.Form = forms.SpwnForm

    def test_valid_data(self):
        # get valid data
        self.assert_form_valid(self.Form, data=self.data)

    def test_invalid_pair(self):
        # cannot use invalid pair code
        invalid_data = self.data
        non_valid_pair = BioFactoryFloor.PairFactory(valid=False)
        invalid_data['pair_id'] = non_valid_pair.pk
        self.assert_form_invalid(self.Form, data=invalid_data)


@tag("Team", 'forms')
class TestTeamForm(CommonTest):

    def setUp(self):
        super().setUp()  # used to import fixtures
        self.data = BioFactoryFloor.TeamFactory.build_valid_data()
        self.Form = forms.TeamForm

    def test_valid_data(self):
        # get valid data
        self.assert_form_valid(self.Form, data=self.data)

    def test_invalid_perc(self):
        # cannot use invalid personnel code
        invalid_data = self.data
        non_valid_perc = BioFactoryFloor.PercFactory(perc_valid=False)
        invalid_data['perc_id'] = non_valid_perc.pk
        self.assert_form_invalid(self.Form, data=invalid_data)
