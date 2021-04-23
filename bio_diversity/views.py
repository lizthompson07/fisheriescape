import datetime
import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.utils import timezone
from django.views.generic import TemplateView, DetailView, DeleteView
from shapely.geometry import box

from shared_models.views import CommonAuthCreateView, CommonAuthUpdateView, CommonTemplateView, \
    CommonFormsetView, CommonHardDeleteView, CommonFormView, CommonFilterView
from django.urls import reverse_lazy, reverse
from django import forms
from bio_diversity.forms import HelpTextFormset, CommentKeywordsFormset
from django.forms.models import model_to_dict
from . import mixins, filters, utils, models, reports
from datetime import date
import pytz
from django.utils.translation import gettext_lazy as _

from .utils import get_cont_evnt


class IndexTemplateView(TemplateView):
    nav_menu = 'bio_diversity/bio_diversity_nav_menu.html'
    site_css = 'bio_diversity/bio_diversity_css.css'
    home_url_name = "bio_diversity:index"

    template_name = 'bio_diversity/index.html'


class SiteLoginRequiredMixin(UserPassesTestMixin):

    def test_func(self):
        if not hasattr(self, "admin_only"):
            self.admin_only = True

        if self.admin_only:
            return utils.bio_diverisity_admin(self.request.user)
        else:
            return utils.bio_diverisity_authorized(self.request.user)


class AdminIndexTemplateView(TemplateView):
    nav_menu = 'bio_diversity/bio_diversity_nav_menu.html'
    site_css = 'bio_diversity/bio_diversity_css.css'
    home_url_name = "bio_diversity:index"

    template_name = 'bio_diversity/admin_index.html'

    def get(self, request, *args, **kwargs):
        if not utils.bio_diverisity_admin(self.request.user):
            return HttpResponseRedirect(reverse_lazy('accounts:login_required'))
        else:
            context = self.get_context_data(**kwargs)
            return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        # we want to update the context with the context vars added by CommonMixin classes
        context = super().get_context_data(**kwargs)
        context["auth"] = utils.bio_diverisity_admin(self.request.user)
        return context


class CodesIndexTemplateView(TemplateView):
    nav_menu = 'bio_diversity/bio_diversity_nav_menu.html'
    site_css = 'bio_diversity/bio_diversity_css.css'
    home_url_name = "bio_diversity:index"

    template_name = 'bio_diversity/codes_index.html'

    def get(self, request, *args, **kwargs):
        if not utils.bio_diverisity_admin(self.request.user):
            return HttpResponseRedirect(reverse_lazy('accounts:login_required'))
        else:
            context = self.get_context_data(**kwargs)
            return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        # we want to update the context with the context vars added by CommonMixin classes
        context = super().get_context_data(**kwargs)
        context["auth"] = utils.bio_diverisity_admin(self.request.user)
        return context


class FacicIndexTemplateView(TemplateView):
    nav_menu = 'bio_diversity/bio_diversity_nav_menu.html'
    site_css = 'bio_diversity/bio_diversity_css.css'
    home_url_name = "bio_diversity:index"

    template_name = 'bio_diversity/facic_index.html'

    def get(self, request, *args, **kwargs):
        if not utils.bio_diverisity_admin(self.request.user):
            return HttpResponseRedirect(reverse_lazy('accounts:login_required'))
        else:
            context = self.get_context_data(**kwargs)
            return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        # we want to update the context with the context vars added by CommonMixin classes
        context = super().get_context_data(**kwargs)
        context["auth"] = utils.bio_diverisity_admin(self.request.user)
        return context


class ProgIndexTemplateView(TemplateView):
    nav_menu = 'bio_diversity/bio_diversity_nav_menu.html'
    site_css = 'bio_diversity/bio_diversity_css.css'
    home_url_name = "bio_diversity:index"

    template_name = 'bio_diversity/prog_index.html'

    def get(self, request, *args, **kwargs):
        if not utils.bio_diverisity_admin(self.request.user):
            return HttpResponseRedirect(reverse_lazy('accounts:login_required'))
        else:
            context = self.get_context_data(**kwargs)
            return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        # we want to update the context with the context vars added by CommonMixin classes
        context = super().get_context_data(**kwargs)
        context["auth"] = utils.bio_diverisity_admin(self.request.user)
        return context


# CommonCreate Extends the UserPassesTestMixin used to determine if a user has
# has the correct privileges to interact with Creation Views
# --------------------CREATE VIEWS----------------------------------------
class CommonCreate(CommonAuthCreateView):

    nav_menu = 'bio_diversity/bio_diversity_nav.html'
    site_css = 'bio_diversity/bio_diversity.css'
    home_url_name = "bio_diversity:index"

    def get_initial(self):
        init = super().get_initial()

        init["created_by"] = self.request.user.username
        init["created_date"] = date.today

        if hasattr(self.model, "start_date"):
            init["start_date"] = date.today

        return init

    # Upon success most creation views will be redirected to their respective 'CommonList' view. To send
    # a successful creation view somewhere else, override this method
    def get_success_url(self):
        success_url = self.success_url if self.success_url else reverse_lazy("bio_diversity:list_{}".format(self.key))

        if self.kwargs.get("pop"):
            # create views intended to be pop out windows should close the window upon success
            success_url = reverse_lazy("shared_models:close_me_no_refresh")

        return success_url

    # overrides the UserPassesTestMixin test to check that a user belongs to the bio_diversity_admin group
    def test_func(self):
        if self.admin_only:
            return utils.bio_diverisity_admin(self.request.user)
        else:
            return utils.bio_diverisity_authorized(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editable'] = context['auth']
        context['help_text_dict'] = utils.get_help_text_dict(self.model)

        return context


class AnidcCreate(mixins.AnidcMixin, CommonCreate):
    pass


class AnixCreate(mixins.AnixMixin, CommonCreate):
    def get_initial(self):
        initial = super().get_initial()
        if 'evnt' in self.kwargs:
            initial['evnt_id'] = self.kwargs['evnt']

        if 'visible' in self.kwargs:
            for field in self.get_form_class().base_fields:
                if field in self.kwargs['visible']:
                    self.get_form_class().base_fields[field].widget = forms.Select()
                else:
                    self.get_form_class().base_fields[field].widget = forms.HiddenInput()
        else:
            for field in self.get_form_class().base_fields:
                self.get_form_class().base_fields[field].widget = forms.Select()

        return initial


class AdscCreate(mixins.AdscMixin, CommonCreate):
    pass


class CntCreate(mixins.CntMixin, CommonCreate):
    def get_initial(self):
        initial = super().get_initial()
        if 'loc' in self.kwargs:
            initial['loc_id'] = self.kwargs['loc']


class CntcCreate(mixins.CntcMixin, CommonCreate):
    pass


class CntdCreate(mixins.CntdMixin, CommonCreate):
    pass


class CollCreate(mixins.CollMixin, CommonCreate):
    pass


class ContdcCreate(mixins.ContdcMixin, CommonCreate):
    pass


class ContxCreate(mixins.ContxMixin, CommonCreate):
    def get_initial(self):
        initial = super().get_initial()
        if 'evnt' in self.kwargs:
            initial['evnt_id'] = self.kwargs['evnt']

        if 'visible' in self.kwargs:
            for field in self.get_form_class().base_fields:
                if field in self.kwargs['visible']:
                    self.get_form_class().base_fields[field].widget = forms.Select()
                else:
                    self.get_form_class().base_fields[field].widget = forms.HiddenInput()
        else:
            for field in self.get_form_class().base_fields:
                self.get_form_class().base_fields[field].widget = forms.Select()

        return initial


class CdscCreate(mixins.CdscMixin, CommonCreate):
    pass


class CupCreate(mixins.CupMixin, CommonCreate):
    pass


class CupdCreate(mixins.CupdMixin, CommonCreate):
    pass


class DataCreate(mixins.DataMixin, CommonCreate):
    template_name = 'bio_diversity/data_entry_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_initial(self):
        init = super().get_initial()
        if 'evnt' in self.kwargs:
            evnt = models.Event.objects.filter(pk=self.kwargs["evnt"]).select_related("evntc_id", "facic_id").get()
            init['evnt_id'] = self.kwargs['evnt']
            evntc = evnt.evntc_id
            init['evntc_id'] = evntc
            init['facic_id'] = evnt.facic_id
            self.get_form_class().base_fields["data_csv"].required = True
            self.get_form_class().base_fields["trof_id"].required = False

            self.get_form_class().base_fields["evnt_id"].widget = forms.HiddenInput()
            self.get_form_class().base_fields["evntc_id"].widget = forms.HiddenInput()
            self.get_form_class().base_fields["facic_id"].widget = forms.HiddenInput()
            if evntc.__str__() in ["Electrofishing", "Smolt Wheel Collection", "Bypass Collection"]:
                self.get_form_class().base_fields["tank_id"].widget = forms.Select(attrs={"class": "chosen-select-contains"})
                self.get_form_class().base_fields["tank_id"].required = True
            else:
                self.get_form_class().base_fields["tank_id"].required = False
                self.get_form_class().base_fields["tank_id"].widget = forms.HiddenInput()
            if evntc.__str__() in ["Egg Development", "Measuring"]:
                self.get_form_class().base_fields["trof_id"].widget = forms.Select(
                    attrs={"class": "chosen-select-contains"})
                self.get_form_class().base_fields["data_type"].required = True
                if evntc.__str__() == "Egg Development":
                    data_types = ((None, "---------"), ('Temperature', 'Temperature'), ('Picks', 'Picks'))
                elif evntc.__str__() == "Measuring":
                    data_types = ((None, "---------"), ('Individual', 'Individual'), ('Group', 'Group'))
                self.get_form_class().base_fields["data_type"] = forms.ChoiceField(choices=data_types, label=_("Type of data entry"))
            else:
                self.get_form_class().base_fields["data_type"].required = False
                self.get_form_class().base_fields["data_type"].widget = forms.HiddenInput()
        return init

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['java_script'] = 'bio_diversity/_entry_data_js.html'
        if 'evnt' in self.kwargs:
            evnt_code = models.Event.objects.filter(pk=self.kwargs["evnt"]).get().evntc_id.__str__().lower()
            facility_code = models.Event.objects.filter(pk=self.kwargs["evnt"]).get().facic_id.__str__().lower()
            context["title"] = "Add {} data".format(evnt_code)
            context["template_url"] = 'data_templates/{}-{}.xlsx'.format(facility_code, evnt_code)
            if evnt_code == "spawning":
                context["template_url"] = 'data_templates/{}-{}.xls'.format(facility_code, evnt_code)
            context["template_name"] = "{}-{}".format(facility_code, evnt_code)
        return context

    def get_success_url(self):
        success_url = reverse_lazy("bio_diversity:data_log")
        return success_url


class DrawCreate(mixins.DrawMixin, CommonCreate):
    pass


class EnvCreate(mixins.EnvMixin, CommonCreate):
    def get_initial(self):
        init = super().get_initial()
        init["start_date"] = date.today()
        if 'loc' in self.kwargs:
            init['loc_id'] = self.kwargs['loc']
        return init


class EnvcCreate(mixins.EnvcMixin, CommonCreate):
    pass


class EnvcfCreate(mixins.EnvcfMixin, CommonCreate):
    pass


class EnvscCreate(mixins.EnvscMixin, CommonCreate):
    pass


class EnvtCreate(mixins.EnvtMixin, CommonCreate):
    pass


class EnvtcCreate(mixins.EnvtcMixin, CommonCreate):
    pass


class EvntCreate(mixins.EvntMixin, CommonCreate):
    def get_success_url(self):
        success_url = self.success_url if self.success_url else reverse_lazy("bio_diversity:details_{}".format(self.key), kwargs={'pk': self.object.pk})

        if self.kwargs.get("pop"):
            # create views intended to be pop out windows should close the window upon success
            success_url = reverse_lazy("shared_models:close_me_no_refresh")

        return success_url


class EvntcCreate(mixins.EvntcMixin, CommonCreate):
    pass


class EvntfCreate(mixins.EvntfMixin, CommonCreate):
    def get_initial(self):
        init = super().get_initial()
        if 'evnt_pk' in self.kwargs:
            init['evnt_id'] = self.kwargs['evnt_pk']
            self.get_form_class().base_fields["evnt_id"].widget = forms.HiddenInput()

        return init


class EvntfcCreate(mixins.EvntfcMixin, CommonCreate):
    pass


class FacicCreate(mixins.FacicMixin, CommonCreate):
    pass


class FecuCreate(mixins.FecuMixin, CommonCreate):
    pass


class FeedCreate(mixins.FeedMixin, CommonCreate):
    pass


class FeedcCreate(mixins.FeedcMixin, CommonCreate):
    pass


class FeedmCreate(mixins.FeedmMixin, CommonCreate):
    pass


class GrpCreate(mixins.GrpMixin, CommonCreate):

    def form_valid(self, form):
        """If the form is valid, save the associated model and add an X ref object."""
        self.object = form.save()
        if 'evnt' in self.kwargs:
            anix_link = models.AniDetailXref(evnt_id=models.Event.objects.filter(pk=self.kwargs['evnt']).get(),
                                             grp_id=self.object, created_by=self.object.created_by,
                                             created_date=self.object.created_date)
            anix_link.clean()
            anix_link.save()
        return super().form_valid(form)


class GrpdCreate(mixins.GrpdMixin, CommonCreate):
    pass


class HeatCreate(mixins.HeatMixin, CommonCreate):
    pass


class HeatdCreate(mixins.HeatdMixin, CommonCreate):
    pass


class ImgCreate(mixins.ImgMixin, CommonCreate):
    def get_initial(self):
        initial = super().get_initial()
        if 'feature' in self.kwargs:
            for field in self.get_form_class().base_fields:
                if self.kwargs['feature'] in field:
                    initial[field] = self.kwargs["feature_id"]
                if field not in ["imgc_id", "img_png"]:
                    self.get_form_class().base_fields[field].widget = forms.HiddenInput()
        return initial


class ImgcCreate(mixins.ImgcMixin, CommonCreate):
    pass


class IndvCreate(mixins.IndvMixin, CommonCreate):

    def get_initial(self):
        init = super().get_initial()
        if 'clone' in self.kwargs:
            parent_indv = models.Individual.objects.filter(pk=self.kwargs["clone_id"]).get()
            for name, value in model_to_dict(parent_indv).items():
                if name not in ["ufid", "pit_tag", "created_by", "created_date"]:
                    init[name] = value
        return init

    def form_valid(self, form):
        """If the form is valid, save the associated model and add an X ref object."""
        self.object = form.save()
        if 'evnt' in self.kwargs:
            anix_link = models.AniDetailXref(evnt_id=models.Event.objects.filter(pk=self.kwargs['evnt']).get(),
                                             indv_id=self.object, created_by=self.object.created_by,
                                             created_date=self.object.created_date)
            anix_link.clean()
            anix_link.save()
        return super().form_valid(form)


class IndvdCreate(mixins.IndvdMixin, CommonCreate):
    pass


class IndvtCreate(mixins.IndvtMixin, CommonCreate):
    pass


class IndvtcCreate(mixins.IndvtcMixin, CommonCreate):
    pass


class InstCreate(mixins.InstMixin, CommonCreate):
    pass


class InstcCreate(mixins.InstcMixin, CommonCreate):
    pass


class InstdCreate(mixins.InstdMixin, CommonCreate):
    pass


class InstdcCreate(mixins.InstdcMixin, CommonCreate):
    pass


class LocCreate(mixins.LocMixin, CommonCreate):
    pass


class LoccCreate(mixins.LoccMixin, CommonCreate):
    pass


class OrgaCreate(mixins.OrgaMixin, CommonCreate):
    pass


class PairCreate(mixins.PairMixin, CommonCreate):
    pass


class PercCreate(mixins.PercMixin, CommonCreate):
    pass


class PrioCreate(mixins.PrioMixin, CommonCreate):
    pass


class ProgCreate(mixins.ProgMixin, CommonCreate):
    pass


class ProgaCreate(mixins.ProgaMixin, CommonCreate):
    pass


class ProtCreate(mixins.ProtMixin, CommonCreate):
    def get_initial(self):
        initial = super().get_initial()
        if 'prog' in self.kwargs:
            initial['prog_id'] = self.kwargs['prog']
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['java_script'] = 'bio_diversity/_entry_prot_js.html'

        return context


class ProtcCreate(mixins.ProtcMixin, CommonCreate):
    pass


class ProtfCreate(mixins.ProtfMixin, CommonCreate):
    def get_initial(self):
        initial = super().get_initial()
        if 'prot' in self.kwargs:
            initial['prot_id'] = self.kwargs['prot']
        return initial


class QualCreate(mixins.QualMixin, CommonCreate):
    pass


class RelcCreate(mixins.RelcMixin, CommonCreate):
    def get_initial(self):
        initial = super().get_initial()
        if 'n' in self.kwargs:
            initial['max_lat'] = round(float(self.kwargs['n']), 5)
        if 's' in self.kwargs:
            initial['min_lat'] = round(float(self.kwargs['s']), 5)
        if 'w' in self.kwargs:
            initial['min_lon'] = round(float(self.kwargs['w']), 5)
        if 'e' in self.kwargs:
            initial['max_lon'] = round(float(self.kwargs['e']), 5)
        return initial


class RiveCreate(mixins.RiveMixin, CommonCreate):
    pass


class RoleCreate(mixins.RoleMixin, CommonCreate):
    pass


class SampCreate(mixins.SampMixin, CommonCreate):
    pass


class SampcCreate(mixins.SampcMixin, CommonCreate):
    pass


class SampdCreate(mixins.SampdMixin, CommonCreate):
    pass


class SireCreate(mixins.SireMixin, CommonCreate):
    def get_initial(self):
        initial = super().get_initial()
        if 'pair' in self.kwargs:
            initial['pair_id'] = self.kwargs['pair']
        return initial


class SpwndCreate(mixins.SpwndMixin, CommonCreate):
    pass


class SpwndcCreate(mixins.SpwndcMixin, CommonCreate):
    pass


class SpwnscCreate(mixins.SpwnscMixin, CommonCreate):
    pass


class SpecCreate(mixins.SpecMixin, CommonCreate):
    pass


class StokCreate(mixins.StokMixin, CommonCreate):
    pass


class SubrCreate(mixins.SubrMixin, CommonCreate):
    pass


class TankCreate(mixins.TankMixin, CommonCreate):
    def form_valid(self, form):
        """If the form is valid, save the associated model and add an X ref object."""
        self.object = form.save()
        if 'evnt' in self.kwargs:
            contx_link = models.ContainerXRef(evnt_id=models.Event.objects.filter(pk=self.kwargs['evnt']).get(),
                                              tank_id=self.object, created_by=self.object.created_by,
                                              created_date=self.object.created_date)
            contx_link.clean()
            contx_link.save()
        return super().form_valid(form)


class TankdCreate(mixins.TankdMixin, CommonCreate):
    pass


class TeamCreate(mixins.TeamMixin, CommonCreate):
    pass


class TrayCreate(mixins.TrayMixin, CommonCreate):
    def form_valid(self, form):
        """If the form is valid, save the associated model and add an X ref object."""
        self.object = form.save()
        if 'evnt' in self.kwargs:
            contx_link = models.ContainerXRef(evnt_id=models.Event.objects.filter(pk=self.kwargs['evnt']).get(),
                                              tank_id=self.object, created_by=self.object.created_by,
                                              created_date=self.object.created_date)
            contx_link.clean()
            contx_link.save()
        return super().form_valid(form)


class TraydCreate(mixins.TraydMixin, CommonCreate):
    pass


class TribCreate(mixins.TribMixin, CommonCreate):
    pass


class TrofCreate(mixins.TrofMixin, CommonCreate):
    def form_valid(self, form):
        """If the form is valid, save the associated model and add an X ref object."""
        self.object = form.save()
        if 'evnt' in self.kwargs:
            contx_link = models.ContainerXRef(evnt_id=models.Event.objects.filter(pk=self.kwargs['evnt']).get(),
                                              trof_id=self.object, created_by=self.object.created_by,
                                              created_date=self.object.created_date)
            contx_link.clean()
            contx_link.save()
        return super().form_valid(form)


class TrofdCreate(mixins.TrofdMixin, CommonCreate):
    pass


class UnitCreate(mixins.UnitMixin, CommonCreate):
    pass


# ---------------------------DETAIL VIEWS-----------------------------------------------
class CommonDetails(DetailView):
    # default template to use to create a details view
    template_name = "bio_diversity/bio_details.html"

    # title to display on the list page
    title = None

    # key used for creating default list and update URLs in the get_context_data method
    key = None

    # URL linking the details page back to the proper list
    list_url = None
    update_url = None

    # By default detail objects are editable, set to false to remove update buttons
    editable = True

    img = False

    def get_auth(self):
        if self.admin_only:
            return utils.bio_diverisity_admin(self.request.user)
        else:
            return utils.bio_diverisity_authorized(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["table_list"] = []
        context["context_dict"] = {}

        if self.title:
            context['title'] = self.title

        if self.fields:
            context['fields'] = self.fields

        if "back" in self.kwargs:
            context['list_url'] = "bio_diversity:details_{}".format(self.kwargs["back"])
            context['back'] = True
            context['back_id'] = self.kwargs["back_id"]
        else:
            context['list_url'] = self.list_url if self.list_url else "bio_diversity:list_{}".format(self.key)
        context['update_url'] = self.update_url if self.update_url else "bio_diversity:update_{}".format(self.key)
        # for the most part if the user is authorized then the content is editable
        # but extending classes can choose to make content not editable even if the user is authorized
        context['auth'] = self.get_auth()
        context['editable'] = context['auth'] and self.editable
        context["model_key"] = self.key

        if self.img:
            context["table_list"].extend(["img"])
            context["img_object"] = models.Image.objects.first()
            context["img_field_list"] = [
                "img_png",
                "imgc_id",
            ]

        return context


class CommonContDetails(CommonDetails):
    template_name = 'bio_diversity/details_cont.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cont_pk = self.object.pk
        arg_name = "contx_id__{}_id_id".format(self.key)
        env_set = models.EnvCondition.objects.filter(**{arg_name: cont_pk}).select_related("envc_id", "envsc_id")
        env_field_list = ["envc_id", "envsc_id", "start_datetime", "env_val", ]
        obj_mixin = mixins.EnvMixin
        context["context_dict"]["env"] = {"div_title": "Environment Conditions",
                                          "sub_model_key": obj_mixin.key,
                                          "objects_list": env_set,
                                          "field_list": env_field_list,
                                          "single_object": obj_mixin.model.objects.first()}

        cnt_set = models.Count.objects.filter(**{arg_name: cont_pk}).select_related("cntc_id")
        cnt_field_list = ["cntc_id", "cnt", "est", "date"]
        obj_mixin = mixins.CntMixin
        context["context_dict"]["cnt"] = {"div_title": "Counts",
                                          "sub_model_key": obj_mixin.key,
                                          "objects_list": cnt_set,
                                          "field_list": cnt_field_list,
                                          "single_object": obj_mixin.model.objects.first()}

        envt_set = models.EnvTreatment.objects.filter(**{arg_name: cont_pk}).select_related("envtc_id", "unit_id")
        envt_field_list = ["envtc_id", "amt", "unit_id", "concentration_str", "duration", ]
        obj_mixin = mixins.EnvtMixin
        context["context_dict"]["envt"] = {"div_title": "Container Treatments",
                                           "sub_model_key": obj_mixin.key,
                                           "objects_list": envt_set,
                                           "field_list": envt_field_list,
                                           "single_object": obj_mixin.model.objects.first()}

        indv_list, grp_list = self.object.fish_in_cont(select_fields=["indv_id__grp_id__stok_id", "indv_id__grp_id__coll_id"])
        indv_field_list = ["ufid", "pit_tag", "grp_id", ]
        obj_mixin = mixins.IndvMixin
        context["context_dict"]["indv_cont"] = {"div_title": "Individuals in Container",
                                                "sub_model_key": obj_mixin.key,
                                                "objects_list": indv_list,
                                                "field_list": indv_field_list,
                                                "single_object": obj_mixin.model.objects.first()}

        grp_field_list = ["stok_id", "coll_id", "spec_id", ]
        obj_mixin = mixins.GrpMixin
        context["context_dict"]["grp_cont"] = {"div_title": "Groups in Container",
                                               "sub_model_key": obj_mixin.key,
                                               "objects_list": grp_list,
                                               "field_list": grp_field_list,
                                               "single_object": obj_mixin.model.objects.first()}

        context["table_list"].extend(["grp_cont", "indv_cont", "env", "envt", "cnt"])

        return context


class AnidcDetails(mixins.AnidcMixin, CommonDetails):
    fields = ["name", "nom", "description_en", "description_fr", "min_val", "max_val", "unit_id", "ani_subj_flag",
              "created_by", "created_date", ]


class AnixDetails(mixins.AnixMixin, CommonDetails):
    fields = ["evnt_id", "loc_id", "indvt_id", "indv_id", "pair_id", "grp_id", "created_by",
              "created_date", ]


class AdscDetails(mixins.AdscMixin, CommonDetails):
    fields = ["anidc_id", "name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class CntDetails(mixins.CntMixin, CommonDetails):
    fields = ["loc_id", "cntc_id", "spec_id", "cnt", "est", "comments", "created_by", "created_date", ]

    def get_context_data(self, **kwargs):
        # use this to pass sire fields/sample object to template
        context = super().get_context_data(**kwargs)
        context["table_list"].extend(["cntd"])

        cntd_set = self.object.count_details.all()
        cntd_field_list = ["anidc_id", "adsc_id", "det_val"]
        obj_mixin = mixins.CntdMixin
        context["context_dict"]["cntd"] = {"div_title": "Count Details",
                                           "sub_model_key": obj_mixin.key,
                                           "objects_list": cntd_set,
                                           "field_list": cntd_field_list,
                                           "single_object": obj_mixin.model.objects.first()}

        return context


class CntcDetails(mixins.CntcMixin, CommonDetails):
    fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class CntdDetails(mixins.CntdMixin, CommonDetails):
    fields = ["cnt_id", "anidc_id", "adsc_id", "det_val", "qual_id", "comments", "created_by", "created_date", ]


class CollDetails(mixins.CollMixin, CommonDetails):
    fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class ContdcDetails(mixins.ContdcMixin, CommonDetails):
    fields = ["name", "nom", "description_en", "description_fr", "min_val", "max_val", "unit_id", "cont_subj_flag",
              "created_by", "created_date", ]


class ContxDetails(mixins.ContxMixin, CommonDetails):
    fields = ["evnt_id", "cup_id", "draw_id", "heat_id", "tank_id", "tray_id", "trof_id", "created_by", "created_date"]


class CdscDetails(mixins.CdscMixin, CommonDetails):
    fields = ["contdc_id", "name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class CupDetails(mixins.CupMixin, CommonContDetails):
    fields = ["name", "nom", "draw_id", "description_en", "description_fr", "start_date", "end_date",
              "created_by", "created_date", ]


class CupdDetails(mixins.CupdMixin, CommonDetails):
    fields = ["cup_id", "contdc_id", "det_value", "cdsc_id", "start_date", "end_date", "det_valid", "comments",
              "created_by", "created_date", ]


class DrawDetails(mixins.DrawMixin, CommonDetails):
    fields = ["heat_id", "name", "nom", "description_en", "description_fr", "created_by", "created_date", ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["table_list"].extend(["cup"])

        cup_set = self.object.cups.all()
        cup_field_list = ["name", ]
        obj_mixin = mixins.CupMixin
        context["context_dict"]["cup"] = {"div_title": "Cups in Drawer",
                                          "sub_model_key": obj_mixin.key,
                                          "objects_list": cup_set,
                                          "field_list": cup_field_list,
                                          "single_object": obj_mixin.model.objects.first()}
        return context


class EnvDetails(mixins.EnvMixin, CommonDetails):
    template_name = 'bio_diversity/details_env.html'
    fields = ["loc_id", "inst_id", "envc_id", "env_val", "envsc_id", "start_date|Start Date", "start_time|Start Time",
              "end_date|End Date", "end_time|End Time", "env_avg", "qual_id", "comments", "created_by", "created_date"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["envcf_object"] = models.EnvCondFile.objects.first()
        context["envcf_field_list"] = [
            "env_pdf",
            "created_date",
        ]

        return context


class EnvcDetails(mixins.EnvcMixin, CommonDetails):
    fields = ["name", "nom", "description_en", "description_fr", "min_val", "max_val", "unit_id", "env_subj_flag",
              "created_by", "created_date", ]


class EnvcfDetails(mixins.EnvcfMixin, CommonDetails):
    template_name = 'bio_diversity/details_envcf.html'
    fields = ["env_id", "env_pdf", "comments", "created_by", "created_date", ]


class EnvscDetails(mixins.EnvscMixin, CommonDetails):
    fields = ["name", "nom", "envc_id", "description_en", "description_fr", "created_by", "created_date", ]


class EnvtDetails(mixins.EnvtMixin, CommonDetails):
    fields = ["envtc_id", "lot_num", "amt", "unit_id", "concentration_str", "duration", "comments", "created_by",
              "created_date", ]


class EnvtcDetails(mixins.EnvtcMixin, CommonDetails):
    fields = ["name", "nom", "rec_dose", "manufacturer", "description_en", "description_fr", "created_by",
              "created_date", ]


class EvntDetails(mixins.EvntMixin, CommonDetails):
    fields = ["facic_id", "evntc_id", "perc_id", "prog_id", "start_date|Start Date", "start_time|Start Time",
              "end_date|End Date", "end_time|End Time", "comments", "created_by", "created_date", ]

    def get_context_data(self, **kwargs):
        # use this to pass sire fields/sample object to template
        context = super().get_context_data(**kwargs)
        loc_set = self.object.location.all()
        loc_field_list = ["locc_id", "rive_id", "subr_id", "start_date|Start Date"]
        obj_mixin = mixins.LocMixin
        context["context_dict"]["loc"] = {"div_title": "{} Details".format(obj_mixin.title),
                                          "sub_model_key": obj_mixin.key,
                                          "objects_list": loc_set,
                                          "field_list": loc_field_list,
                                          "single_object": obj_mixin.model.objects.first()}

        indv_set = models.Individual.objects.filter(animal_details__evnt_id=self.object,
                                                    ).distinct().select_related("grp_id__stok_id", "grp_id__coll_id")
        indv_field_list = ["ufid", "pit_tag", "grp_id", "indv_valid"]
        obj_mixin = mixins.IndvMixin
        context["context_dict"]["indv"] = {"div_title": "{} Details".format(obj_mixin.title),
                                           "sub_model_key": obj_mixin.key,
                                           "objects_list": indv_set,
                                           "field_list": indv_field_list,
                                           "single_object": obj_mixin.model.objects.first()}

        grp_set = models.Group.objects.filter(animal_details__evnt_id=self.object,
                                              ).distinct().select_related("stok_id", "coll_id", "spec_id")
        grp_field_list = ["stok_id", "coll_id", "spec_id", ]
        obj_mixin = mixins.GrpMixin
        context["context_dict"]["grp"] = {"div_title": "{} Details".format(obj_mixin.title),
                                          "sub_model_key": obj_mixin.key,
                                          "objects_list": grp_set,
                                          "field_list": grp_field_list,
                                          "single_object": obj_mixin.model.objects.first()}

        tank_set = models.Tank.objects.filter(contxs__evnt_id=self.object).distinct()
        tank_field_list = ["name"]
        obj_mixin = mixins.TankMixin
        context["context_dict"]["tank"] = {"div_title": "{} Details".format(obj_mixin.title),
                                           "sub_model_key": obj_mixin.key,
                                           "objects_list": tank_set,
                                           "field_list": tank_field_list,
                                           "single_object": obj_mixin.model.objects.first()}

        trof_set = models.Trough.objects.filter(contxs__evnt_id=self.object).distinct()
        trof_field_list = ["name"]
        obj_mixin = mixins.TrofMixin
        context["context_dict"]["trof"] = {"div_title": "{} Details".format(obj_mixin.title),
                                           "sub_model_key": obj_mixin.key,
                                           "objects_list": trof_set,
                                           "field_list": trof_field_list,
                                           "single_object": obj_mixin.model.objects.first()}

        heat_set = models.HeathUnit.objects.filter(contxs__evnt_id=self.object).distinct()
        heat_field_list = ["name"]
        obj_mixin = mixins.HeatMixin
        context["context_dict"]["heat"] = {"div_title": "{} Details".format(obj_mixin.title),
                                           "sub_model_key": obj_mixin.key,
                                           "objects_list": heat_set,
                                           "field_list": heat_field_list,
                                           "single_object": obj_mixin.model.objects.first()}

        prot_set = models.Protocol.objects.filter(prog_id=self.object.prog_id, evntc_id=self.object.evntc_id).distinct()
        prot_field_list = ["name", "evntc_id", "start_date", "end_date", ]
        obj_mixin = mixins.ProtMixin
        context["context_dict"]["prot"] = {"div_title": "{} Details".format(obj_mixin.title),
                                           "sub_model_key": obj_mixin.key,
                                           "objects_list": prot_set,
                                           "field_list": prot_field_list,
                                           "single_object": obj_mixin.model.objects.first()}

        pair_set = models.Pairing.objects.filter(animal_details__evnt_id=self.object
                                                 ).distinct().select_related("indv_id")
        pair_field_list = ["start_date", "indv_id", "cross", ]
        obj_mixin = mixins.PairMixin
        context["context_dict"]["pair"] = {"div_title": "{} Details".format(obj_mixin.title),
                                           "sub_model_key": obj_mixin.key,
                                           "objects_list": pair_set,
                                           "field_list": pair_field_list,
                                           "single_object": obj_mixin.model.objects.first()}

        obj_set = models.TeamXRef.objects.filter(evnt_id=self.object
                                                 ).distinct().select_related("perc_id", "loc_id", "role_id")
        obj_field_list = ["perc_id", "role_id", "loc_id"]
        obj_mixin = mixins.TeamMixin
        context["context_dict"]["team"] = {"div_title": "{} Details".format(obj_mixin.title),
                                           "sub_model_key": obj_mixin.key,
                                           "objects_list": obj_set,
                                           "field_list": obj_field_list,
                                           "single_object": obj_mixin.model.objects.first()}

        evntf_set = self.object.event_files.all()
        evntf_field_list = ["evntf_xls", "evntfc_id", "stok_id", ]
        obj_mixin = mixins.EvntfMixin
        context["context_dict"]["evntf"] = {"div_title": "{}".format(obj_mixin.title),
                                            "sub_model_key": obj_mixin.key,
                                            "objects_list": evntf_set,
                                            "field_list": evntf_field_list,
                                            "add_btn_url": "foo",
                                            "single_object": obj_mixin.model.objects.first()}

        evnt_code = self.object.evntc_id.__str__()
        if evnt_code == "Electrofishing" or evnt_code == "Bypass Collection" or evnt_code == "Smolt Wheel Collection":
            context["table_list"].extend(["data", "team", "loc", "grp", "tank", "prot", "evntf"])
        elif evnt_code == "PIT Tagging":
            context["table_list"].extend(["data", "team", "indv", "grp", "tank", "prot", "evntf"])
        elif evnt_code == "Egg Development":
            context["table_list"].extend(["data", "team", "grp", "trof", "heat", "prot", "evntf"])
        elif evnt_code == "Maturity Sorting":
            context["table_list"].extend(["data", "team", "indv", "tank", "prot", "evntf"])
        elif evnt_code == "Water Quality Record":
            context["table_list"].extend(["data", "team", "tank", "prot", "evntf"])
        elif evnt_code == "Spawning":
            context["table_list"].extend(["data", "team", "indv", "pair", "grp", "evntf", "prot", "evntf"])
        elif evnt_code == "Treatment":
            context["table_list"].extend(["data", "team", "tank", "trof", "prot", "evntf"])
        elif evnt_code == "Movement":
            context["table_list"].extend(["indv", "team", "grp", "tank", "trof", "prot", "evntf"])
        elif evnt_code == "Mortality":
            context["table_list"].extend(["indv", "team", "grp", "evntf"])
        else:
            context["table_list"].extend(["data", "team", "loc", "indv", "grp", "tank", "trof", "heat", "pair", "evntf", "prot"])

        return context


class EvntcDetails(mixins.EvntcMixin, CommonDetails):
    fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class EvntfDetails(mixins.EvntfMixin, CommonDetails):
    template_name = 'bio_diversity/details_evntf.html'
    fields = ["evnt_id", "evntfc_id", "evntf_xls", "stok_id", "comments", "created_by", "created_date", ]


class EvntfcDetails(mixins.EvntfcMixin, CommonDetails):
    fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class FacicDetails(mixins.FacicMixin, CommonDetails):
    fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class FecuDetails(mixins.FecuMixin, CommonDetails):
    fields = ["stok_id", "coll_id", "description_en", "start_date", "end_date", "alpha", "beta", "valid",
              "comments", "created_by", "created_date", ]


class FeedDetails(mixins.FeedMixin, CommonDetails):
    fields = ["feedm_id", "feedc_id", "lot_num", "amt", "unit_id", "freq", "comments", "created_by",
              "created_date", ]


class FeedcDetails(mixins.FeedcMixin, CommonDetails):
    fields = ["name", "nom", "manufacturer", "description_en", "description_fr", "created_by", "created_date", ]


class FeedmDetails(mixins.FeedmMixin, CommonDetails):
    fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class GrpDetails(mixins.GrpMixin, CommonDetails):
    template_name = 'bio_diversity/details_grp.html'
    fields = ["spec_id", "stok_id", "coll_id", "grp_year", "grp_valid", "comments", "created_by", "created_date", ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["table_list"].extend(["evnt", "indv", "cnt", "grpd", "pair", "cont"])
        anix_set = self.object.animal_details.filter(evnt_id__isnull=False, contx_id__isnull=True, loc_id__isnull=True,
                                                     indvt_id__isnull=True, indv_id__isnull=True, pair_id__isnull=True).select_related('evnt_id', 'evnt_id__evntc_id', 'evnt_id__facic_id', 'evnt_id__prog_id')
        evnt_list = list(dict.fromkeys([anix.evnt_id for anix in anix_set]))
        evnt_field_list = ["evntc_id", "facic_id", "prog_id", "start_date|Start Date"]
        obj_mixin = mixins.EvntMixin
        context["context_dict"]["evnt"] = {"div_title": "{} Details".format(obj_mixin.title),
                                           "sub_model_key": obj_mixin.key,
                                           "objects_list": evnt_list,
                                           "field_list": evnt_field_list,
                                           "single_object": obj_mixin.model.objects.first()}

        grp_set = models.GroupDet.objects.filter(anix_id__grp_id=self.object).distinct().select_related('anidc_id')
        grpd_field_list = ["anidc_id", "adsc_id", "det_val", "grpd_valid", "detail_date"]
        obj_mixin = mixins.GrpdMixin
        context["context_dict"]["grpd"] = {"div_title": "{} ".format(obj_mixin.title),
                                           "sub_model_key": obj_mixin.key,
                                           "objects_list": grp_set,
                                           "field_list": grpd_field_list,
                                           "single_object": obj_mixin.model.objects.first()}

        cnt_set = models.Count.objects.filter(contx_id__animal_details__grp_id=self.object).distinct().select_related("cntc_id")
        cnt_field_list = ["cntc_id", "cnt", "est", "date"]
        obj_mixin = mixins.CntMixin
        context["context_dict"]["cnt"] = {"div_title": "Counts",
                                          "sub_model_key": obj_mixin.key,
                                          "objects_list": cnt_set,
                                          "field_list": cnt_field_list,
                                          "single_object": obj_mixin.model.objects.first()}

        anix_evnt_set = self.object.animal_details.filter(contx_id__isnull=False, loc_id__isnull=True,
                                                          indvt_id__isnull=True, pair_id__isnull=True)

        contx_tuple_set = list(dict.fromkeys([(anix.contx_id, anix.final_contx_flag) for anix in anix_evnt_set]))
        context["cont_evnt_list"] = [get_cont_evnt(contx) for contx in contx_tuple_set]
        context["cont_evnt_field_list"] = [
            "Evnt",
            "Date",
            "Container",
        ]

        anix_set = self.object.animal_details.filter(contx_id__isnull=True, loc_id__isnull=True,
                                                     indvt_id__isnull=True, pair_id__isnull=False).select_related('pair_id')
        pair_list = [anix.pair_id for anix in anix_set]
        pair_field_list = ["start_date", "indv_id", "prio_id"]
        obj_mixin = mixins.PairMixin
        context["context_dict"]["pair"] = {"div_title": "{} Details".format(obj_mixin.title),
                                           "sub_model_key": obj_mixin.key,
                                           "objects_list": pair_list,
                                           "field_list": pair_field_list,
                                           "single_object": obj_mixin.model.objects.first()}

        indv_set = models.Individual.objects.filter(grp_id_id=self.object.pk)
        indv_field_list = ["pit_tag", "indv_valid"]
        obj_mixin = mixins.IndvMixin
        context["context_dict"]["indv"] = {"div_title": "{} From Group".format(obj_mixin.title),
                                           "sub_model_key": obj_mixin.key,
                                           "objects_list": indv_set,
                                           "field_list": indv_field_list,
                                           "single_object": obj_mixin.model.objects.first()}

        return context


class GrpdDetails(mixins.GrpdMixin, CommonDetails):
    fields = ["anidc_id",  "det_val", "adsc_id", "qual_id", "grpd_valid",  "detail_date", "comments", "created_by", "created_date", ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["title"] = "Group: {}".format(self.object.__str__())
        return context


class HeatDetails(mixins.HeatMixin, CommonDetails):
    fields = ["facic_id", "name", "nom", "description_en", "description_fr", "manufacturer", "serial_number", "inservice_date",
              "created_by", "created_date", ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["table_list"].extend(["draw"])

        draw_set = self.object.draws.all()
        draw_field_list = ["name", ]
        obj_mixin = mixins.DrawMixin
        context["context_dict"]["draw"] = {"div_title": "Draws in Heath Unit",
                                           "sub_model_key": obj_mixin.key,
                                           "objects_list": draw_set,
                                           "field_list": draw_field_list,
                                           "single_object": obj_mixin.model.objects.first()}
        return context


class HeatdDetails(mixins.HeatdMixin, CommonDetails):
    fields = ["heat_id", "contdc_id", "det_value", "cdsc_id", "start_date", "end_date", "det_valid", "comments",
              "created_by", "created_date", ]


class ImgDetails(mixins.ImgMixin, CommonDetails):
    template_name = 'bio_diversity/details_img.html'
    fields = ["imgc_id", "loc_id", "cntd_id", "grpd_id", "sampd_id", "indvd_id", "spwnd_id", "tankd_id", "heatd_id",
              "draw_id", "trofd_id", "trayd_id", "cupd_id", "img_png", "comments", "created_by", "created_date", ]


class ImgcDetails(mixins.ImgcMixin, CommonDetails):
    fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class IndvDetails(mixins.IndvMixin, CommonDetails):
    template_name = 'bio_diversity/details_indv.html'
    fields = ["grp_id", "spec_id", "stok_id", "coll_id", "indv_year", "ufid", "pit_tag", "indv_valid", "comments", "created_by",
              "created_date", ]

    def get_context_data(self, **kwargs):
        # use this to pass fields/sample object to template
        context = super().get_context_data(**kwargs)
        context["title"] = "Individual: {}".format(self.object.__str__())
        context["table_list"].extend(["evnt", "indvd", "pair", "team", "cont", "sire"])

        anix_evnt_set = self.object.animal_details.filter(contx_id__isnull=True, loc_id__isnull=True,
                                                          indvt_id__isnull=True, pair_id__isnull=True)\
            .select_related('evnt_id', 'evnt_id__evntc_id', 'evnt_id__facic_id', 'evnt_id__prog_id')
        evnt_list = list(dict.fromkeys([anix.evnt_id for anix in anix_evnt_set]))
        evnt_field_list = ["evntc_id", "facic_id", "prog_id", "start_datetime"]
        obj_mixin = mixins.EvntMixin
        context["context_dict"]["evnt"] = {"div_title": "{} Details".format(obj_mixin.title),
                                           "sub_model_key": obj_mixin.key,
                                           "objects_list": evnt_list,
                                           "field_list": evnt_field_list,
                                           "single_object": obj_mixin.model.objects.first()}

        indvd_set = models.IndividualDet.objects.filter(anix_id__indv_id=self.object).distinct()
        indvd_field_list = ["anidc_id", "adsc_id", "det_val", "indvd_valid", "detail_date"]
        obj_mixin = mixins.IndvdMixin
        context["context_dict"]["indvd"] = {"div_title": "{} ".format(obj_mixin.title),
                                            "sub_model_key": obj_mixin.key,
                                            "objects_list": indvd_set,
                                            "field_list": indvd_field_list,
                                            "single_object": obj_mixin.model.objects.first()}

        anix_set = self.object.animal_details.filter(pair_id__isnull=False)\
            .select_related('pair_id', 'pair_id__prio_id', 'pair_id__indv_id')
        pair_list = list(dict.fromkeys([anix.pair_id for anix in anix_set]))
        pair_list.extend([pair for pair in self.object.pairings.all().select_related('prio_id', 'indv_id')])
        pair_field_list = ["start_date", "indv_id", "prio_id"]
        obj_mixin = mixins.PairMixin
        context["context_dict"]["pair"] = {"div_title": "{} Details".format(obj_mixin.title),
                                           "sub_model_key": obj_mixin.key,
                                           "objects_list": pair_list,
                                           "field_list": pair_field_list,
                                           "single_object": obj_mixin.model.objects.first()}

        anix_set = self.object.animal_details.filter(team_id__isnull=False)\
            .select_related('team_id__role_id', 'team_id__perc_id', 'team_id__evnt_id')
        obj_list = list(dict.fromkeys([anix.team_id for anix in anix_set]))
        obj_field_list = ["perc_id", "role_id", "evnt_id"]
        obj_mixin = mixins.TeamMixin
        context["context_dict"]["team"] = {"div_title": "{} Details".format(obj_mixin.title),
                                           "sub_model_key": obj_mixin.key,
                                           "objects_list": obj_list,
                                           "field_list": obj_field_list,
                                           "single_object": obj_mixin.model.objects.first()}

        sire_set = self.object.sires.all().select_related('prio_id', 'indv_id')
        sire_field_list = ["prio_id", "pair_id", "choice"]
        obj_mixin = mixins.SireMixin
        context["context_dict"]["sire"] = {"div_title": "{} Details".format(obj_mixin.title),
                                           "sub_model_key": obj_mixin.key,
                                           "objects_list": sire_set,
                                           "field_list": sire_field_list,
                                           "single_object": obj_mixin.model.objects.first()}

        anix_evnt_set = self.object.animal_details.filter(contx_id__isnull=False, loc_id__isnull=True,
                                                          indvt_id__isnull=True, pair_id__isnull=True).select_related('contx_id', 'contx_id__evnt_id__evntc_id', 'contx_id__evnt_id')
        contx_tuple_set = list(dict.fromkeys([(anix.contx_id, anix.final_contx_flag) for anix in anix_evnt_set]))
        context["cont_evnt_list"] = [get_cont_evnt(contx) for contx in contx_tuple_set]
        context["cont_evnt_field_list"] = [
            "Evnt",
            "Date",
            "Direction"
            "Container",
        ]

        return context


class IndvdDetails(mixins.IndvdMixin, CommonDetails):
    fields = ["anidc_id",  "det_val", "adsc_id", "qual_id", "indvd_valid", "detail_date", "comments", "created_by", "created_date", ]


class IndvtDetails(mixins.IndvtMixin, CommonDetails):
    fields = ["indvtc_id", "lot_num", "dose", "unit_id", "start_time|Start Time", "end_date|End Date",
              "end_time|End Time", "comments", "created_by", "created_date", ]


class IndvtcDetails(mixins.IndvtcMixin, CommonDetails):
    fields = ["name", "nom", "rec_dose", "manufacturer", "description_en", "description_fr", "created_by",
              "created_date", ]


class InstDetails(mixins.InstMixin, CommonDetails):
    fields = ["instc_id", "serial_number", "comments", "created_by", "created_date", ]


class InstcDetails(mixins.InstcMixin, CommonDetails):
    fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class InstdDetails(mixins.InstdMixin, CommonDetails):
    fields = ["inst_id", "instdc_id", "det_value", "start_date", "end_date", "valid", "comments", "created_by",
              "created_date", ]


class InstdcDetails(mixins.InstdcMixin, CommonDetails):
    fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class LocDetails(mixins.LocMixin, CommonDetails):
    fields = ["evnt_id", "locc_id", "rive_id", "trib_id", "subr_id", "relc_id", "loc_lat", "loc_lon", "end_lat",
              "end_lon", "start_date|Date", "start_time|Time",  "comments", "created_by", "created_date", ]

    def get_context_data(self, **kwargs):
        # use this to pass sire fields/sample object to template
        context = super().get_context_data(**kwargs)
        context["table_list"].extend(["env", "team", "cnt"])

        env_set = self.object.env_condition.all()
        env_field_list = ["envc_id", "env_val", "start_datetime|Date", ]
        obj_mixin = mixins.EnvMixin
        context["context_dict"]["env"] = {"div_title": "{} Details".format(obj_mixin.title),
                                          "sub_model_key": obj_mixin.key,
                                          "objects_list": env_set,
                                          "field_list": env_field_list,
                                          "single_object": obj_mixin.model.objects.first()}

        cnt_set = self.object.counts.all()
        cnt_field_list = ["cntc_id", "spec_id", "cnt", "est"]
        obj_mixin = mixins.CntMixin
        context["context_dict"]["cnt"] = {"div_title": "{} Details".format(obj_mixin.title),
                                          "sub_model_key": obj_mixin.key,
                                          "objects_list": cnt_set,
                                          "field_list": cnt_field_list,
                                          "single_object": obj_mixin.model.objects.first()}

        obj_set = models.TeamXRef.objects.filter(loc_id=self.object
                                                 ).distinct().select_related("perc_id", "role_id")
        obj_field_list = ["perc_id", "role_id"]
        obj_mixin = mixins.TeamMixin
        context["context_dict"]["team"] = {"div_title": "{} Details".format(obj_mixin.title),
                                           "sub_model_key": obj_mixin.key,
                                           "objects_list": obj_set,
                                           "field_list": obj_field_list,
                                           "single_object": obj_mixin.model.objects.first()}
        return context


class LoccDetails(mixins.LoccMixin, CommonDetails):
    fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class OrgaDetails(mixins.OrgaMixin, CommonDetails):
    fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class PairDetails(mixins.PairMixin, CommonDetails):
    fields = ["indv_id", "start_date", "end_date", "prio_id", "pair_prio_id", "cross", "valid", "comments", "created_by", "created_date", ]

    def get_context_data(self, **kwargs):
        # use this to pass sire fields/sample object to template
        context = super().get_context_data(**kwargs)
        context["table_list"].extend(["sire", "spwnd"])

        sire_set = self.object.sires.all()
        sire_field_list = ["indv_id", "prio_id", "choice"]
        obj_mixin = mixins.SireMixin
        context["context_dict"]["sire"] = {"div_title": "{} Details".format(obj_mixin.title),
                                           "sub_model_key": obj_mixin.key,
                                           "objects_list": sire_set,
                                           "field_list": sire_field_list,
                                           "single_object": obj_mixin.model.objects.first()}

        context["spwnd_object"] = models.SpawnDet.objects.first()
        context["spwnd_field_list"] = [
            "spwndc_id",
            "det_val",
            "qual_id",
        ]

        spwnd_set = self.object.spawning_details.all()
        spwnd_field_list = ["spwndc_id", "det_val", "qual_id"]
        obj_mixin = mixins.SpwndMixin
        context["context_dict"]["spwnd"] = {"div_title": "{} Details".format(obj_mixin.title),
                                            "sub_model_key": obj_mixin.key,
                                            "objects_list": spwnd_set,
                                            "field_list": spwnd_field_list,
                                            "single_object": obj_mixin.model.objects.first()}
        return context


class PercDetails(mixins.PercMixin, CommonDetails):
    fields = ["perc_first_name", "perc_last_name", "initials", "perc_valid", "created_by", "created_date", ]


class PrioDetails(mixins.PrioMixin, CommonDetails):
    fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class ProgDetails(mixins.ProgMixin, CommonDetails):
    fields = ["prog_name", "prog_desc", "proga_id", "orga_id", "start_date", "end_date", "valid", "comments",
              "created_by", "created_date", ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["table_list"].extend(["prot"])

        prot_set = self.object.protocols.all()
        prot_field_list = ["name", "protc_id", "start_date"]
        obj_mixin = mixins.ProtMixin
        context["context_dict"]["prot"] = {"div_title": "{} Details".format(obj_mixin.title),
                                           "sub_model_key": obj_mixin.key,
                                           "objects_list": prot_set,
                                           "field_list": prot_field_list,
                                           "single_object": obj_mixin.model.objects.first()}

        return context


class ProgaDetails(mixins.ProgaMixin, CommonDetails):
    fields = ["proga_last_name", "proga_first_name", "created_by", "created_date", ]


class ProtDetails(mixins.ProtMixin, CommonDetails):
    template_name = "bio_diversity/details_prot.html"
    fields = ["name", "prog_id", "protc_id", "prot_desc", "facic_id", "evntc_id", "start_date", "end_date", "valid",
              "created_by", "created_date", ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["protf_object"] = models.Protofile.objects.first()
        context["protf_field_list"] = [
            "protf_pdf",
            "created_date",
        ]

        return context


class ProtcDetails(mixins.ProtcMixin, CommonDetails):
    fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class ProtfDetails(mixins.ProtfMixin, CommonDetails):
    template_name = 'bio_diversity/details_protf.html'
    fields = ["prot_id", "protf_pdf", "comments", "created_by", "created_date", ]


class QualDetails(mixins.QualMixin, CommonDetails):
    fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class RelcDetails(mixins.RelcMixin, CommonDetails):
    fields = ["name", "nom", "description_en", "description_fr", "rive_id", "trib_id", "subr_id", "min_lat", "max_lat",
              "min_lon", "max_lon", "created_by", "created_date", ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["table_list"].extend(["loc"])

        obj_set = self.object.locations.all()
        obj_field_list = ["locc_id", "start_date|Date"]
        obj_mixin = mixins.LocMixin
        context["context_dict"]["loc"] = {"div_title": "{} Details".format(obj_mixin.title),
                                          "sub_model_key": obj_mixin.key,
                                          "objects_list": obj_set,
                                          "field_list": obj_field_list,
                                          "single_object": obj_mixin.model.objects.first()}

        return context


class RiveDetails(mixins.RiveMixin, CommonDetails):
    fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["table_list"].extend(["relc"])

        obj_set = self.object.sites.all()
        obj_field_list = ["name", "subr_id", "trib_id"]
        obj_mixin = mixins.RelcMixin
        context["context_dict"]["relc"] = {"div_title": "{} Details".format(obj_mixin.title),
                                           "sub_model_key": obj_mixin.key,
                                           "objects_list": obj_set,
                                           "field_list": obj_field_list,
                                           "single_object": obj_mixin.model.objects.first()}

        return context


class RoleDetails(mixins.RoleMixin, CommonDetails):
    fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class SampDetails(mixins.SampMixin, CommonDetails):
    fields = ["loc_id", "samp_num", "spec_id", "sampc_id", "comments", "created_by", "created_date", ]


class SampcDetails(mixins.SampcMixin, CommonDetails):
    fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class SampdDetails(mixins.SampdMixin, CommonDetails):
    fields = ["samp_id", "anidc_id",  "det_val", "adsc_id", "qual_id", "comments", "created_by", "created_date", ]


class SireDetails(mixins.SireMixin, CommonDetails):
    fields = ["prio_id", "pair_id",  "indv_id", "choice", "comments", "created_by", "created_date", ]


class SpwndDetails(mixins.SpwndMixin, CommonDetails):
    fields = ["pair_id", "spwndc_id", "det_val", "spwnsc_id", "qual_id", "comments", "created_by", "created_date", ]


class SpwndcDetails(mixins.SpwndcMixin, CommonDetails):
    fields = ["name", "nom", "description_en", "description_fr", "min_val", "max_val", "unit_id", "spwn_subj_flag",
              "created_by", "created_date", ]


class SpwnscDetails(mixins.SpwnscMixin, CommonDetails):
    fields = ["name", "nom", "description_en", "description_fr", "spwndc_id", "created_by", "created_date", ]


class SpecDetails(mixins.SpecMixin, CommonDetails):
    fields = ["name", "species", "com_name", "created_by", "created_date", ]


class StokDetails(mixins.StokMixin, CommonDetails):
    fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class SubrDetails(mixins.SubrMixin, CommonDetails):
    fields = ["name", "nom", "rive_id", "trib_id", "description_en", "description_fr", "created_by", "created_date", ]


class TankDetails(mixins.TankMixin, CommonContDetails):
    fields = ["facic_id", "name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class TankdDetails(mixins.TankdMixin, CommonDetails):
    fields = ["tank_id", "contdc_id", "det_value", "cdsc_id", "start_date", "end_date", "det_valid", "comments",
              "created_by", "created_date", ]


class TeamDetails(mixins.TeamMixin, CommonDetails):
    fields = ["perc_id", "role_id", "evnt_id", "loc_id", "created_by", "created_date", ]


class TrayDetails(mixins.TrayMixin, CommonContDetails):
    fields = ["name", "nom", "trof_id", "description_en", "description_fr", "start_date", "end_date",
              "created_by", "created_date", ]


class TraydDetails(mixins.TraydMixin, CommonDetails):
    fields = ["tray_id", "contdc_id", "det_value", "cdsc_id", "start_date", "end_date", "det_valid", "comments",
              "created_by", "created_date", ]


class TribDetails(mixins.TribMixin, CommonDetails):
    fields = ["name", "nom", "rive_id", "description_en", "description_fr", "created_by", "created_date", ]


class TrofDetails(mixins.TrofMixin, CommonContDetails):

    fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["table_list"].extend(["tray"])

        tray_list = self.object.trays.all()
        tray_field_list = ["name", "start_date", "end_date"]
        obj_mixin = mixins.TrayMixin
        context["context_dict"]["tray"] = {"div_title": "Trays in Trough",
                                           "sub_model_key": obj_mixin.key,
                                           "objects_list": tray_list,
                                           "field_list": tray_field_list,
                                           "single_object": obj_mixin.model.objects.first()}
        return context


class TrofdDetails(mixins.TrofdMixin, CommonDetails):
    fields = ["trof_id", "contdc_id", "det_value", "cdsc_id", "start_date", "end_date", "det_valid", "comments",
              "created_by", "created_date", ]


class UnitDetails(mixins.UnitMixin, CommonDetails):
    fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


# ----------------------------LIST VIEWS-----------------------------
class GenericList(SiteLoginRequiredMixin, CommonFilterView):
    template_name = 'bio_diversity/bio_list.html'
    home_url_name = "bio_diversity:index"

    paginate_by = 20
    new_object_url_name = None
    row_object_url_name = row_ = None
    h1 = None

    def get_new_object_url_name(self):
        return self.new_object_url_name if self.new_object_url_name is not None else "bio_diversity:create_{}".format(self.key)

    def get_row_object_url_name(self):
        return self.new_object_url_name if self.new_object_url_name is not None else "bio_diversity:details_{}".format(self.key)

    def get_h1(self):
        return self.h1 if self.h1 is not None else self.title

    def get_queryset(self):
        if self.queryset:
            return self.queryset
        else:
            return self.model.objects.all()


class AnidcList(mixins.AnidcMixin, GenericList):
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'nom', "class": "", "width": ""},
    ]
    filterset_class = filters.AnidcFilter


class AnixList(mixins.AnixMixin, GenericList):
    field_list = [
        {"name": 'evnt_id', "class": "", "width": ""},
    ]
    queryset = models.AniDetailXref.objects.select_related("evnt_id")
    filterset_class = filters.AnixFilter


class AdscList(mixins.AdscMixin,  GenericList):
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'nom', "class": "", "width": ""},
    ]
    filterset_class = filters.AdscFilter


class CntList(mixins.CntMixin, GenericList):
    field_list = [
        {"name": 'loc_id', "class": "", "width": ""},
        {"name": 'spec_id', "class": "", "width": ""},
    ]
    queryset = models.Count.objects.select_related("loc_id", "spec_id")
    filterset_class = filters.CntFilter


class CntcList(mixins.CntcMixin, GenericList):
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'nom', "class": "", "width": ""},
    ]
    filterset_class = filters.CntcFilter


class CntdList(mixins.CntdMixin, GenericList):
    field_list = [
        {"name": 'cnt_id', "class": "", "width": ""},
        {"name": 'anidc_id', "class": "", "width": ""},
        {"name": 'qual_id', "class": "", "width": ""},
    ]
    queryset = models.CountDet.objects.select_related("cnt_id", "anidc_id", "qual_id")
    filterset_class = filters.CntdFilter


class CollList(mixins.CollMixin, GenericList):
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'nom', "class": "", "width": ""},
    ]
    filterset_class = filters.CollFilter


class ContdcList(mixins.ContdcMixin, GenericList):
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'nom', "class": "", "width": ""},
        {"name": 'min_val', "class": "", "width": ""},
        {"name": 'max_val', "class": "", "width": ""},
    ]
    filterset_class = filters.ContdcFilter


class ContxList(mixins.ContxMixin, GenericList):
    field_list = [
        {"name": 'evnt_id', "class": "", "width": ""},
    ]
    queryset = models.ContainerXRef.objects.select_related('evnt_id')
    filterset_class = filters.ContxFilter


class CdscList(mixins.CdscMixin, GenericList):
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'nom', "class": "", "width": ""},
        {"name": 'contdc_id', "class": "", "width": ""},
    ]
    queryset = models.ContDetSubjCode.objects.select_related("contdc_id")
    filterset_class = filters.CdscFilter


class CupList(mixins.CupMixin, GenericList):
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'nom', "class": "", "width": ""},
        {"name": 'draw_id', "class": "", "width": ""},
    ]
    queryset = models.Cup.objects.select_related("draw_id", "draw_id__heat_id")
    filterset_class = filters.CupFilter


class CupdList(mixins.CupdMixin, GenericList):
    field_list = [
        {"name": 'cup_id', "class": "", "width": ""},
        {"name": 'cdsc_id', "class": "", "width": ""},
        {"name": 'contdc_id', "class": "", "width": ""},
        {"name": 'start_date', "class": "", "width": ""},
        {"name": 'end_date', "class": "", "width": ""},
    ]
    queryset = models.CupDet.objects.select_related("contdc_id", "cup_id", "cdsc_id")
    filterset_class = filters.CupdFilter


class DrawList(mixins.DrawMixin, GenericList):
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'nom', "class": "", "width": ""},
        {"name": 'heat_id', "class": "", "width": ""},
    ]
    queryset = models.Drawer.objects.select_related("heat_id")
    filterset_class = filters.DrawFilter


class EnvList(mixins.EnvMixin, GenericList):
    field_list = [
        {"name": 'loc_id', "class": "", "width": ""},
        {"name": 'inst_id', "class": "", "width": ""},
        {"name": 'envc_id', "class": "", "width": ""},
    ]
    queryset = models.EnvCondition.objects.select_related("loc_id", "inst_id", "envc_id")
    filterset_class = filters.EnvFilter


class EnvcList(mixins.EnvcMixin, GenericList):
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'nom', "class": "", "width": ""},
    ]
    filterset_class = filters.EnvcFilter


class EnvcfList(mixins.EnvcfMixin, GenericList):
    field_list = [
        {"name": 'env_id', "class": "", "width": ""},
    ]
    queryset = models.EnvCondFile.objects.select_related("env")
    filterset_class = filters.EnvcfFilter


class EnvscList(mixins.EnvscMixin, GenericList):
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'nom', "class": "", "width": ""},
    ]
    filterset_class = filters.EnvscFilter


class EnvtList(mixins.EnvtMixin, GenericList):
    field_list = [
        {"name": 'envtc_id', "class": "", "width": ""},
        {"name": 'lot_num', "class": "", "width": ""},
    ]
    queryset = models.EnvTreatment.objects.select_related("envtc_id")
    filterset_class = filters.EnvtFilter


class EnvtcList(mixins.EnvtcMixin, GenericList):
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'nom', "class": "", "width": ""},
        {"name": 'rec_dose', "class": "", "width": ""},
        {"name": 'manufacturer', "class": "", "width": ""},
    ]
    filterset_class = filters.EnvtcFilter


class EvntList(mixins.EvntMixin, GenericList):
    field_list = [
        {"name": 'facic_id', "class": "", "width": ""},
        {"name": 'evntc_id', "class": "", "width": ""},
        {"name": 'start_datetime', "class": "", "width": ""},
    ]
    queryset = models.Event.objects.select_related("facic_id", "evntc_id")
    filterset_class = filters.EvntFilter


class EvntcList(mixins.EvntcMixin, GenericList):
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'nom', "class": "", "width": ""},
    ]
    filterset_class = filters.EvntcFilter


class EvntfList(mixins.EvntfMixin, GenericList):
    field_list = [
        {"name": 'evnt_id', "class": "", "width": ""},
        {"name": 'evntf_xls', "class": "", "width": ""},
    ]
    queryset = models.EventFile.objects.select_related("evnt_id")
    filterset_class = filters.EvntfFilter


class EvntfcList(mixins.EvntfcMixin, GenericList):
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'nom', "class": "", "width": ""},
    ]
    filterset_class = filters.EvntfcFilter


class FacicList(mixins.FacicMixin, GenericList):
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'nom', "class": "", "width": ""},
    ]
    filterset_class = filters.FacicFilter


class FecuList(mixins.FecuMixin, GenericList):
    field_list = [
        {"name": 'stok_id', "class": "", "width": ""},
        {"name": 'coll_id', "class": "", "width": ""},
        {"name": 'alpha_id', "class": "", "width": ""},
        {"name": 'beta_id', "class": "", "width": ""},
    ]
    queryset = models.Fecundity.objects.select_related("stok_id", "coll_id")
    filterset_class = filters.FecuFilter


class FeedList(mixins.FeedMixin, GenericList):
    field_list = [
        {"name": 'feedm_id', "class": "", "width": ""},
        {"name": 'feedc_id', "class": "", "width": ""},
    ]
    queryset = models.Feeding.objects.select_related("feedm_id", "feedc_id")
    filterset_class = filters.FeedFilter


class FeedcList(mixins.FeedcMixin, GenericList):
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'nom', "class": "", "width": ""},
    ]
    filterset_class = filters.FeedcFilter


class FeedmList(mixins.FeedmMixin, GenericList):
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'nom', "class": "", "width": ""},
    ]
    filterset_class = filters.FeedmFilter


class GrpList(mixins.GrpMixin, GenericList):
    field_list = [
        {"name": 'stok_id', "class": "", "width": ""},
        {"name": 'coll_id', "class": "", "width": ""},
        {"name": 'grp_year', "class": "", "width": ""},
    ]
    queryset = models.Group.objects.select_related("stok_id", "coll_id")
    filterset_class = filters.GrpFilter


class GrpdList(mixins.GrpdMixin, GenericList):
    field_list = [
        {"name": 'anix_id', "class": "", "width": ""},
        {"name": 'anidc_id', "class": "", "width": ""},
    ]
    queryset = models.GroupDet.objects.select_related("anix_id", "anidc_id")
    filterset_class = filters.GrpdFilter


class HeatList(mixins.HeatMixin, GenericList):
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'nom', "class": "", "width": ""},
        {"name": 'manufacturer', "class": "", "width": ""},
        {"name": 'serial_number', "class": "", "width": ""},
        {"name": 'inservice_date', "class": "", "width": ""},
    ]
    filterset_class = filters.HeatFilter


class HeatdList(mixins.HeatdMixin, GenericList):
    field_list = [
        {"name": 'heat_id', "class": "", "width": ""},
        {"name": 'contdc_id', "class": "", "width": ""},
        {"name": 'cdsc_id', "class": "", "width": ""},
        {"name": 'start_date', "class": "", "width": ""},
        {"name": 'end_date', "class": "", "width": ""},
    ]
    queryset = models.HeathUnitDet.objects.select_related("heat_id", "contdc_id", "cdsc_id")
    filterset_class = filters.HeatdFilter


class ImgList(mixins.ImgMixin, GenericList):
    field_list = [
        {"name": 'imgc_id', "class": "", "width": ""},
    ]
    queryset = models.Image.objects.select_related("imgc_id")
    filterset_class = filters.ImgFilter
    fields = ["imgc_id", ]


class ImgcList(mixins.ImgcMixin, GenericList):
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'nom', "class": "", "width": ""},
    ]
    filterset_class = filters.ImgcFilter
    fields = ["name", "nom", ]


class IndvList(mixins.IndvMixin, GenericList):
    field_list = [
        {"name": 'pit_tag', "class": "", "width": ""},
        {"name": 'ufid', "class": "", "width": ""},
        {"name": 'stok_id', "class": "", "width": ""},
        {"name": 'coll_id', "class": "", "width": ""},
    ]
    queryset = models.Individual.objects.all().select_related("stok_id", "coll_id")
    filterset_class = filters.IndvFilter


class IndvdList(mixins.IndvdMixin, GenericList):
    field_list = [
        {"name": 'anidc_id', "class": "", "width": ""},
    ]
    queryset = models.Individual.objects.all().select_related("anidc_id")
    filterset_class = filters.IndvdFilter


class IndvtList(mixins.IndvtMixin, GenericList):
    field_list = [
        {"name": 'indvtc_id', "class": "", "width": ""},
        {"name": 'lot_num', "class": "", "width": ""},
    ]
    queryset = models.IndTreatment.objects.all().select_related("indvtc_id")
    filterset_class = filters.IndvtFilter


class IndvtcList(mixins.IndvtcMixin, GenericList):
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'nom', "class": "", "width": ""},
        {"name": 'rec_dose', "class": "", "width": ""},
        {"name": 'manufacturer', "class": "", "width": ""},
    ]
    filterset_class = filters.IndvtcFilter


class InstList(mixins.InstMixin, GenericList):
    field_list = [
        {"name": 'instc_id', "class": "", "width": ""},
        {"name": 'serial_number', "class": "", "width": ""},
    ]
    queryset = models.Instrument.objects.all().select_related("instc_id")
    filterset_class = filters.InstFilter


class InstcList(mixins.InstcMixin, GenericList):
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'nom', "class": "", "width": ""},
    ]
    queryset = models.InstrumentCode.objects.all().select_related("a", "b")
    filterset_class = filters.InstcFilter


class InstdList(mixins.InstdMixin, GenericList):
    field_list = [
        {"name": 'inst_id', "class": "", "width": ""},
        {"name": 'instdc_id', "class": "", "width": ""},
    ]
    queryset = models.InstrumentDet.objects.all().select_related("inst_id", "instdc_id")
    filterset_class = filters.InstdFilter


class InstdcList(mixins.InstdcMixin, GenericList):
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'nom', "class": "", "width": ""},
    ]
    filterset_class = filters.InstdcFilter


class LocList(mixins.LocMixin, GenericList):
    field_list = [
        {"name": 'evnt_id', "class": "", "width": ""},
        {"name": 'rive_id', "class": "", "width": ""},
        {"name": 'trib_id', "class": "", "width": ""},
        {"name": 'relc_id', "class": "", "width": ""},
        {"name": 'start_date|Date', "class": "", "width": ""},
    ]
    queryset = models.Location.objects.all().select_related("evnt_id", "rive_id", "trib_id", "relc_id")
    filterset_class = filters.LocFilter


class LoccList(mixins.LoccMixin, GenericList):
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'nom', "class": "", "width": ""},
    ]
    filterset_class = filters.LoccFilter


class OrgaList(mixins.OrgaMixin, GenericList):
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'nom', "class": "", "width": ""},
    ]
    filterset_class = filters.OrgaFilter


class PairList(mixins.PairMixin, GenericList):
    field_list = [
        {"name": 'indv_id', "class": "", "width": ""},
        {"name": 'prio_id', "class": "", "width": ""},
    ]
    queryset = models.Pairing.objects.all().select_related("indv_id", "prio_id")
    filterset_class = filters.PairFilter


class PercList(mixins.PercMixin, GenericList):
    field_list = [
        {"name": 'perc_first_name', "class": "", "width": ""},
        {"name": 'perc_last_name', "class": "", "width": ""},
        {"name": 'perc_valid', "class": "", "width": ""},
    ]
    filterset_class = filters.PercFilter


class PrioList(mixins.PrioMixin, GenericList):
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'nom', "class": "", "width": ""},
    ]
    filterset_class = filters.PrioFilter
    fields = ["name", "nom", ]


class ProgList(mixins.ProgMixin, GenericList):
    field_list = [
        {"name": 'prog_name', "class": "", "width": ""},
        {"name": 'proga_id', "class": "", "width": ""},
        {"name": 'orga_id', "class": "", "width": ""},
    ]
    queryset = models.Program.objects.all().select_related("proga_id", "orga_id")
    filterset_class = filters.ProgFilter


class ProgaList(mixins.ProgaMixin, GenericList):
    field_list = [
        {"name": 'proga_first_name', "class": "", "width": ""},
        {"name": 'proga_last_name', "class": "", "width": ""},
    ]
    filterset_class = filters.ProgaFilter


class ProtList(mixins.ProtMixin, GenericList):
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'prog_id', "class": "", "width": ""},
        {"name": 'protc_id', "class": "", "width": ""},
        {"name": 'facic_id', "class": "", "width": ""},
    ]
    queryset = models.Protocol.objects.all().select_related("prog_id", "protc_id", "facic_id")
    filterset_class = filters.ProtFilter


class ProtcList(mixins.ProtcMixin, GenericList):
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'nom', "class": "", "width": ""},
    ]
    filterset_class = filters.ProtcFilter
    fields = ["name", "nom", ]


class ProtfList(mixins.ProtfMixin, GenericList):
    field_list = [
        {"name": 'prot_id', "class": "", "width": ""},
    ]
    queryset = models.Protofile.objects.all().select_related("prot_id")
    filterset_class = filters.ProtfFilter


class QualList(mixins.QualMixin, GenericList):
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'nom', "class": "", "width": ""},
    ]
    filterset_class = filters.QualFilter


class RelcList(mixins.RelcMixin, GenericList):
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'nom', "class": "", "width": ""},
    ]
    filterset_class = filters.RelcFilter


class RiveList(mixins.RiveMixin, GenericList):
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'nom', "class": "", "width": ""},
    ]
    filterset_class = filters.RiveFilter


class RoleList(mixins.RoleMixin, GenericList):
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'nom', "class": "", "width": ""},
    ]
    filterset_class = filters.RoleFilter


class SampList(mixins.SampMixin, GenericList):
    field_list = [
        {"name": 'loc_id', "class": "", "width": ""},
        {"name": 'samp_num', "class": "", "width": ""},
        {"name": 'spec_id', "class": "", "width": ""},
    ]
    queryset = models.Sample.objects.all().select_related("loc_id", "spec_id")
    filterset_class = filters.SampFilter


class SampcList(mixins.SampcMixin, GenericList):
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'nom', "class": "", "width": ""},
    ]
    filterset_class = filters.SampcFilter


class SampdList(mixins.SampdMixin, GenericList):
    field_list = [
        {"name": 'samp_id', "class": "", "width": ""},
        {"name": 'anidc_id', "class": "", "width": ""},
    ]
    queryset = models.SampleDet.objects.all().select_related("samp_id", "anidc_id")
    filterset_class = filters.SampdFilter


class SireList(mixins.SireMixin, GenericList):
    field_list = [
        {"name": 'prio_id', "class": "", "width": ""},
        {"name": 'pair_id', "class": "", "width": ""},
    ]
    queryset = models.Sire.objects.all().select_related("prio_id", "pair_id")
    filterset_class = filters.SireFilter


class SpwndList(mixins.SpwndMixin, GenericList):
    field_list = [
        {"name": 'pair_id', "class": "", "width": ""},
        {"name": 'spwndc_id', "class": "", "width": ""},
    ]
    queryset = models.SpawnDet.objects.all().select_related("pair_id", "spwndc_id")
    filterset_class = filters.SpwndFilter


class SpwndcList(mixins.SpwndcMixin, GenericList):
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'nom', "class": "", "width": ""},
    ]
    filterset_class = filters.SpwndcFilter


class SpwnscList(mixins.SpwnscMixin, GenericList):
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'nom', "class": "", "width": ""},
    ]
    filterset_class = filters.SpwnscFilter


class SpecList(mixins.SpecMixin, GenericList):
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'species', "class": "", "width": ""},
        {"name": 'com_name', "class": "", "width": ""},
    ]
    filterset_class = filters.SpecFilter


class StokList(mixins.StokMixin, GenericList):
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'nom', "class": "", "width": ""},
    ]
    filterset_class = filters.StokFilter


class SubrList(mixins.SubrMixin, GenericList):
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'nom', "class": "", "width": ""},
        {"name": 'rive_id', "class": "", "width": ""},
        {"name": 'trib_id', "class": "", "width": ""},
    ]
    queryset = models.SubRiverCode.objects.all().select_related("rive_id", "trib_id")
    filterset_class = filters.SubrFilter


class TankList(mixins.TankMixin, GenericList):
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'nom', "class": "", "width": ""},
        {"name": 'facic_id', "class": "", "width": ""},
    ]
    queryset = models.Tank.objects.select_related("facic_id")
    filterset_class = filters.TankFilter


class TankdList(mixins.TankdMixin, GenericList):
    field_list = [
        {"name": 'tank_id', "class": "", "width": ""},
        {"name": 'contdc_id', "class": "", "width": ""},
        {"name": 'cdsc_id', "class": "", "width": ""},
        {"name": 'start_date', "class": "", "width": ""},
        {"name": 'end_date', "class": "", "width": ""},
    ]
    queryset = models.TankDet.objects.all().select_related("tank_id", "contdc_id", "cdsc_id")
    filterset_class = filters.TankdFilter


class TeamList(mixins.TeamMixin, GenericList):
    field_list = [
        {"name": 'perc_id', "class": "", "width": ""},
        {"name": 'role_id', "class": "", "width": ""},
        {"name": 'evnt_id', "class": "", "width": ""},
        {"name": 'loc_id', "class": "", "width": ""},
    ]
    queryset = models.TeamXRef.objects.all().select_related("perc_id", "role_id", "evnt_id", "loc_id")
    filterset_class = filters.TeamFilter


class TrayList(mixins.TrayMixin, GenericList):
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'nom', "class": "", "width": ""},
    ]
    filterset_class = filters.TrayFilter


class TraydList(mixins.TraydMixin, GenericList):
    field_list = [
        {"name": 'tray_id', "class": "", "width": ""},
        {"name": 'contdc_id', "class": "", "width": ""},
        {"name": 'cdsc_id', "class": "", "width": ""},
        {"name": 'start_date', "class": "", "width": ""},
        {"name": 'end_date', "class": "", "width": ""},
    ]
    queryset = models.TrayDet.objects.all().select_related("tray_id", "contdc_id", "cdsc_id")
    filterset_class = filters.TraydFilter


class TribList(mixins.TribMixin, GenericList):
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'nom', "class": "", "width": ""},
        {"name": 'rive_id', "class": "", "width": ""},
    ]
    queryset = models.Tributary.objects.all().select_related("rive_id")
    filterset_class = filters.TribFilter


class TrofList(mixins.TrofMixin, GenericList):
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'nom', "class": "", "width": ""},
        {"name": 'facic_id', "class": "", "width": ""},
    ]
    queryset = models.Trough.objects.all().select_related("facic_id")
    filterset_class = filters.TrofFilter


class TrofdList(mixins.TrofdMixin, GenericList):
    field_list = [
        {"name": 'trof_id', "class": "", "width": ""},
        {"name": 'contdc_id', "class": "", "width": ""},
        {"name": 'cdsc_id', "class": "", "width": ""},
        {"name": 'start_date', "class": "", "width": ""},
        {"name": 'end_date', "class": "", "width": ""},
    ]
    queryset = models.TroughDet.objects.all().select_related("trof_id", "contdc_id", "cdsc_id")
    filterset_class = filters.TrofdFilter


class UnitList(mixins.UnitMixin,  GenericList):
    field_list = [
        {"name": 'name', "class": "", "width": ""},
        {"name": 'nom', "class": "", "width": ""},
    ]
    filterset_class = filters.UnitFilter


# ---------------------------UPDATE VIEWS-----------------------------------
class CommonUpdate(CommonAuthUpdateView):

    nav_menu = 'bio_diversity/bio_diversity_nav.html'
    site_css = 'bio_diversity/bio_diversity.css'
    home_url_name = "bio_diversity:index"

    def get_success_url(self):
        success_url = self.success_url if self.success_url else reverse_lazy("bio_diversity:list_{}".format(self.key))

        if self.kwargs.get("pop"):
            # create views intended to be pop out windows should close the window upon success
            success_url = reverse_lazy("shared_models:close_me_no_refresh")

        return success_url

    def get_nav_menu(self):
        if self.kwargs.get("pop"):
            return None

        return self.nav_menu

    def get_initial(self):
        init = super().get_initial()
        # can uncomment this to auto update user on any update
        # init["created_by"] = self.request.user.username
        if hasattr(self.model, "start_datetime"):
            init["start_date"] = self.object.start_date
            init["start_time"] = self.object.start_time
        if hasattr(self.model, "end_datetime"):
            if self.object.end_datetime:
                init["end_date"] = self.object.end_date
                init["end_time"] = self.object.end_time
        return init

    # this function overrides UserPassesTestMixin.test_func() to determine if
    # the user should have access to this content, if the user is logged in
    # This function could be overridden in extending classes to preform further testing to see if
    # an object is editable
    def test_func(self):
        if self.admin_only:
            return utils.bio_diverisity_admin(self.request.user)
        else:
            return utils.bio_diverisity_authorized(self.request.user)

    # Get context returns elements used on the page. Make sure when extending to call
    # context = super().get_context_data(**kwargs) so that elements created in the parent
    # class are inherited by the extending class.
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editable'] = context['auth']
        return context


class AnidcUpdate(mixins.AnidcMixin, CommonUpdate):
    pass


class AnixUpdate(mixins.AnixMixin, CommonUpdate):
    pass


class AdscUpdate(mixins.AdscMixin, CommonUpdate):
    pass


class CntUpdate(mixins.CntMixin, CommonUpdate):
    pass


class CntcUpdate(mixins.CntcMixin, CommonUpdate):
    pass


class CntdUpdate(mixins.CntdMixin, CommonUpdate):
    pass


class CollUpdate(mixins.CollMixin, CommonUpdate):
    pass


class ContdcUpdate(mixins.ContdcMixin, CommonUpdate):
    pass


class ContxUpdate(mixins.ContxMixin, CommonUpdate):
    pass


class CdscUpdate(mixins.CdscMixin, CommonUpdate):
    pass


class CupUpdate(mixins.CupMixin, CommonUpdate):
    pass


class CupdUpdate(mixins.CupdMixin, CommonUpdate):
    pass


class DrawUpdate(mixins.DrawMixin, CommonUpdate):
    pass


class EnvUpdate(mixins.EnvMixin, CommonUpdate):
    pass


class EnvcUpdate(mixins.EnvcMixin, CommonUpdate):
    pass


class EnvcfUpdate(mixins.EnvcfMixin, CommonUpdate):
    pass


class EnvscUpdate(mixins.EnvscMixin, CommonUpdate):
    pass


class EnvtUpdate(mixins.EnvtMixin, CommonUpdate):
    pass


class EnvtcUpdate(mixins.EnvtcMixin, CommonUpdate):
    pass


class EvntUpdate(mixins.EvntMixin, CommonUpdate):
    def get_success_url(self):
        success_url = self.success_url if self.success_url else reverse_lazy("bio_diversity:details_{}".format(self.key), kwargs={'pk': self.object.pk})

        if self.kwargs.get("pop"):
            # create views intended to be pop out windows should close the window upon success
            success_url = reverse_lazy("shared_models:close_me_no_refresh")

        return success_url

    def get_initial(self):
        init = super().get_initial()
        # can uncomment this to auto update user on any update
        # init["created_by"] = self.request.user.username
        init["start_date"] = self.object.start_date
        init["start_time"] = self.object.start_time
        init["end_date"] = self.object.end_date
        init["end_time"] = self.object.end_time
        return init


class EvntcUpdate(mixins.EvntcMixin, CommonUpdate):
    pass


class EvntfUpdate(mixins.EvntfMixin, CommonUpdate):
    pass


class EvntfcUpdate(mixins.EvntfcMixin, CommonUpdate):
    pass


class FacicUpdate(mixins.FacicMixin, CommonUpdate):
    pass


class FecuUpdate(mixins.FecuMixin, CommonUpdate):
    pass


class FeedUpdate(mixins.FeedMixin, CommonUpdate):
    pass


class FeedcUpdate(mixins.FeedcMixin, CommonUpdate):
    pass


class FeedmUpdate(mixins.FeedmMixin, CommonUpdate):
    pass


class GrpUpdate(mixins.GrpMixin, CommonUpdate):
    pass


class GrpdUpdate(mixins.GrpdMixin, CommonUpdate):
    pass


class HeatUpdate(mixins.HeatMixin, CommonUpdate):
    pass


class HeatdUpdate(mixins.HeatdMixin, CommonUpdate):
    pass


class ImgUpdate(mixins.ImgMixin, CommonUpdate):
    pass


class ImgcUpdate(mixins.ImgcMixin, CommonUpdate):
    pass


class IndvUpdate(mixins.IndvMixin, CommonUpdate):
    pass


class IndvdUpdate(mixins.IndvdMixin, CommonUpdate):
    pass


class IndvtUpdate(mixins.IndvtMixin, CommonUpdate):
    pass


class IndvtcUpdate(mixins.IndvtcMixin, CommonUpdate):
    pass


class InstUpdate(mixins.InstMixin, CommonUpdate):
    pass


class InstcUpdate(mixins.InstcMixin, CommonUpdate):
    pass


class InstdUpdate(mixins.InstdMixin, CommonUpdate):
    pass


class InstdcUpdate(mixins.InstdcMixin, CommonUpdate):
    pass


class LocUpdate(mixins.LocMixin, CommonUpdate):
    def get_initial(self):
        init = super().get_initial()
        # can uncomment this to auto update user on any update
        # init["created_by"] = self.request.user.username
        init["start_date"] = self.object.start_date
        init["start_time"] = self.object.start_time
        return init


class LoccUpdate(mixins.LoccMixin, CommonUpdate):
    pass


class OrgaUpdate(mixins.OrgaMixin, CommonUpdate):
    pass


class PairUpdate(mixins.PairMixin, CommonUpdate):
    pass


class PercUpdate(mixins.PercMixin, CommonUpdate):
    pass


class PrioUpdate(mixins.PrioMixin, CommonUpdate):
    pass


class ProgUpdate(mixins.ProgMixin, CommonUpdate):
    pass


class ProgaUpdate(mixins.ProgaMixin, CommonUpdate):
    pass


class ProtUpdate(mixins.ProtMixin, CommonUpdate):
    pass


class ProtcUpdate(mixins.ProtcMixin, CommonUpdate):
    pass


class ProtfUpdate(mixins.ProtfMixin, CommonUpdate):
    pass


class QualUpdate(mixins.QualMixin, CommonUpdate):
    pass


class RelcUpdate(mixins.RelcMixin, CommonUpdate):
    pass


class RiveUpdate(mixins.RiveMixin, CommonUpdate):
    pass


class RoleUpdate(mixins.RoleMixin, CommonUpdate):
    pass


class SampUpdate(mixins.SampMixin, CommonUpdate):
    pass


class SampcUpdate(mixins.SampcMixin, CommonUpdate):
    pass


class SampdUpdate(mixins.SampdMixin, CommonUpdate):
    pass


class SireUpdate(mixins.SireMixin, CommonUpdate):
    pass


class SpwndUpdate(mixins.SpwndMixin, CommonUpdate):
    pass


class SpwndcUpdate(mixins.SpwndcMixin, CommonUpdate):
    pass


class SpwnscUpdate(mixins.SpwnscMixin, CommonUpdate):
    pass


class SpecUpdate(mixins.SpecMixin, CommonUpdate):
    pass


class StokUpdate(mixins.StokMixin, CommonUpdate):
    pass


class SubrUpdate(mixins.SubrMixin, CommonUpdate):
    pass


class TankUpdate(mixins.TankMixin, CommonUpdate):
    pass


class TankdUpdate(mixins.TankdMixin, CommonUpdate):
    pass


class TeamUpdate(mixins.TeamMixin, CommonUpdate):
    pass


class TrayUpdate(mixins.TrayMixin, CommonUpdate):
    pass


class TraydUpdate(mixins.TraydMixin, CommonUpdate):
    pass


class TribUpdate(mixins.TribMixin, CommonUpdate):
    pass


class TrofUpdate(mixins.TrofMixin, CommonUpdate):
    pass


class TrofdUpdate(mixins.TrofdMixin, CommonUpdate):
    pass


class UnitUpdate(mixins.UnitMixin, CommonUpdate):
    pass


# ---------------------GENERIC VIEWS-----------------------
class CommonLog(CommonTemplateView):
    success_url = reverse_lazy("shared_models:close_me")
    template_name = 'bio_diversity/bio_log.html'
    title = "Data Log"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        log_data = self.request.session.get("log_data")
        context['log_data'] = log_data
        context["load_success"] = self.request.session.get("load_success")

        return context

    def test_func(self):
        return utils.bio_diverisity_authorized(self.request.user)


class DataLog(CommonLog):
    pass


class CommonDelete(SiteLoginRequiredMixin, DeleteView):
    success_url = reverse_lazy("shared_models:close_me")
    template_name = 'bio_diversity/delete_confirm.html'
    success_message = 'The dataset was successfully deleted!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title_msg'] = _("Are you sure you want to delete the following from the database?")
        context['confirm_msg'] = _("You will not be able to recover this object.")

        return context

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class IndvDelete(mixins.IndvMixin, CommonDelete):
    success_url = reverse_lazy("bio_diversity:list_indv")


class CommentKeywordsFormsetView(SiteLoginRequiredMixin, CommonFormsetView):
    template_name = 'bio_diversity/formset.html'
    title = _("Bio Diversity Comment Keywords")
    h1 = _("Manage Comment Keywords")
    queryset = models.CommentKeywords.objects.all()
    formset_class = CommentKeywordsFormset
    success_url_name = "bio_diversity:manage_comment_keywords"
    home_url_name = "bio_diversity:index"
    delete_url_name = "bio_diversity:delete_comment_keywords"


class CommentKeywordsHardDeleteView(SiteLoginRequiredMixin, CommonHardDeleteView):
    model = models.CommentKeywords
    success_url = reverse_lazy("bio_diversity:manage_comment_keywords")


class HelpTextFormsetView(SiteLoginRequiredMixin, CommonFormsetView):
    template_name = 'bio_diversity/formset.html'
    title = _("Bio Diversity Help Text")
    h1 = _("Manage Help Texts")
    queryset = models.HelpText.objects.all()
    formset_class = HelpTextFormset
    success_url_name = "bio_diversity:manage_help_texts"
    home_url_name = "bio_diversity:index"
    delete_url_name = "bio_diversity:delete_help_text"


class HelpTextHardDeleteView(SiteLoginRequiredMixin, CommonHardDeleteView):
    model = models.HelpText
    success_url = reverse_lazy("bio_diversity:manage_help_texts")


class MortFormView(mixins.MortMixin, SiteLoginRequiredMixin, CommonFormView):
    template_name = 'shared_models/shared_entry_form.html'

    nav_menu = 'bio_diversity/bio_diversity_nav.html'
    site_css = 'bio_diversity/bio_diversity.css'
    home_url_name = "bio_diversity:index"

    def get_initial(self):
        init = super().get_initial()
        init["created_by"] = self.request.user.username
        init["created_date"] = date.today
        init["mort_date"] = date.today
        if self.kwargs.get("iorg") == "indv":
            init["indv_mort"] = self.kwargs.get("pk")
        elif self.kwargs.get("iorg") == "grp":
            init["grp_mort"] = self.kwargs.get("pk")
        return init

    def get_nav_menu(self):
        if self.kwargs.get("pop"):
            return None

        return self.nav_menu

    # Upon success most creation views will be redirected to the Individual List view. To send
    # a successful creation view somewhere else, override this method
    def get_success_url(self):
        success_url = self.success_url if self.success_url else reverse_lazy("bio_diversity:list_indv")

        if self.kwargs.get("pop"):
            # create views intended to be pop out windows should close the window upon success
            success_url = reverse_lazy("shared_models:close_me_no_refresh")

        return success_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        return super().form_valid(form)


class ReportFormView(mixins.ReportMixin, SiteLoginRequiredMixin, CommonFormView):
    template_name = 'shared_models/shared_entry_form.html'

    nav_menu = 'bio_diversity/bio_diversity_nav.html'
    site_css = 'bio_diversity/bio_diversity.css'
    home_url_name = "bio_diversity:index"
    h1 = _("Facility Reports")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['java_script'] = 'bio_diversity/_entry_report_js.html'

        return context

    def form_valid(self, form):
        report = int(form.cleaned_data["report"])

        if report == 1:
            facic_pk = int(form.cleaned_data["facic_id"].pk)
            return HttpResponseRedirect(reverse("bio_diversity:facic_tank_report") + f"?facic_pk={facic_pk}")
        elif report == 2:
            stok_pk = int(form.cleaned_data["stok_id"].pk)
            if form.cleaned_data["on_date"]:
                return HttpResponseRedirect(reverse("bio_diversity:stock_code_report") + f"?stok_pk={stok_pk}&on_date={form.cleaned_data['on_date']}")
            else:
                return HttpResponseRedirect(reverse("bio_diversity:stock_code_report") + f"?stok_pk={stok_pk}")
        else:
            messages.error(self.request, "Report is not available. Please select another report.")
            return HttpResponseRedirect(reverse("bio_diversity:reports"))


@login_required()
def facility_tank_report(request):
    facic_pk = request.GET.get("facic_pk")
    if facic_pk:
        file_url = reports.generate_facility_tank_report(facic_pk)

    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = f'inline; filename="dmapps facility tank report ({timezone.now().strftime("%Y-%m-%d")}).xlsx"'

            return response
    raise Http404


@login_required()
def stock_code_report(request):
    stok_pk = request.GET.get("stok_pk")
    on_date = request.GET.get("on_date")
    stok_id = models.StockCode.objects.filter(pk=stok_pk).get()
    if stok_id and on_date:
        on_date = datetime.datetime.strptime(on_date, "%Y-%m-%d").replace(tzinfo=pytz.UTC)
        file_url = reports.generate_stock_code_report(stok_id, on_date)
    elif stok_id:
        file_url = reports.generate_stock_code_report(stok_id)

    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = f'inline; filename="dmapps stock codes report ({timezone.now().strftime("%Y-%m-%d")}).xlsx"'

            return response
    raise Http404


@login_required()
def plot_data_file(request):
    file_url = request.GET.get("file_url")

    if os.path.exists(file_url):
        with open(file_url, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="text/csv")
            response['Content-Disposition'] = f'inline; filename="plot_data_file ({timezone.now().strftime("%Y-%m-%d")}).csv"'
            return response
    raise Http404


class PlotView(CommonTemplateView):
    success_url = reverse_lazy("shared_models:close_me")
    template_name = 'bio_diversity/bio_plot.html'
    title = "Plot view"

    def test_func(self):
        return utils.bio_diverisity_authorized(self.request.user)


class GrowthChartView(PlotView):

    title = _("Growth Chart")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fish_pk = self.kwargs.get("pk")
        if self.kwargs.get("iorg") == "indv":
            plot_fish = models.Individual.objects.filter(pk=fish_pk).get()
        elif self.kwargs.get("iorg") == "grp":
            plot_fish = models.Group.objects.filter(pk=fish_pk).get()
        context["the_script"], context["the_div"], file_url = reports.generate_growth_chart(plot_fish)
        context["data_file_url"] = reverse("bio_diversity:plot_data_file") + f"?file_url={file_url}"
        return context


class MaturityRateView(PlotView):

    title = _("Maturity Rate")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cont_pk = self.kwargs.get("pk")
        if self.kwargs.get("cont") == "tank":
            cont = models.Tank.objects.filter(pk=cont_pk).get()
        elif self.kwargs.get("cont") == "trof":
            cont = models.Trough.objects.filter(pk=cont_pk).get()
        elif self.kwargs.get("cont") == "tray":
            cont = models.Tray.objects.filter(pk=cont_pk).get()
        elif self.kwargs.get("cont") == "cup":
            cont = models.Cup.objects.filter(pk=cont_pk).get()
        elif self.kwargs.get("cont") == "grp":
            cont = models.Group.objects.filter(pk=cont_pk).get()
        context["the_script"], context["the_div"], file_url = reports.generate_maturity_rate(cont)
        context["data_file_url"] = reverse("bio_diversity:plot_data_file") + f"?file_url={file_url}"
        return context


class PlotTempData(PlotView):

    title = _("Temperature Data")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cont_pk = self.kwargs.get("pk")
        env_set = []
        if self.kwargs.get("cont") == "tank":
            env_set = models.EnvCondition.objects.filter(contx_id__tank_id=cont_pk, envc_id__name="Temperature")
        elif self.kwargs.get("cont") == "trof":
            env_set = models.EnvCondition.objects.filter(contx_id__trof_id=cont_pk, envc_id__name="Temperature")
        elif self.kwargs.get("cont") == "tray":
            trof_pk = models.Tray.objects.filter(pk=cont_pk).get().trof_id.pk
            env_set = models.EnvCondition.objects.filter(contx_id__trof_id=trof_pk, envc_id__name="Temperature")

        x_data = [env.start_datetime for env in env_set]
        y_data = [env.env_val for env in env_set]
        context["the_script"], context["the_div"], file_url = reports.plot_date_data(x_data, y_data, "Temperature", "Temperature data")
        context["data_file_url"] = reverse("bio_diversity:plot_data_file") + f"?file_url={file_url}"
        return context


class LocMapTemplateView(mixins.MapMixin, SiteLoginRequiredMixin, CommonFormView):
    template_name = 'bio_diversity/loc_map.html'
    admin_only = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['google_api_key'] = settings.GOOGLE_API_KEY

        # filter locations by start-end dates and river codes if needed:
        location_qs = models.Location.objects.filter(loc_lat__isnull=False, loc_lon__isnull=False).select_related("evnt_id__evntc_id", "rive_id", "relc_id__rive_id")
        if self.kwargs.get("start"):
            start_date = utils.naive_to_aware(datetime.datetime.strptime(self.kwargs.get("start"), '%Y-%m-%d'))
            end_date = utils.naive_to_aware(datetime.datetime.strptime(self.kwargs.get("end"), '%Y-%m-%d'))
            location_qs = location_qs.filter(loc_date__lte=end_date, loc_date__gte=start_date)

        if self.kwargs.get("rive_id"):
            location_qs = location_qs.filter(rive_id__name=self.kwargs.get("rive_id")) | location_qs.filter(relc_id__rive_id__name=self.kwargs.get("rive_id"))

        context["locations"] = location_qs.filter(end_lat__isnull=True, end_lon__isnull=True)
        context["line_locations"] = location_qs.filter(end_lat__isnull=False, end_lon__isnull=False)

        # filter sites:
        site_qs = models.ReleaseSiteCode.objects.filter(min_lat__isnull=False, max_lat__isnull=False, min_lon__isnull=False, max_lon__isnull=False).select_related("rive_id")
        if self.kwargs.get("rive_id"):
            site_qs = site_qs.filter(rive_id__name=self.kwargs.get("rive_id"))

        context["sites"] = site_qs

        # start by determining which locations do not have spatial data
        non_spatial_location_list = []
        for loc in models.Location.objects.all():
            if loc.point:
                break
            elif loc.linestring:
                break
            else:
                non_spatial_location_list.append(loc)

        context['non_spatial_location_list'] = non_spatial_location_list

        # if there are bounding coords, we look in the box

        if self.kwargs.get("n"):
            bbox = box(
                float(self.kwargs.get("w")),
                float(self.kwargs.get("s")),
                float(self.kwargs.get("e")),
                float(self.kwargs.get("n")),
            )

            captured_locations_list = []
            captured_site_list = []
            for loc in location_qs:
                if loc not in non_spatial_location_list:
                    captured = False
                    # check to see if the bbox overlaps with any record points
                    if bbox.contains(loc.point) or bbox.contains(loc.end_point):
                        captured = True
                    # if checked through all records and nothing found, add to non-spatial list
                    if captured:
                        captured_locations_list.append(loc)
            for site in site_qs:
                # check to see if the bbox overlaps with any record points
                if bbox.intersects(site.bbox):
                    captured_site_list.append(site)
        else:
            captured_locations_list = []
            captured_site_list = []

        context["captured_locations_list"] = captured_locations_list
        context["captured_site_list"] = captured_site_list
        return context

    def get_initial(self, *args, **kwargs):
        if self.kwargs.get("start"):
            start_date = self.kwargs.get("start")
            end_date = self.kwargs.get("end")
        else:
            start_date = (datetime.datetime.now() - datetime.timedelta(days=5 * 365)).date()
            end_date = datetime.datetime.today()

        return {
            "north": self.kwargs.get("n"),
            "south": self.kwargs.get("s"),
            "east": self.kwargs.get("e"),
            "west": self.kwargs.get("w"),
            "start_date": start_date,
            "end_date": end_date,
        }

    def form_valid(self, form):
        kwarg_dict = {
            "n": form.cleaned_data.get("north"),
            "s": form.cleaned_data.get("south"),
            "e": form.cleaned_data.get("east"),
            "w": form.cleaned_data.get("west"),
            "start": form.cleaned_data.get("start_date"),
            "end": form.cleaned_data.get("end_date"),
        }
        if form.cleaned_data.get("rive_id"):
            kwarg_dict["rive_id"] = form.cleaned_data.get("rive_id").name
        return HttpResponseRedirect(reverse("bio_diversity:loc_map", kwargs=kwarg_dict))
