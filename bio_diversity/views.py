from django.views.generic import TemplateView, DetailView
from shared_models.views import CommonAuthCreateView, CommonAuthFilterView, CommonAuthUpdateView
from django.urls import reverse_lazy

from . import mixins, filters, utils


class IndexTemplateView(TemplateView):
    nav_menu = 'bio_diversity/bio_diversity_nav_menu.html'
    site_css = 'bio_diversity/bio_diversity_css.css'
    home_url_name = "bio_diversity:index"

    template_name = 'bio_diversity/index.html'


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

        return init

    # Upon success most creation views will be redirected to their respective 'CommonList' view. To send
    # a successful creation view somewhere else, override this method
    def get_success_url(self):
        success_url = self.success_url if self.success_url else reverse_lazy("bio_diversity:list_{}".format(self.key))

        if self.kwargs.get("pop"):
            # create views intended to be pop out windows should close the window upon success
            success_url = reverse_lazy("shared_models:close_me_no_refresh")

        return success_url

    # overrides the UserPassesTestMixin test to check that a user belongs to the whalesdb_admin group
    def test_func(self):
        return utils.bio_diverisity_authorized(self.request.user)


class InstCreate(mixins.InstMixin, CommonCreate):
    pass


class InstcCreate(mixins.InstcMixin, CommonCreate):
    pass


class InstdCreate(mixins.InstdMixin, CommonCreate):
    pass


class InstdcCreate(mixins.InstdcMixin, CommonCreate):
    pass


class OrgaCreate(mixins.OrgaMixin, CommonCreate):
    pass


class ProgaCreate(mixins.ProgaMixin, CommonCreate):
    pass


class ProtcCreate(mixins.ProtcMixin, CommonCreate):
    pass


class ProtfCreate(mixins.ProtfMixin, CommonCreate):
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.title:
            context['title'] = self.title

        if self.fields:
            context['fields'] = self.fields

        context['list_url'] = self.list_url if self.list_url else "bio_diversity:list_{}".format(self.key)
        context['update_url'] = self.update_url if self.update_url else "bio_diversity:update_{}".format(self.key)
        # for the most part if the user is authorized then the content is editable
        # but extending classes can choose to make content not editable even if the user is authorized
        context['auth'] = utils.bio_diverisity_authorized(self.request.user)
        context['editable'] = context['auth'] and self.editable

        return context


class InstDetails(mixins.InstMixin, CommonDetails):
    fields = ["instc", "serial_number", "comments", "created_by", "created_date", ]


class InstcDetails(mixins.InstcMixin, CommonDetails):
    fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class InstdDetails(mixins.InstdMixin, CommonDetails):
    fields = ["inst", "instdc", "det_value", "start_date", "end_date", "valid", "created_by", "created_date", ]


class InstdcDetails(mixins.InstdcMixin, CommonDetails):
    fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class OrgaDetails(mixins.OrgaMixin, CommonDetails):
    fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class ProgaDetails(mixins.ProgaMixin, CommonDetails):
    fields = ["proga_last_name", "proga_first_name", "created_by", "created_date", ]


class ProtcDetails(mixins.ProtcMixin, CommonDetails):
    fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class ProtfDetails(mixins.ProtfMixin, CommonDetails):
    fields = ["prot_id", "protf_file", "comments", "created_by", "created_date", ]


# ----------------------------LIST VIEWS-----------------------------
class CommonList(CommonAuthFilterView):

    nav_menu = 'bio_diversity/bio_diversity_nav.html'
    site_css = 'bio_diversity/bio_diversity.css'
    home_url_name = "bio_diversity:index"

    # fields to be used as columns to display an object in the filter view table
    fields = []

    # URL to use to create a new object to be added to the filter view
    create_url = None

    # URL to use for the details button element in the filter view's list
    details_url = None

    # URL to use for the update button element in the filter view's list
    update_url = None

    # URL to use for the delete button element in the filter view's list
    delete_url = False

    # The height of the popup dialog used to display the creation/update form
    # if not set by the extending class the default popup height will be used
    creation_form_height = None

    # By default Listed objects will have an update button, set editable to false in extending classes to disable
    editable = True

    def get_fields(self):
        if self.fields:
            return self.fields

        return ['tname|Name', 'tdescription|Description']

    def get_create_url(self):
        return self.create_url if self.create_url is not None else "bio_diversity:create_{}".format(self.key)

    def get_details_url(self):
        return self.details_url if self.details_url is not None else "bio_diversity:details_{}".format(self.key)

    def get_update_url(self):
        return self.update_url if self.update_url is not None else "bio_diversity:update_{}".format(self.key)

    def get_delete_url(self):
        return self.delete_url if self.delete_url is not None else "bio_diversity:delete_{}".format(self.key)

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(*args, object_list=object_list, **kwargs)

        context['fields'] = self.get_fields()

        # if the url is not None, use the value specified by the url variable.
        # if the url is None, create a url using the views key
        # this way if no URL, say details_url, is provided it's assumed the default RUL will be 'whalesdb:details_key'
        # if the details_url = False in the extending view then False will be passed to the context['detials_url']
        # variable and in the template where the variable is used for buttons and links the button and/or links can
        # be left out without causing URL Not Found issues.
        context['create_url'] = self.get_create_url()
        context['details_url'] = self.get_details_url()
        context['update_url'] = self.get_update_url()
        context['delete_url'] = self.get_delete_url()

        # for the most part if the user is authorized then the content is editable
        # but extending classes can choose to make content not editable even if the user is authorized
        # context['auth'] = utils.whales_authorized(self.request.user)
        context['editable'] = context['auth'] and self.editable

        if self.creation_form_height:
            context['height'] = self.creation_form_height

        return context


class InstList(mixins.InstMixin, CommonList):
    filterset_class = filters.InstFilter
    fields = ["instc", "serial_number", "comments", "created_by", "created_date", ]


class InstcList(mixins.InstcMixin, CommonList):
    filterset_class = filters.InstcFilter
    fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class InstdList(mixins.InstdMixin, CommonList):
    filterset_class = filters.InstdFilter
    fields = ["inst", "instdc", "created_by", "created_date", ]


class InstdcList(mixins.InstdcMixin, CommonList):
    filterset_class = filters.InstdcFilter
    fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]
    

class OrgaList(mixins.OrgaMixin, CommonList):
    filterset_class = filters.OrgaFilter
    fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class ProgaList(mixins.ProgaMixin, CommonList):
    filterset_class = filters.ProgaFilter
    fields = ["proga_last_name", "proga_first_name", "created_by", "created_date", ]


class ProtcList(mixins.ProtcMixin, CommonList):
    filterset_class = filters.ProtcFilter
    fields = ["name", "nom", "description_en", "description_fr", "created_by", "created_date", ]


class ProtfList(mixins.ProtfMixin, CommonList):
    filterset_class = filters.ProtfFilter
    fields = ["prot_id", "protf_file", "comments", "created_by", "created_date", ]


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

        init["created_by"] = self.request.user.username

        return init

    # this function overrides UserPassesTestMixin.test_func() to determine if
    # the user should have access to this content, if the user is logged in
    # This function could be overridden in extending classes to preform further testing to see if
    # an object is editable
    def test_func(self):
        return utils.bio_diverisity_authorized(self.request.user)

    # Get context returns elements used on the page. Make sure when extending to call
    # context = super().get_context_data(**kwargs) so that elements created in the parent
    # class are inherited by the extending class.
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editable'] = context['auth']
        return context


class InstUpdate(mixins.InstMixin, CommonUpdate):
    pass


class InstcUpdate(mixins.InstcMixin, CommonUpdate):
    pass


class InstdUpdate(mixins.InstdMixin, CommonUpdate):
    pass


class InstdcUpdate(mixins.InstdcMixin, CommonUpdate):
    pass


class OrgaUpdate(mixins.OrgaMixin, CommonUpdate):
    pass


class ProgaUpdate(mixins.ProgaMixin, CommonUpdate):
    pass


class ProtcUpdate(mixins.ProtcMixin, CommonUpdate):
    pass


class ProtfUpdate(mixins.ProtfMixin, CommonUpdate):
    pass
