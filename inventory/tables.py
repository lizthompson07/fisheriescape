import django_tables2 as tables
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.templatetags.static import static
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy

from lib.templatetags.custom_filters import percentage
from .models import Resource


class ResourceTable(tables.Table):
    """
        {"name": 'review_status_display|{}'.format(gettext_lazy("review status"))}
    """

    #
    fav = tables.Column(verbose_name=gettext_lazy(" "), empty_values=(), attrs=dict(th={"class": "w-5"}))
    t_title = tables.Column(verbose_name=gettext_lazy("Title"), empty_values=(), attrs=dict(th={"class": "w-30"}))
    external_links = tables.Column(verbose_name=gettext_lazy("External_links"), empty_values=())
    prev_cert = tables.Column(verbose_name=gettext_lazy("Previous time certified"), empty_values=())
    rating = tables.Column(verbose_name=gettext_lazy("Completeness rating"), empty_values=())
    review_status = tables.Column(verbose_name=gettext_lazy("Review status"), empty_values=())

    class Meta:
        model = Resource
        template_name = "django_tables2/bootstrap4.html"
        fields = (
            "fav",
            "t_title",
            "external_links",
            "resource_type",
            "region",
            "section",
            "prev_cert",
            "rating",
            "review_status",
        )
        attrs = {"class": "table table-sm table-hover"}

    def render_t_title(self, record):
        return mark_safe(f'<a href="{reverse("inventory:resource_detail", args=[record.id])}">{record.t_title}</a>')

    def render_rating(self, record):
        return percentage(record.completedness_rating)

    def render_review_status(self, record):
        return mark_safe(record.review_status_display)

    def render_fav(self, record):
        user = self.context.get("request").user
        if record.favourited_by.filter(id=user.id).exists():
            return mark_safe(
                f'<a href="{reverse("inventory:remove_favourites", args=[record.id])}" data-toggle="tooltip" title="remove from favourites"><span class="mdi mdi-star"></span></a>')
        elif record.resource_people2.filter(user=user).exists():
            return mark_safe(f'<span class="mdi mdi-account-multiple"></span></a>')
        else:
            return mark_safe(
                f'<a href="{reverse("inventory:add_favourites", args=[record.id])}" data-toggle="tooltip" title="add to favourites"><span class="mdi mdi-star-outline text-secondary"></span></a>')

    def render_external_links(self, record):
        payload = str()
        if record.fgp_url:
            img_url = static('img/icons/fgp.png')
            payload += f'<a class="stop-blank mx-1" href="{{ object.fgp_url }}" data-toggle="tooltip" title="Open URL in the Federal Geospatial Platform"> <img src="{img_url}" alt="" width="15px"> </a>'
        if record.public_url:
            img_url = static('img/icons/canada.png')
            payload += f'<a class="stop-blank mx-1" href="{{ object.public_url }}" data-toggle="tooltip" title="Open URL in the Open Government Portal"> <img src="{img_url}" alt="" width="15px"> </a>'
        return mark_safe(payload)

    def render_prev_cert(self, record):
        if record.certification_history.exists():
            return naturaltime(record.certification_history.first().certification_date)
        else:
            return mark_safe(f'<span class="red-font"><b>Never</b></span>')
