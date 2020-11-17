from whalesdb import mixins, models, forms
from shared_models import models as shared_models

from django.test import TestCase, tag
from django.utils.translation import gettext_lazy as _


class CommonMixinsTest(object):
    mixin = None
    expected_key = None
    expected_title = None
    expected_model = None
    expected_form = None

    def test_key_exists(self):
        self.assertEqual(self.expected_key, self.mixin.key)

    def test_correct_title(self):
        self.assertEqual(self.expected_title, self.mixin.title)

    def test_correct_model(self):
        self.assertEqual(self.expected_model, self.mixin.model)

    def test_correct_form(self):
        self.assertEqual(self.expected_form, self.mixin.form_class)


@tag('cru', 'mixin')
class TestCru(CommonMixinsTest, TestCase):

    def setUp(self) -> None:
        self.mixin = mixins.CruMixin
        self.expected_key = 'cru'
        self.expected_title = _("Cruise")
        self.expected_model = shared_models.Cruise
        self.expected_form = forms.CruForm


@tag('dep', 'mixin')
class TestDep(CommonMixinsTest, TestCase):

    def setUp(self) -> None:
        self.mixin = mixins.DepMixin
        self.expected_key = 'dep'
        self.expected_title = _("Deployment")
        self.expected_model = models.DepDeployment
        self.expected_form = forms.DepForm


@tag('ecc', 'mixin')
class TestEcc(CommonMixinsTest, TestCase):

    def setUp(self) -> None:
        self.mixin = mixins.EccMixin
        self.expected_key = 'ecc'
        self.expected_title = _("Calibration Values")
        self.expected_model = models.EccCalibrationValue
        self.expected_form = forms.EccForm


@tag('eca', 'mixin')
class TestEca(CommonMixinsTest, TestCase):

    def setUp(self) -> None:
        self.mixin = mixins.EcaMixin
        self.expected_key = 'eca'
        self.expected_title = _("Calibration Event")
        self.expected_model = models.EcaCalibrationEvent
        self.expected_form = forms.EcaForm


@tag('ecp', 'mixin')
class TestEcp(CommonMixinsTest, TestCase):

    def setUp(self) -> None:
        self.mixin = mixins.EcpMixin
        self.expected_key = 'ecp'
        self.expected_title = _("Equipment Channel Properties")
        self.expected_model = models.EcpChannelProperty
        self.expected_form = forms.EcpForm


@tag('eda', 'mixin')
class TestEda(CommonMixinsTest, TestCase):

    def setUp(self) -> None:
        self.mixin = mixins.EdaMixin
        self.expected_key = 'eda'
        self.expected_title = _("Equipment Attachment")
        self.expected_model = models.EdaEquipmentAttachment
        self.expected_form = forms.EdaForm


@tag('emm', 'mixin')
class TestEmm(CommonMixinsTest, TestCase):

    def setUp(self) -> None:
        self.mixin = mixins.EmmMixin
        self.expected_key = 'emm'
        self.expected_title = _("Make/Model")
        self.expected_model = models.EmmMakeModel
        self.expected_form = forms.EmmForm


@tag('ehe', 'mixin')
class TestEhe(CommonMixinsTest, TestCase):

    def setUp(self) -> None:
        self.mixin = mixins.EheMixin
        self.expected_key = 'ehe'
        self.expected_title = _("Hydrophone Event")
        self.expected_model = models.EheHydrophoneEvent
        self.expected_form = forms.EheForm


@tag('eqh', 'mixin')
class TestEqh(CommonMixinsTest, TestCase):

    def setUp(self) -> None:
        self.mixin = mixins.EqhMixin
        self.expected_key = 'eqh'
        self.expected_title = _("Hydrophone Properties")
        self.expected_model = models.EqhHydrophoneProperty
        self.expected_form = forms.EqhForm


@tag('eqp', 'mixin')
class TestEqp(CommonMixinsTest, TestCase):

    def setUp(self) -> None:
        self.mixin = mixins.EqpMixin
        self.expected_key = 'eqp'
        self.expected_title = _("Equipment")
        self.expected_model = models.EqpEquipment
        self.expected_form = forms.EqpForm


@tag('eqo', 'mixin')
class TestEqo(CommonMixinsTest, TestCase):

    def setUp(self) -> None:
        self.mixin = mixins.EqoMixin
        self.expected_key = 'eqo'
        self.expected_title = _("Equipment Owner")
        self.expected_model = models.EqoOwner
        self.expected_form = forms.EqoForm


@tag('eqr', 'mixin')
class TestEqr(CommonMixinsTest, TestCase):

    def setUp(self) -> None:
        self.mixin = mixins.EqrMixin
        self.expected_key = 'eqr'
        self.expected_title = _("Recorder Properties")
        self.expected_model = models.EqrRecorderProperties
        self.expected_form = forms.EqrForm


@tag('etr', 'mixin')
class TestEtr(CommonMixinsTest, TestCase):

    def setUp(self) -> None:
        self.mixin = mixins.EtrMixin
        self.expected_key = 'etr'
        self.expected_title = _("Technical Repair Event")
        self.expected_model = models.EtrTechnicalRepairEvent
        self.expected_form = forms.EtrForm


@tag('mor', 'mixin')
class TestMor(CommonMixinsTest, TestCase):

    def setUp(self) -> None:
        self.mixin = mixins.MorMixin
        self.expected_key = 'mor'
        self.expected_title = _("Mooring Setup")
        self.expected_model = models.MorMooringSetup
        self.expected_form = forms.MorForm


@tag('prj', 'mixin')
class TestPrj(CommonMixinsTest, TestCase):

    def setUp(self) -> None:
        self.mixin = mixins.PrjMixin
        self.expected_key = 'prj'
        self.expected_title = _("Project")
        self.expected_model = models.PrjProject
        self.expected_form = forms.PrjForm


@tag('rci', 'mixin')
class TestRci(CommonMixinsTest, TestCase):

    def setUp(self) -> None:
        self.mixin = mixins.RciMixin
        self.expected_key = 'rci'
        self.expected_title = _("Channel Information")
        self.expected_model = models.RciChannelInfo
        self.expected_form = forms.RciForm


@tag('rec', 'mixin')
class TestRec(CommonMixinsTest, TestCase):

    def setUp(self) -> None:
        self.mixin = mixins.RecMixin
        self.expected_key = 'rec'
        self.expected_title = _("Dataset")
        self.expected_model = models.RecDataset
        self.expected_form = forms.RecForm


@tag('ree', 'mixin')
class TestRee(CommonMixinsTest, TestCase):

    def setUp(self) -> None:
        self.mixin = mixins.ReeMixin
        self.expected_key = 'ree'
        self.expected_title = _("Recording Events")
        self.expected_model = models.ReeRecordingEvent
        self.expected_form = forms.ReeForm


@tag('ret', 'mixin')
class TestRet(CommonMixinsTest, TestCase):

    def setUp(self) -> None:
        self.mixin = mixins.RetMixin
        self.expected_key = 'ret'
        self.expected_title = _("Recording Event Type")
        self.expected_model = models.RetRecordingEventType
        self.expected_form = forms.RetForm


@tag('rsc', 'mixin')
class TestRsc(CommonMixinsTest, TestCase):

    def setUp(self) -> None:
        self.mixin = mixins.RscMixin
        self.expected_key = 'rsc'
        self.expected_title = _("Recording Schedule")
        self.expected_model = models.RscRecordingSchedule
        self.expected_form = forms.RscForm


@tag('rst', 'mixin')
class TestRst(CommonMixinsTest, TestCase):

    def setUp(self) -> None:
        self.mixin = mixins.RstMixin
        self.expected_key = 'rst'
        self.expected_title = _("Recording Stage")
        self.expected_model = models.RstRecordingStage
        self.expected_form = forms.RstForm


@tag('rtt', 'mixin')
class TestRtt(CommonMixinsTest, TestCase):

    def setUp(self) -> None:
        self.mixin = mixins.RttMixin
        self.expected_key = 'rtt'
        self.expected_title = _("Time Zone")
        self.expected_model = models.RttTimezoneCode
        self.expected_form = forms.RttForm


@tag('ste', 'mixin')
class TestSte(CommonMixinsTest, TestCase):

    def setUp(self) -> None:
        self.mixin = mixins.SteMixin
        self.expected_key = 'ste'
        self.expected_title = _("Station Event")
        self.expected_model = models.SteStationEvent
        self.expected_form = forms.SteForm


@tag('stn', 'mixin')
class TestStn(CommonMixinsTest, TestCase):

    def setUp(self) -> None:
        self.mixin = mixins.StnMixin
        self.expected_key = 'stn'
        self.expected_title = _("Station")
        self.expected_model = models.StnStation
        self.expected_form = forms.StnForm


@tag('tea', 'mixin')
class TestTea(CommonMixinsTest, TestCase):

    def setUp(self) -> None:
        self.mixin = mixins.TeaMixin
        self.expected_key = 'tea'
        self.expected_title = _("Team Member")
        self.expected_model = models.TeaTeamMember
        self.expected_form = forms.TeaForm
