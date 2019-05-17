from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from shared_models import models as shared_models

import markdown


class Lookup(models.Model):

    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class Theme(Lookup):
    """
        Theme - Lookup table of Themes of which a publication can have multiple
    """
    pass


class HumanComponents(Lookup):
    """
        HumanComponent - Lookup table of Human Components of which a publication can have multiple
    """
    pass


class EcosystemComponents(Lookup):
    """
        EcosystemComponent - Lookup table of Ecosystem Components of which a publication can have multiple
    """
    pass


class SpatialManagement(Lookup):
    """
        SpatialManagement - Lookup table of Spatial Management of which a
        publication can have multiple
    """
    pass


class SustainabilityPillar(Lookup):
    """
        SustainabilityPillar - Lookup table of Pillar of Sustainability of which a
        publication can have multiple
    """
    pass


class ProgramLinkage(Lookup):
    """
        ProgramLinkage - Lookup table of Program Linkage of which a
        publication can have multiple
    """
    pass


class Publications(models.Model):
    # year
    # title
    # division <- region is a part of division
    # Linkage to national or regional program
    # Human component
    # Ecosystem component

    pub_year = models.DateField(verbose_name=_("Publication Year"))
    pub_title = models.CharField(max_length=255, verbose_name=_("Publication Title"))
    division = models.ForeignKey(shared_models.Division, on_delete=models.DO_NOTHING, blank=True, null=True,
                                 verbose_name=_("Division"))
    date_last_modified = models.DateTimeField(blank=True, null=True, default=timezone.now,
                                              verbose_name=_("Date last modified"))

    pub_abstract = models.TextField(verbose_name=_("Abstract"), blank=True, null=True)
    pub_abstract_html = models.TextField(verbose_name=_("Abstract"), blank=True, null=True)

    # Todo: Last modified by isn't currently set in the new or update forms
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True)

    theme = models.ManyToManyField(Theme, verbose_name=_("Theme(s)"))
    human_component = models.ManyToManyField(HumanComponents, verbose_name=_("Human Component(s)"))
    ecosystem_component = models.ManyToManyField(EcosystemComponents, verbose_name=_("Ecosystem Component(s)"))
    spatial_management = models.ManyToManyField(SpatialManagement, verbose_name=_("Spatial Management Designation(s)"))
    sustainability_pillar = models.ManyToManyField(SustainabilityPillar, verbose_name=_("Pillar(s) of Sustainability"))
    program_linkage = models.ManyToManyField(ProgramLinkage, verbose_name=_("Program Linkage(s)"))

    class Meta:
        ordering = ['-pub_year', 'division', 'pub_title']

    def __str__(self):
        return "{}".format(self.pub_title)

    def get_absolute_url(self):
        return reverse('publications:pub_detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        if self.pub_abstract:
            self.pub_abstract_html = markdown.markdown(self.pub_abstract)

        super().save(*args, **kwargs)
