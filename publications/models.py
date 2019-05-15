from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from shared_models import models as shared_models


class Publications(models.Model):
    # year
    # title
    # region
    # division
    # Linkage to national or regional program
    # Human component
    # Ecosystem component

    pub_year = models.DateField(verbose_name=_("Publication Year"))
    pub_title = models.CharField(max_length=255, verbose_name=_("Publication Title"))
    division = models.ForeignKey(shared_models.Division, on_delete=models.DO_NOTHING, blank=True, null=True)
    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now,
                                              verbose_name=_("date last modified"))
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        ordering = ['-pub_year', 'division', 'pub_title']

    def __str__(self):
        return "{}".format(self.pub_title)

    def get_absolute_url(self):
        return reverse('publications:pub_detail', kwargs={'pk': self.pk})
