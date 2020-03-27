from django.test import TestCase, tag,  RequestFactory
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import CreateView, UpdateView

from shared_models import views, models


EXPECTED_LOGIN_URL = '/accounts/login_required/'
EXPECTED_TEMPLATE_NAME = 'shared_models/_entry_form.html'

EXPECTED_MOCK_TITLE = "Mock Title"


# This is used to simulate calling the as_veiw() function normally called in the urls.py
# this will return a view that can then have it's internal methods tested
def setup_view(view, request, *args, **kwargs):

    view.request = request
    view.args = args
    view.kwargs = kwargs
    return view


# mock example of extending the create common view used in testing
class MockCreateCommonView(views.CreateCommon):

    # These are required at a minimum by extending classes as part of Django's base framework
    model = models.Region
    fields = []

    # These are for testing purposes only
    auth = True
    editable = True

    # this should be overriden in an extending class to determine if a user is authorized to do certain actions
    def test_func(self):
        return self.auth

    # example of overriding the get_java_script function to return something other than the java_script variable
    def get_java_script(self):
        if self.kwargs.get("pop"):
            return "pop/{}".format(self.java_script)

        return super().get_java_script()

    # example of overriding the get_nav_menu function to return something other than the nav_menu variable
    def get_nav_menu(self):
        if self.kwargs.get("pop"):
            return "pop/{}".format(self.nav_menu)

        return super().get_nav_menu()

    # example of overriding the get_site_css function to return something other than the site_css variable
    def get_site_css(self):
        if self.kwargs.get("pop"):
            return "pop/{}".format(self.site_css)

        return super().get_site_css()


# mock example of extending the update common view used in testing, virtually the same as CreateCommon
class MockUpdateCommonView(views.UpdateCommon):

    # These are required at a minimum by extending classes as part of Django's base framework
    model = models.Region
    fields = []

    # These are for testing purposes only
    auth = True
    editable = True

    # this should be overriden in an extending class to determine if a user is authorized to do certain actions
    def test_func(self):
        return self.auth

    # example of overriding the get_java_script function to return something other than the java_script variable
    def get_java_script(self):
        if self.kwargs.get("pop"):
            return "pop/{}".format(self.java_script)

        return super().get_java_script()

    # example of overriding the get_nav_menu function to return something other than the nav_menu variable
    def get_nav_menu(self):
        if self.kwargs.get("pop"):
            return "pop/{}".format(self.nav_menu)

        return super().get_nav_menu()

    # example of overriding the get_site_css function to return something other than the site_css variable
    def get_site_css(self):
        if self.kwargs.get("pop"):
            return "pop/{}".format(self.site_css)

        return super().get_site_css()


# Testing for CommonCreate view, used in:
#  csas
#  whalesdb
class TestCreateCommon(TestCase):

    # In order to test users should be allowed to create database objects extending apps should make use of the test_
    # func method that comes from Django's django.contrib.auth.mixins.UserPassesTestMixin module. As such
    # the CreateCommon class is an abstract class with CreateView and UserPassesTestMixin as super classes
    def test_extends(self):
        view = views.CreateCommon()

        self.assertIsInstance(view, UserPassesTestMixin)
        self.assertIsInstance(view, CreateView)

    # This frame work expects app urls to take a form app_label:create_[key], app_label:update_[key],
    # app_label:details_[key], app_label:list_[key]. The default functionality is that these URL names will be
    # created where needed in the respective common view class. Specifiy a key in the extending class and
    # The create view will create context variables with the expected URL Name.
    def test_key(self):
        view = views.CreateCommon()

        # CreateCommon Should have the key
        self.assertTrue(hasattr(view, "key"))

        # The key should be null and overriden in an extending class. But be null in the parent
        self.assertIs(view.key, None)

    # This frame work allows for the inclusion of a nav_menu attribute, if present it will be
    # included in the base forms and a navigation menu displayed at the top of a page
    def test_nav_menu(self):
        view = views.CreateCommon()

        # CreateCommon Should have the attribute
        self.assertTrue(hasattr(view, "nav_menu"))

        # The attribute should be null and overriden in an extending class. But be null in the parent
        self.assertIs(view.nav_menu, None)

    # This frame work allows for the inclusion of a java_script attribute, if present it will be
    # included in the base forms
    def test_java_script(self):
        view = views.CreateCommon()

        # CreateCommon Should have the attribute
        self.assertTrue(hasattr(view, "java_script"))

        # The attribute should be null and overriden in an extending class. But be null in the parent
        self.assertIs(view.java_script, None)

    # This frame work allows for the inclusion of a site_css attribute, if present it will be
    # included in the base forms template
    def test_site_css(self):
        view = views.CreateCommon()

        # CreateCommon Should have the attribute
        self.assertTrue(hasattr(view, "site_css"))

        # The attribute should be null and overriden in an extending class. But be null in the parent
        self.assertIs(view.site_css, None)

    # All DM apps share a common login system so it makes sense that common views should direct
    # users to the common login URL
    def test_login_url(self):
        view = views.CreateCommon()

        # CreateCommon Should have the login_url attribute
        self.assertTrue(hasattr(view, "login_url"))

        # Expected Login URL
        self.assertEquals(view.login_url, EXPECTED_LOGIN_URL)

    # The shared templates have a common layout that will display a form's title, so the CommonCreate
    # get_context method will return the title set in an extending class.
    def test_title(self):
        view = views.CreateCommon()

        # CreateCommon Should have the title
        self.assertTrue(hasattr(view, "title"))

        # The title should be null and overriden in an extending class. But be null in the parent
        self.assertIs(view.title, None)

    def test_title_exception(self):
        # have to create the request and setup the view
        req_factory = RequestFactory()
        request = req_factory.get(EXPECTED_LOGIN_URL)
        view = setup_view(MockCreateCommonView(), request)
        view.object = models.Region()

        # The CommonCreate class will raise an exception if the dev forgot to set the title attribute
        self.assertRaises(AttributeError, view.get_context_data)

        view.title = EXPECTED_MOCK_TITLE

        # else the title should be returned by the get_title method
        self.assertEquals(view.get_title(), EXPECTED_MOCK_TITLE)

        # the context should contain a title element
        self.assertIn("title", view.get_context_data())
        self.assertEquals(view.get_context_data()['title'], EXPECTED_MOCK_TITLE)

    # Create common by default uses the simple shared_models/_entry_form.html template
    # Extending classes can provide their own templates modeled on the _entry_form.html Template
    def test_template(self):
        view = views.CreateCommon()
        self.assertEquals(view.template_name, EXPECTED_TEMPLATE_NAME)

    # if the test_func method returns true then the get_context method will return an auth element used by
    # templates to determine when to show/hide certain elements
    def test_get_context(self):
        # have to create the request and setup the view
        req_factory = RequestFactory()
        request = req_factory.get(EXPECTED_LOGIN_URL)
        view = setup_view(MockCreateCommonView(), request)
        view.object = models.Region()
        view.title = EXPECTED_MOCK_TITLE

        # the context should contain a title element
        self.assertIn("auth", view.get_context_data())
        self.assertTrue(view.get_context_data()['auth'])

        view.auth = False
        self.assertFalse(view.get_context_data()['auth'])

        self.assertNotIn("java_script", view.get_context_data())

        view.java_script = "some/location.js"
        self.assertIn("java_script", view.get_context_data())
        self.assertEquals(view.get_context_data()['java_script'], "some/location.js")

        self.assertNotIn("nav_menu", view.get_context_data())

        view.nav_menu = "some/nav.html"
        self.assertIn("nav_menu", view.get_context_data())
        self.assertEquals(view.get_context_data()['nav_menu'], "some/nav.html")

        self.assertNotIn("site_css", view.get_context_data())

        view.site_css = "some/site.css"
        self.assertIn("site_css", view.get_context_data())
        self.assertEquals(view.get_context_data()['site_css'], "some/site.css")

    # tests that if a kwarg pop is passed to the request the extended method in the mock class
    # can preform some operation on the java_script variable.
    def test_get_java_script(self):
        # have to create the request and setup the view
        req_factory = RequestFactory()
        request = req_factory.get(EXPECTED_LOGIN_URL)
        view = setup_view(MockCreateCommonView(), request, pop='pop')
        view.object = models.Region()
        view.title = EXPECTED_MOCK_TITLE

        view.java_script = "some/location.js"
        self.assertEquals(view.get_context_data()['java_script'], "pop/some/location.js")

    # tests that if a kwarg pop is passed to the request the extended method in the mock class
    # can preform some operation on the nav_menu variable.
    def test_get_nav_menu(self):
        # have to create the request and setup the view
        req_factory = RequestFactory()
        request = req_factory.get(EXPECTED_LOGIN_URL)
        view = setup_view(MockCreateCommonView(), request, pop='pop')
        view.object = models.Region()
        view.title = EXPECTED_MOCK_TITLE

        view.nav_menu = "some/location.js"
        self.assertEquals(view.get_context_data()['nav_menu'], "pop/some/location.js")

    # tests that if a kwarg pop is passed to the request the extended method in the mock class
    # can preform some operation on the site_css variable.
    def test_get_site_css(self):
        # have to create the request and setup the view
        req_factory = RequestFactory()
        request = req_factory.get(EXPECTED_LOGIN_URL)
        view = setup_view(MockCreateCommonView(), request, pop='pop')
        view.object = models.Region()
        view.title = EXPECTED_MOCK_TITLE

        view.site_css = "some/location.js"
        self.assertEquals(view.get_context_data()['site_css'], "pop/some/location.js")


# Testing for CommonUpdate view, used in:
#  csas
#  whalesdb
class TestUpdateCommon(TestCase):

    # In order to test users should be allowed to create database objects extending apps should make use of the test_
    # func method that comes from Django's django.contrib.auth.mixins.UserPassesTestMixin module. As such
    # the UpdateCommon class is an abstract class with UpdateView and UserPassesTestMixin as super classes
    def test_extends(self):
        view = views.UpdateCommon()

        self.assertIsInstance(view, UserPassesTestMixin)
        self.assertIsInstance(view, UpdateView)

    # This frame work expects app urls to take a form app_label:create_[key], app_label:update_[key],
    # app_label:details_[key], app_label:list_[key]. The default functionality is that these URL names will be
    # created where needed in the respective common view class. Specifiy a key in the extending class and
    # The create view will create context variables with the expected URL Name.
    def test_key(self):
        view = views.UpdateCommon()

        # UpdateCommon Should have the key
        self.assertTrue(hasattr(view, "key"))

        # The key should be null and overriden in an extending class. But be null in the parent
        self.assertIs(view.key, None)

    # This frame work allows for the inclusion of a nav_menu attribute, if present it will be
    # included in the base forms and a navigation menu displayed at the top of a page
    def test_nav_menu(self):
        view = views.UpdateCommon()

        # UpdateCommon Should have the attribute
        self.assertTrue(hasattr(view, "nav_menu"))

        # The attribute should be null and overriden in an extending class. But be null in the parent
        self.assertIs(view.nav_menu, None)

    # This frame work allows for the inclusion of a java_script attribute, if present it will be
    # included in the base forms
    def test_java_script(self):
        view = views.UpdateCommon()

        # UpdateCommon Should have the attribute
        self.assertTrue(hasattr(view, "java_script"))

        # The attribute should be null and overriden in an extending class. But be null in the parent
        self.assertIs(view.java_script, None)

    # This frame work allows for the inclusion of a site_css attribute, if present it will be
    # included in the base forms template
    def test_site_css(self):
        view = views.UpdateCommon()

        # UpdateCommon Should have the attribute
        self.assertTrue(hasattr(view, "site_css"))

        # The attribute should be null and overriden in an extending class. But be null in the parent
        self.assertIs(view.site_css, None)

    # All DM apps share a common login system so it makes sense that common views should direct
    # users to the common login URL
    def test_login_url(self):
        view = views.UpdateCommon()

        # UpdateCommon Should have the login_url attribute
        self.assertTrue(hasattr(view, "login_url"))

        # Expected Login URL
        self.assertEquals(view.login_url, EXPECTED_LOGIN_URL)

    # The shared templates have a common layout that will display a form's title, so the CommonUpdate
    # get_context method will return the title set in an extending class.
    def test_title(self):
        view = views.UpdateCommon()

        # UpdateCommon Should have the title
        self.assertTrue(hasattr(view, "title"))

        # The title should be null and overriden in an extending class. But be null in the parent
        self.assertIs(view.title, None)

    def test_title_exception(self):
        # have to create the request and setup the view
        req_factory = RequestFactory()
        request = req_factory.get(EXPECTED_LOGIN_URL)
        view = setup_view(MockUpdateCommonView(), request)
        view.object = models.Region()

        # The CommonUpdate class will raise an exception if the dev forgot to set the title attribute
        self.assertRaises(AttributeError, view.get_context_data)

        view.title = EXPECTED_MOCK_TITLE

        # else the title should be returned by the get_title method
        self.assertEquals(view.get_title(), EXPECTED_MOCK_TITLE)

        # the context should contain a title element
        self.assertIn("title", view.get_context_data())
        self.assertEquals(view.get_context_data()['title'], EXPECTED_MOCK_TITLE)

    # Update common by default uses the simple shared_models/_entry_form.html template
    # Extending classes can provide their own templates modeled on the _entry_form.html Template
    def test_template(self):
        view = views.UpdateCommon()
        self.assertEquals(view.template_name, EXPECTED_TEMPLATE_NAME)

    # if the test_func method returns true then the get_context method will return an auth element used by
    # templates to determine when to show/hide certain elements
    def test_get_context(self):
        # have to create the request and setup the view
        req_factory = RequestFactory()
        request = req_factory.get(EXPECTED_LOGIN_URL)
        view = setup_view(MockUpdateCommonView(), request)
        view.object = models.Region()
        view.title = EXPECTED_MOCK_TITLE

        # the context should contain a title element
        self.assertIn("auth", view.get_context_data())
        self.assertTrue(view.get_context_data()['auth'])

        view.auth = False
        self.assertFalse(view.get_context_data()['auth'])

        self.assertNotIn("java_script", view.get_context_data())

        view.java_script = "some/location.js"
        self.assertIn("java_script", view.get_context_data())
        self.assertEquals(view.get_context_data()['java_script'], "some/location.js")

        self.assertNotIn("nav_menu", view.get_context_data())

        view.nav_menu = "some/nav.html"
        self.assertIn("nav_menu", view.get_context_data())
        self.assertEquals(view.get_context_data()['nav_menu'], "some/nav.html")

        self.assertNotIn("site_css", view.get_context_data())

        view.site_css = "some/site.css"
        self.assertIn("site_css", view.get_context_data())
        self.assertEquals(view.get_context_data()['site_css'], "some/site.css")

    # tests that if a kwarg pop is passed to the request the extended method in the mock class
    # can preform some operation on the java_script variable.
    def test_get_java_script(self):
        # have to create the request and setup the view
        req_factory = RequestFactory()
        request = req_factory.get(EXPECTED_LOGIN_URL)
        view = setup_view(MockUpdateCommonView(), request, pop='pop')
        view.object = models.Region()
        view.title = EXPECTED_MOCK_TITLE

        view.java_script = "some/location.js"
        self.assertEquals(view.get_context_data()['java_script'], "pop/some/location.js")

    # tests that if a kwarg pop is passed to the request the extended method in the mock class
    # can preform some operation on the nav_menu variable.
    def test_get_nav_menu(self):
        # have to create the request and setup the view
        req_factory = RequestFactory()
        request = req_factory.get(EXPECTED_LOGIN_URL)
        view = setup_view(MockUpdateCommonView(), request, pop='pop')
        view.object = models.Region()
        view.title = EXPECTED_MOCK_TITLE

        view.nav_menu = "some/location.js"
        self.assertEquals(view.get_context_data()['nav_menu'], "pop/some/location.js")

    # tests that if a kwarg pop is passed to the request the extended method in the mock class
    # can preform some operation on the site_css variable.
    def test_get_site_css(self):
        # have to create the request and setup the view
        req_factory = RequestFactory()
        request = req_factory.get(EXPECTED_LOGIN_URL)
        view = setup_view(MockUpdateCommonView(), request, pop='pop')
        view.object = models.Region()
        view.title = EXPECTED_MOCK_TITLE

        view.site_css = "some/location.js"
        self.assertEquals(view.get_context_data()['site_css'], "pop/some/location.js")