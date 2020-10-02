from whalesdb import mixins, models, forms
from shared_models import models as shared_models

from django.test import TestCase, tag


class CommonMixinsTest(TestCase):
    mixin = None
    expected_key = None
    expected_title = None
    expected_model = None
    expected_form = None

    def assertKeyExists(self):
        self.assertEqual(self.expected_key, self.mixin.key)

    def assertTitleExists(self):
        self.assertEqual(self.expected_title, self.mixin.title)

    def assertCorrectModel(self):
        self.assertEqual(self.expected_model, self.mixin.model)

    def assertCorrectForm(self):
        self.assertEqual(self.expected_form, self.mixin.form_class)


class TestCru(CommonMixinsTest):

    def setUp(self) -> None:
        self.mixin = mixins.CruMixin
        self.expected_key = 'cru'
        self.expected_title = "Cruise"
        self.expected_model = shared_models.Cruise
        self.expected_form = forms.CruForm

    @tag('cru', 'mixin', 'key')
    def test_cru_mixin_key(self):
        super().assertKeyExists()

    @tag('cru', 'mixin', 'title')
    def test_cru_mixin_title(self):
        super().assertTitleExists()

    @tag('cru', 'mixin', 'model')
    def test_cru_mixin_model(self):
        super().assertCorrectModel()

    @tag('cru', 'mixin', 'form')
    def test_cru_mixin_form(self):
        super().assertCorrectForm()


class TestDep(CommonMixinsTest):

    def setUp(self) -> None:
        self.mixin = mixins.DepMixin
        self.expected_key = 'dep'
        self.expected_title = "Deployment"
        self.expected_model = models.DepDeployment
        self.expected_form = forms.DepForm

    @tag('dep', 'mixin', 'key')
    def test_dep_mixin_key(self):
        super().assertKeyExists()

    @tag('dep', 'mixin', 'title')
    def test_dep_mixin_title(self):
        super().assertTitleExists()

    @tag('dep', 'mixin', 'model')
    def test_dep_mixin_model(self):
        super().assertCorrectModel()

    @tag('dep', 'mixin', 'form')
    def test_dep_mixin_form(self):
        super().assertCorrectForm()


class TestEca(CommonMixinsTest):

    def setUp(self) -> None:
        self.mixin = mixins.EcaMixin
        self.expected_key = 'eca'
        self.expected_title = "Calibration Event"
        self.expected_model = models.EcaCalibrationEvent
        self.expected_form = forms.EcaForm

    @tag('eca', 'mixin', 'key')
    def test_eca_mixin_key(self):
        super().assertKeyExists()

    @tag('eca', 'mixin', 'title')
    def test_eca_mixin_title(self):
        super().assertTitleExists()

    @tag('eca', 'mixin', 'model')
    def test_eca_mixin_model(self):
        super().assertCorrectModel()

    @tag('eca', 'mixin', 'form')
    def test_eca_mixin_form(self):
        super().assertCorrectForm()


class TestEda(CommonMixinsTest):

    def setUp(self) -> None:
        self.mixin = mixins.EdaMixin
        self.expected_key = 'eda'
        self.expected_title = "Equipment Attachment"
        self.expected_model = models.EdaEquipmentAttachment
        self.expected_form = forms.EdaForm

    @tag('eda', 'mixin', 'key')
    def test_eda_mixin_key(self):
        super().assertKeyExists()

    @tag('eda', 'mixin', 'title')
    def test_eda_mixin_title(self):
        super().assertTitleExists()

    @tag('eda', 'mixin', 'model')
    def test_eda_mixin_model(self):
        super().assertCorrectModel()

    @tag('eda', 'mixin', 'form')
    def test_eda_mixin_form(self):
        super().assertCorrectForm()


class TestEmm(CommonMixinsTest):

    def setUp(self) -> None:
        self.mixin = mixins.EmmMixin
        self.expected_key = 'emm'
        self.expected_title = "Make/Model"
        self.expected_model = models.EmmMakeModel
        self.expected_form = forms.EmmForm

    @tag('emm', 'mixin', 'key')
    def test_emm_mixin_key(self):
        super().assertKeyExists()

    @tag('emm', 'mixin', 'title')
    def test_emm_mixin_title(self):
        super().assertTitleExists()

    @tag('emm', 'mixin', 'model')
    def test_emm_mixin_model(self):
        super().assertCorrectModel()

    @tag('emm', 'mixin', 'form')
    def test_emm_mixin_form(self):
        super().assertCorrectForm()


class TestEqh(CommonMixinsTest):

    def setUp(self) -> None:
        self.mixin = mixins.EqhMixin
        self.expected_key = 'eqh'
        self.expected_title = "Hydrophone Properties"
        self.expected_model = models.EqhHydrophoneProperty
        self.expected_form = forms.EqhForm

    @tag('eqh', 'mixin', 'key')
    def test_eqh_mixin_key(self):
        super().assertKeyExists()

    @tag('eqh', 'mixin', 'title')
    def test_eqh_mixin_title(self):
        super().assertTitleExists()

    @tag('eqh', 'mixin', 'model')
    def test_eqh_mixin_model(self):
        super().assertCorrectModel()

    @tag('eqh', 'mixin', 'form')
    def test_eqh_mixin_form(self):
        super().assertCorrectForm()


class TestEqp(CommonMixinsTest):

    def setUp(self) -> None:
        self.mixin = mixins.EqpMixin
        self.expected_key = 'eqp'
        self.expected_title = "Equipment"
        self.expected_model = models.EqpEquipment
        self.expected_form = forms.EqpForm

    @tag('eqp', 'mixin', 'key')
    def test_eqp_mixin_key(self):
        super().assertKeyExists()

    @tag('eqp', 'mixin', 'title')
    def test_eqp_mixin_title(self):
        super().assertTitleExists()

    @tag('eqp', 'mixin', 'model')
    def test_eqp_mixin_model(self):
        super().assertCorrectModel()

    @tag('eqp', 'mixin', 'form')
    def test_eqp_mixin_form(self):
        super().assertCorrectForm()


class TestEqo(CommonMixinsTest):

    def setUp(self) -> None:
        self.mixin = mixins.EqoMixin
        self.expected_key = 'eqo'
        self.expected_title = "Equipment Owner"
        self.expected_model = models.EqoOwner
        self.expected_form = forms.EqoForm

    @tag('eqo', 'mixin', 'key')
    def test_eqo_mixin_key(self):
        super().assertKeyExists()

    @tag('eqo', 'mixin', 'title')
    def test_eqo_mixin_title(self):
        super().assertTitleExists()

    @tag('eqo', 'mixin', 'model')
    def test_eqo_mixin_model(self):
        super().assertCorrectModel()

    @tag('eqo', 'mixin', 'form')
    def test_eqo_mixin_form(self):
        super().assertCorrectForm()


class TestEqr(CommonMixinsTest):

    def setUp(self) -> None:
        self.mixin = mixins.EqrMixin
        self.expected_key = 'eqr'
        self.expected_title = "Recorder Properties"
        self.expected_model = models.EqrRecorderProperties
        self.expected_form = forms.EqrForm

    @tag('eqr', 'mixin', 'key')
    def test_eqr_mixin_key(self):
        super().assertKeyExists()

    @tag('eqr', 'mixin', 'title')
    def test_eqr_mixin_title(self):
        super().assertTitleExists()

    @tag('eqr', 'mixin', 'model')
    def test_eqr_mixin_model(self):
        super().assertCorrectModel()

    @tag('eqr', 'mixin', 'form')
    def test_eqr_mixin_form(self):
        super().assertCorrectForm()


class TestEtr(CommonMixinsTest):

    def setUp(self) -> None:
        self.mixin = mixins.EtrMixin
        self.expected_key = 'etr'
        self.expected_title = "Equipment Technical Repair Event"
        self.expected_model = models.EtrTechnicalRepairEvent
        self.expected_form = forms.EtrForm

    @tag('etr', 'mixin', 'key')
    def test_etr_mixin_key(self):
        super().assertKeyExists()

    @tag('etr', 'mixin', 'title')
    def test_etr_mixin_title(self):
        super().assertTitleExists()

    @tag('etr', 'mixin', 'model')
    def test_etr_mixin_model(self):
        super().assertCorrectModel()

    @tag('etr', 'mixin', 'form')
    def test_etr_mixin_form(self):
        super().assertCorrectForm()


class TestMor(CommonMixinsTest):

    def setUp(self) -> None:
        self.mixin = mixins.MorMixin
        self.expected_key = 'mor'
        self.expected_title = "Mooring Setup"
        self.expected_model = models.MorMooringSetup
        self.expected_form = forms.MorForm

    @tag('mor', 'mixin', 'key')
    def test_mor_mixin_key(self):
        super().assertKeyExists()

    @tag('mor', 'mixin', 'title')
    def test_mor_mixin_title(self):
        super().assertTitleExists()

    @tag('mor', 'mixin', 'model')
    def test_mor_mixin_model(self):
        super().assertCorrectModel()

    @tag('mor', 'mixin', 'form')
    def test_mor_mixin_form(self):
        super().assertCorrectForm()


class TestPrj(CommonMixinsTest):

    def setUp(self) -> None:
        self.mixin = mixins.PrjMixin
        self.expected_key = 'prj'
        self.expected_title = "Project"
        self.expected_model = models.PrjProject
        self.expected_form = forms.PrjForm

    @tag('prj', 'mixin', 'key')
    def test_prj_mixin_key(self):
        super().assertKeyExists()

    @tag('prj', 'mixin', 'title')
    def test_prj_mixin_title(self):
        super().assertTitleExists()

    @tag('prj', 'mixin', 'model')
    def test_prj_mixin_model(self):
        super().assertCorrectModel()

    @tag('prj', 'mixin', 'form')
    def test_prj_mixin_form(self):
        super().assertCorrectForm()


class TestRci(CommonMixinsTest):

    def setUp(self) -> None:
        self.mixin = mixins.RciMixin
        self.expected_key = 'rci'
        self.expected_title = "Channel Information"
        self.expected_model = models.RciChannelInfo
        self.expected_form = forms.RciForm

    @tag('rci', 'mixin', 'key')
    def test_rci_mixin_key(self):
        super().assertKeyExists()

    @tag('rci', 'mixin', 'title')
    def test_rci_mixin_title(self):
        super().assertTitleExists()

    @tag('rci', 'mixin', 'model')
    def test_rci_mixin_model(self):
        super().assertCorrectModel()

    @tag('rci', 'mixin', 'form')
    def test_rci_mixin_form(self):
        super().assertCorrectForm()


class TestRec(CommonMixinsTest):

    def setUp(self) -> None:
        self.mixin = mixins.RecMixin
        self.expected_key = 'rec'
        self.expected_title = "Dataset"
        self.expected_model = models.RecDataset
        self.expected_form = forms.RecForm

    @tag('rec', 'mixin', 'key')
    def test_rec_mixin_key(self):
        super().assertKeyExists()

    @tag('rec', 'mixin', 'title')
    def test_rec_mixin_title(self):
        super().assertTitleExists()

    @tag('rec', 'mixin', 'model')
    def test_rec_mixin_model(self):
        super().assertCorrectModel()

    @tag('rec', 'mixin', 'form')
    def test_rec_mixin_form(self):
        super().assertCorrectForm()


class TestRee(CommonMixinsTest):

    def setUp(self) -> None:
        self.mixin = mixins.ReeMixin
        self.expected_key = 'ree'
        self.expected_title = "Recording Events"
        self.expected_model = models.ReeRecordingEvent
        self.expected_form = forms.ReeForm

    @tag('ree', 'mixin', 'key')
    def test_ree_mixin_key(self):
        super().assertKeyExists()

    @tag('ree', 'mixin', 'title')
    def test_ree_mixin_title(self):
        super().assertTitleExists()

    @tag('ree', 'mixin', 'model')
    def test_ree_mixin_model(self):
        super().assertCorrectModel()

    @tag('ree', 'mixin', 'form')
    def test_ree_mixin_form(self):
        super().assertCorrectForm()


class TestRet(CommonMixinsTest):

    def setUp(self) -> None:
        self.mixin = mixins.RetMixin
        self.expected_key = 'ret'
        self.expected_title = "Recording Event Type"
        self.expected_model = models.RetRecordingEventType
        self.expected_form = forms.RetForm

    @tag('ret', 'mixin', 'key')
    def test_ret_mixin_key(self):
        super().assertKeyExists()

    @tag('ret', 'mixin', 'title')
    def test_ret_mixin_title(self):
        super().assertTitleExists()

    @tag('ret', 'mixin', 'model')
    def test_ret_mixin_model(self):
        super().assertCorrectModel()

    @tag('ret', 'mixin', 'form')
    def test_ret_mixin_form(self):
        super().assertCorrectForm()


class TestRsc(CommonMixinsTest):

    def setUp(self) -> None:
        self.mixin = mixins.RscMixin
        self.expected_key = 'rsc'
        self.expected_title = "Recording Schedule"
        self.expected_model = models.RscRecordingSchedule
        self.expected_form = forms.RscForm

    @tag('rsc', 'mixin', 'key')
    def test_rsc_mixin_key(self):
        super().assertKeyExists()

    @tag('rsc', 'mixin', 'title')
    def test_rsc_mixin_title(self):
        super().assertTitleExists()

    @tag('rsc', 'mixin', 'model')
    def test_rsc_mixin_model(self):
        super().assertCorrectModel()

    @tag('rsc', 'mixin', 'form')
    def test_rsc_mixin_form(self):
        super().assertCorrectForm()


class TestRst(CommonMixinsTest):

    def setUp(self) -> None:
        self.mixin = mixins.RstMixin
        self.expected_key = 'rst'
        self.expected_title = "Recording Stage"
        self.expected_model = models.RstRecordingStage
        self.expected_form = forms.RstForm

    @tag('rst', 'mixin', 'key')
    def test_rst_mixin_key(self):
        super().assertKeyExists()

    @tag('rst', 'mixin', 'title')
    def test_rst_mixin_title(self):
        super().assertTitleExists()

    @tag('rst', 'mixin', 'model')
    def test_rst_mixin_model(self):
        super().assertCorrectModel()

    @tag('rst', 'mixin', 'form')
    def test_rst_mixin_form(self):
        super().assertCorrectForm()


class TestRtt(CommonMixinsTest):

    def setUp(self) -> None:
        self.mixin = mixins.RttMixin
        self.expected_key = 'rtt'
        self.expected_title = "Time Zone"
        self.expected_model = models.RttTimezoneCode
        self.expected_form = forms.RttForm

    @tag('rtt', 'mixin', 'key')
    def test_rtt_mixin_key(self):
        super().assertKeyExists()

    @tag('rtt', 'mixin', 'title')
    def test_rtt_mixin_title(self):
        super().assertTitleExists()

    @tag('rtt', 'mixin', 'model')
    def test_rtt_mixin_model(self):
        super().assertCorrectModel()

    @tag('rtt', 'mixin', 'form')
    def test_rtt_mixin_form(self):
        super().assertCorrectForm()


class TestSte(CommonMixinsTest):

    def setUp(self) -> None:
        self.mixin = mixins.SteMixin
        self.expected_key = 'ste'
        self.expected_title = "Station Event"
        self.expected_model = models.SteStationEvent
        self.expected_form = forms.SteForm

    @tag('ste', 'mixin', 'key')
    def test_ste_mixin_key(self):
        super().assertKeyExists()

    @tag('ste', 'mixin', 'title')
    def test_ste_mixin_title(self):
        super().assertTitleExists()

    @tag('ste', 'mixin', 'model')
    def test_ste_mixin_model(self):
        super().assertCorrectModel()

    @tag('ste', 'mixin', 'form')
    def test_ste_mixin_form(self):
        super().assertCorrectForm()


class TestStn(CommonMixinsTest):

    def setUp(self) -> None:
        self.mixin = mixins.StnMixin
        self.expected_key = 'stn'
        self.expected_title = "Station"
        self.expected_model = models.StnStation
        self.expected_form = forms.StnForm

    @tag('stn', 'mixin', 'key')
    def test_stn_mixin_key(self):
        super().assertKeyExists()

    @tag('stn', 'mixin', 'title')
    def test_stn_mixin_title(self):
        super().assertTitleExists()

    @tag('stn', 'mixin', 'model')
    def test_stn_mixin_model(self):
        super().assertCorrectModel()

    @tag('stn', 'mixin', 'form')
    def test_stn_mixin_form(self):
        super().assertCorrectForm()


class TestTea(CommonMixinsTest):

    def setUp(self) -> None:
        self.mixin = mixins.TeaMixin
        self.expected_key = 'tea'
        self.expected_title = "Team Member"
        self.expected_model = models.TeaTeamMember
        self.expected_form = forms.TeaForm

    @tag('tea', 'mixin', 'key')
    def test_tea_mixin_key(self):
        super().assertKeyExists()

    @tag('tea', 'mixin', 'title')
    def test_tea_mixin_title(self):
        super().assertTitleExists()

    @tag('tea', 'mixin', 'model')
    def test_tea_mixin_model(self):
        super().assertCorrectModel()

    @tag('tea', 'mixin', 'form')
    def test_tea_mixin_form(self):
        super().assertCorrectForm()


