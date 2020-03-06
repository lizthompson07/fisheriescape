import os

from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from shared_models import models as shared_models
from shapely.geometry import Polygon, Point, LineString

