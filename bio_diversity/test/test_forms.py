from django.test import tag

from bio_diversity import forms
from bio_diversity.test import BioFactoryFloor
# from ..test.common_tests import CommonProjectTest as CommonTest
from shared_models.test.common_tests import CommonTest


@tag("Cntd", 'forms')
class TestCntdForm(CommonTest):

    def setUp(self):
        super().setUp()  # used to import fixtures
        self.Form = forms.CntdForm
        self.data = BioFactoryFloor.CntdFactory.build_valid_data()

    def test_valid_data(self):
        # get valid data
        self.assert_form_valid(self.Form, data=self.data)

    def test_invalid_val(self):
        # cannot use values outside of anidc min-max range
        invalid_data = self.data
        test_anidc = BioFactoryFloor.AnidcFactory(max_val=(invalid_data['det_val'] - 1))
        invalid_data['anidc_id'] = test_anidc.pk
        self.assert_form_invalid(self.Form, data=invalid_data)

        invalid_data = self.data
        test_anidc = BioFactoryFloor.AnidcFactory(min_val=(invalid_data['det_val'] + 1))
        invalid_data['anidc_id'] = test_anidc.pk
        self.assert_form_invalid(self.Form, data=invalid_data)


@tag("Cupd", 'forms')
class TestCupdForm(CommonTest):

    def setUp(self):
        super().setUp()  # used to import fixtures
        self.Form = forms.CupdForm
        self.data = BioFactoryFloor.CupdFactory.build_valid_data()

    def test_valid_data(self):
        # get valid data
        self.assert_form_valid(self.Form, data=self.data)

    def test_invalid_val(self):
        # cannot use values outside of contdc min-max range
        invalid_data = self.data
        test_contdc = BioFactoryFloor.ContdcFactory(max_val=(invalid_data['det_value'] - 1))
        invalid_data['contdc_id'] = test_contdc.pk
        self.assert_form_invalid(self.Form, data=invalid_data)

        invalid_data = self.data
        test_contdc = BioFactoryFloor.ContdcFactory(min_val=(invalid_data['det_value'] + 1))
        invalid_data['contdc_id'] = test_contdc.pk
        self.assert_form_invalid(self.Form, data=invalid_data)


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

        invalid_data = self.data
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


@tag("Grpd", 'forms')
class TestGrpdForm(CommonTest):

    def setUp(self):
        super().setUp()  # used to import fixtures
        self.Form = forms.GrpdForm
        self.data = BioFactoryFloor.GrpdFactory.build_valid_data()

    def test_valid_data(self):
        # get valid data
        self.assert_form_valid(self.Form, data=self.data)

    def test_invalid_val(self):
        # cannot use values outside of anidc min-max range
        invalid_data = self.data
        test_anidc = BioFactoryFloor.AnidcFactory(max_val=(invalid_data['det_val'] - 1))
        invalid_data['anidc_id'] = test_anidc.pk
        self.assert_form_invalid(self.Form, data=invalid_data)

        invalid_data = self.data
        test_anidc = BioFactoryFloor.AnidcFactory(min_val=(invalid_data['det_val'] + 1))
        invalid_data['anidc_id'] = test_anidc.pk
        self.assert_form_invalid(self.Form, data=invalid_data)


@tag("Heatd", 'forms')
class TestHeatdForm(CommonTest):

    def setUp(self):
        super().setUp()  # used to import fixtures
        self.Form = forms.HeatdForm
        self.data = BioFactoryFloor.HeatdFactory.build_valid_data()

    def test_valid_data(self):
        # get valid data
        self.assert_form_valid(self.Form, data=self.data)

    def test_invalid_val(self):
        # cannot use values outside of contdc min-max range
        invalid_data = self.data
        test_contdc = BioFactoryFloor.ContdcFactory(max_val=(invalid_data['det_value'] - 1))
        invalid_data['contdc_id'] = test_contdc.pk
        self.assert_form_invalid(self.Form, data=invalid_data)

        invalid_data = self.data
        test_contdc = BioFactoryFloor.ContdcFactory(min_val=(invalid_data['det_value'] + 1))
        invalid_data['contdc_id'] = test_contdc.pk
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


@tag("Indvd", 'forms')
class TestIndvdForm(CommonTest):

    def setUp(self):
        super().setUp()  # used to import fixtures
        self.Form = forms.IndvdForm
        self.data = BioFactoryFloor.IndvdFactory.build_valid_data()

    def test_valid_data(self):
        # get valid data
        self.assert_form_valid(self.Form, data=self.data)

    def test_invalid_val(self):
        # cannot use values outside of anidc min-max range
        invalid_data = self.data
        test_anidc = BioFactoryFloor.AnidcFactory(max_val=(invalid_data['det_val'] - 1))
        invalid_data['anidc_id'] = test_anidc.pk
        self.assert_form_invalid(self.Form, data=invalid_data)

        invalid_data = self.data
        test_anidc = BioFactoryFloor.AnidcFactory(min_val=(invalid_data['det_val'] + 1))
        invalid_data['anidc_id'] = test_anidc.pk
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
        invalid_data = self.data
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


@tag("Sampd", 'forms')
class TestSampdForm(CommonTest):

    def setUp(self):
        super().setUp()  # used to import fixtures
        self.Form = forms.SampdForm
        self.data = BioFactoryFloor.SampdFactory.build_valid_data()

    def test_valid_data(self):
        # get valid data
        self.assert_form_valid(self.Form, data=self.data)

    def test_invalid_val(self):
        # cannot use values outside of anidc min-max range
        invalid_data = self.data
        test_anidc = BioFactoryFloor.AnidcFactory(max_val=(invalid_data['det_val'] - 1))
        invalid_data['anidc_id'] = test_anidc.pk
        self.assert_form_invalid(self.Form, data=invalid_data)

        invalid_data = self.data
        test_anidc = BioFactoryFloor.AnidcFactory(min_val=(invalid_data['det_val'] + 1))
        invalid_data['anidc_id'] = test_anidc.pk
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
        invalid_data = self.data
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


@tag("Spwnd", 'forms')
class TestSpwndForm(CommonTest):

    def setUp(self):
        super().setUp()  # used to import fixtures
        self.Form = forms.SpwndForm
        self.data = BioFactoryFloor.SpwndFactory.build_valid_data()

    def test_valid_data(self):
        # get valid data
        self.assert_form_valid(self.Form, data=self.data)

    def test_invalid_val(self):
        # cannot use values outside of spwndc min-max range
        invalid_data = self.data
        test_spwndc = BioFactoryFloor.SpwndcFactory(max_val=(invalid_data['det_val'] - 1))
        invalid_data['spwndc_id'] = test_spwndc.pk
        self.assert_form_invalid(self.Form, data=invalid_data)

        invalid_data = self.data
        test_spwndc = BioFactoryFloor.SpwndcFactory(min_val=(invalid_data['det_val'] + 1))
        invalid_data['spwndc_id'] = test_spwndc.pk
        self.assert_form_invalid(self.Form, data=invalid_data)


@tag("Tankd", 'forms')
class TestTankdForm(CommonTest):

    def setUp(self):
        super().setUp()  # used to import fixtures
        self.Form = forms.TankdForm
        self.data = BioFactoryFloor.TankdFactory.build_valid_data()

    def test_valid_data(self):
        # get valid data
        self.assert_form_valid(self.Form, data=self.data)

    def test_invalid_val(self):
        # cannot use values outside of contdc min-max range
        invalid_data = self.data
        test_contdc = BioFactoryFloor.ContdcFactory(max_val=(invalid_data['det_value'] - 1))
        invalid_data['contdc_id'] = test_contdc.pk
        self.assert_form_invalid(self.Form, data=invalid_data)

        invalid_data = self.data
        test_contdc = BioFactoryFloor.ContdcFactory(min_val=(invalid_data['det_value'] + 1))
        invalid_data['contdc_id'] = test_contdc.pk
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


@tag("Trayd", 'forms')
class TestTraydForm(CommonTest):

    def setUp(self):
        super().setUp()  # used to import fixtures
        self.Form = forms.TraydForm
        self.data = BioFactoryFloor.TraydFactory.build_valid_data()

    def test_valid_data(self):
        # get valid data
        self.assert_form_valid(self.Form, data=self.data)

    def test_invalid_val(self):
        # cannot use values outside of contdc min-max range
        invalid_data = self.data
        test_contdc = BioFactoryFloor.ContdcFactory(max_val=(invalid_data['det_value'] - 1))
        invalid_data['contdc_id'] = test_contdc.pk
        self.assert_form_invalid(self.Form, data=invalid_data)

        invalid_data = self.data
        test_contdc = BioFactoryFloor.ContdcFactory(min_val=(invalid_data['det_value'] + 1))
        invalid_data['contdc_id'] = test_contdc.pk
        self.assert_form_invalid(self.Form, data=invalid_data)


@tag("Trofd", 'forms')
class TestTrofdForm(CommonTest):

    def setUp(self):
        super().setUp()  # used to import fixtures
        self.Form = forms.TrofdForm
        self.data = BioFactoryFloor.TrofdFactory.build_valid_data()

    def test_valid_data(self):
        # get valid data
        self.assert_form_valid(self.Form, data=self.data)

    def test_invalid_val(self):
        # cannot use values outside of contdc min-max range
        invalid_data = self.data
        test_contdc = BioFactoryFloor.ContdcFactory(max_val=(invalid_data['det_value'] - 1))
        invalid_data['contdc_id'] = test_contdc.pk
        self.assert_form_invalid(self.Form, data=invalid_data)

        invalid_data = self.data
        test_contdc = BioFactoryFloor.ContdcFactory(min_val=(invalid_data['det_value'] + 1))
        invalid_data['contdc_id'] = test_contdc.pk
        self.assert_form_invalid(self.Form, data=invalid_data)
