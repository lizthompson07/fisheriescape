from django.db import models
from django.contrib.auth.models import User


class Publications(models.Model):
    # year
    # title
    # region
    # division
    # Linkage to national or regional program
    # Human component
    # Ecosystem component

    pub_year = models.DateField(verbose_name="Publication Year")
    pub_title = models.CharField(max_length=255, verbose_name="Publication Title")
    last_modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        ordering = ['-pub_year', 'pub_title']

    def __str__(self):
        return "{}".format(self.pub_title)
