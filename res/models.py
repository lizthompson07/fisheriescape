from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _, gettext
from shapely.geometry import MultiPoint, Point

from shared_models import models as shared_models
from shared_models.models import SimpleLookup, UnilingualSimpleLookup, UnilingualLookup, MetadataFields
from shared_models.utils import decdeg2dm, dm2decdeg


YES_NO_CHOICES = (
    (True, gettext("Yes")),
    (False, gettext("No")),
)

