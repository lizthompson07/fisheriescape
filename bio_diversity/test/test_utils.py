import os
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.messages import get_messages
from django.test import tag
from django.urls import reverse, resolve
from django.utils.translation import activate
from faker import Faker
from html2text import html2text

from bio_diversity.test import BioFactoryFloor
from bio_diversity import utils
from csas2.models import CSASAdminUser
from ppt.models import PPTAdminUser
from shared_models.test.SharedModelsFactoryFloor import UserFactory, GroupFactory
from shared_models.test.common_tests import CommonTest
from django.test import TransactionTestCase
from random import randint

from travel.models import TravelUser

faker = Faker()

fixtures_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fixtures')
standard_fixtures = [file for file in os.listdir(fixtures_dir)]


def setup_view(view, request, *args, **kwargs):
    view.request = request
    view.args = args
    view.kwargs = kwargs
    return view


class CommonTransactionTest(TransactionTestCase):
    fixtures = standard_fixtures

    login_url_base = '/accounts/login/?next='
    login_url_en = login_url_base + "/en/"
    login_url_fr = login_url_base + "/fr/"
    expected_form = None

    # use when a user needs to be logged in.
    def get_and_login_user(self, user=None, in_group=None, is_superuser=False, in_national_admin_group=False):
        """
        this function is a handy way to log in a user to the testing client.
        :param user: optional user to be logged in
        :param in_group: optional group to have the user assigned to
        :param is_superuser: is the user a superuser?
        :param in_national_admin_group: supplying True will put the user as either a travel, csas or project admin; with access to shared models org structure
        """
        if not user:
            user = UserFactory()
        login_successful = self.client.login(username=user.username, password=UserFactory.get_test_password())
        self.assertEqual(login_successful, True)
        if in_group:
            group = GroupFactory(name=in_group)
            user.groups.add(group)
        if is_superuser:
            user.is_superuser = True
            user.save()

        if in_national_admin_group:
            case = faker.pyint(1, 3)
            if case == 1:  # travel
                TravelUser.objects.create(user=user, is_national_admin=True)
            elif case == 2:  # csas
                CSASAdminUser.objects.create(user=user, is_national_admin=True)
            elif case == 3:  # csas
                PPTAdminUser.objects.create(user=user, is_national_admin=True)
        return user

    def assert_user_access_denied(self, test_url, user, locales=('en', 'fr'), expected_code=302,
                                  login_search_term=None):
        """
        this test will ensure that a specified user does not have access to a given url
       :param test_url: the url to test
       :param user: user to test access
       :param locales: the locales to test
       :param expected_code: the expected http response code; default would be a 302 since we are expecting redirection
       :param login_search_term: the search term to use when confirming a login redirect
       """
        self.client.logout()
        # perform this test for each locale
        for l in locales:
            activate(l)
            login_url = f"{self.login_url_base}{test_url}" if not login_search_term else login_search_term

            # login a user
            self.get_and_login_user(user=user)
            # get a response
            response = self.client.get(test_url)
            # we are expecting to see the login url
            self.assertEquals(expected_code, response.status_code)
            self.assertIn(f"{login_url}", response.url)
            self.client.logout()

    def assert_non_public_view(self, test_url, locales=('en', 'fr'), expected_template=None, user=None,
                               expected_code=200, login_search_term=None, bad_user_list=[]):
        """
        This test will ensure a view requires a user to be logged in in order to access it. Part 1, will test to see
        what happens when an anonymous user tries accessing the url. Part 2 attempt the same this with a logged in user.
        If the `user` arg is provided, it will be used for Part 2.
        :param test_url: the url to test
        :param locales: the locales to test
        :param expected_template: the expected template file
        :param expected_code: the expected http response code
        :param user: an optional user to use for the second part of this test
        :param login_search_term: the search term to use when confirming a login redirect
        :param bad_user_list: a list of users to check to make sure that they do not have access
        """

        # perform this test for each locale
        for l in locales:
            activate(l)
            login_url = f"{self.login_url_base}{test_url}" if not login_search_term else login_search_term

            # PART 1: try accessing with an Anonymous user

            # make sure there is no one already logged in
            self.client.logout()
            response = self.client.get(test_url)
            # with Anonymous User, a 302 response is expected
            self.assertEquals(302, response.status_code)
            # we are expecting to see the login url
            self.assertIn(f"{login_url}", response.url)

            # PART 2: try accessing with the bad users
            for u in bad_user_list:
                # make sure there is no one already logged in
                self.client.logout()
                self.get_and_login_user(user=u)
                response = self.client.get(test_url)
                # a 403 response would be expected here
                possibility_1 = 403 == response.status_code
                possibility_2 = 302 == response.status_code and "denied" in response.url
                self.assertTrue(possibility_1 or possibility_2)

            # PART 3: try with a logged in user. user the User provided in args, if available
            # login a random user if one was not provided by args
            self.get_and_login_user(user=user)

            # must get a new response, but don't know which.
            response = self.client.get(test_url)
            self.assertEquals(expected_code, response.status_code)
            # there is a problem here. If the expected response is a 302, it will be hard to differentiate between this
            # and the login redirect. So we will make sure that the redirect url (if present) does not contain the
            # `accounts/login ...`
            if hasattr(response, "url"):
                self.assertNotIn(f"{login_url}", response.url)

            # if an expected template was provided, test it against the template_name in the response
            if expected_template:
                self.assertIn(expected_template, response.template_name)
            self.client.logout()

    def assert_public_view(self, test_url, locales=('en', 'fr'), expected_template=None, expected_code=200,
                           login_search_term=None):
        """
        ensure a view is a public view, ie. it is accessible to an Anonymous user with a
        :param test_url: the url to test
        :param locales: the locales to test
        :param expected_template: the expected template file
        :param expected_code: the expected http response code
        :param login_search_term: the search term to use when confirming a login redirect
        """
        for l in locales:
            activate(l)
            login_url = f"{self.login_url_base}{test_url}" if not login_search_term else login_search_term

            response = self.client.get(test_url)
            self.assertEquals(expected_code, response.status_code)

            # there is a problem here. If the expected response is a 302, it will be hard to differentiate between this and the login
            # redirect. So we will make sure that the redirect url (if present) does not contain the `accounts/login ...`
            if hasattr(response, "url"):
                self.assertNotIn(f"{login_url}", response.url)

            # if an expected template was provided, test it against the template_name in the response
            if expected_template:
                self.assertIn(expected_template, response.template_name)
            self.client.logout()

    def assert_good_response(self, test_url, locales=('en', 'fr'), anonymous=True):
        """
        This will test check to see if the test url returns something bad like a 404 or a 500 response
        :param test_url: the url to test
        :param locales: the locales to test
        :param anonymous: should the test be run anonymously? default is True
        """
        if anonymous:
            self.client.logout()
        # perform this test for each locale
        for l in locales:
            # make sure we use an anonymous user
            activate(l)
            response = self.client.get(test_url)
            self.assertNotIn(response.status_code, [404, 500, ])

    def assert_inheritance(self, test_child_class, test_parent_class):
        """
        this will test to see if the child is a subclass of the parent.
        :param test_child_class:
        :param test_parent_class:
        """
        # perform this test for each locale
        self.assertTrue(issubclass(test_child_class, test_parent_class))

    def assert_field_in_field_list(self, test_url, name_of_field_list, fields_to_test, user=None):
        """
        this test looks for a field list in the context variable and checks to see if there is a specific field name in
        there
        :param test_url:
        :param name_of_field_list: the name of the field list (e.g. `field_list`)
        :param fields_to_test: list of fields to check for
        :param user: an optional user to use for producing the http response
        """
        activate('en')
        self.get_and_login_user(user=user)
        response = self.client.get(test_url)
        for field in fields_to_test:
            self.assertIn(field, response.context[name_of_field_list])

    def assert_field_not_in_field_list(self, test_url, name_of_field_list, fields_to_test, user=None):
        """
        this test looks for a field list in the context variable and checks to confirm a specific field name is not in there
        :param test_url:
        :param name_of_field_list: the name of the field list (e.g. `field_list`)
        :param fields_to_test: list of fields to check for
        :param user: an optional user to use for producing the http response
        """
        activate('en')
        self.get_and_login_user(user=user)
        response = self.client.get(test_url)
        for field in fields_to_test:
            self.assertNotIn(field, response.context[name_of_field_list])

    def assert_presence_of_context_vars(self, test_url, context_var_list, user=None):
        """
        this test looks to ensure that a specific context var is present in the template context variable
        :param test_url:
        :param context_var_list: a list of name of context var to search for
        :param user: an optional user to use for producing the http response
        """
        activate('en')
        reg_user = self.get_and_login_user(user=user)
        response = self.client.get(test_url)
        for context_var in context_var_list:
            self.assertIn(context_var, response.context)

    def assert_value_of_context_var(self, test_url, context_var, expected_value, user=None):
        """
        this test looks to ensure that a specific context var is present in the template context variable
        :param test_url:
        :param context_var: name of context var to search for
        :param expected_value: expected value of context var
        :param user: an optional user to use for producing the http response
        """
        activate('en')
        reg_user = self.get_and_login_user(user=user)
        response = self.client.get(test_url)

        self.assertIn(context_var, response.context)
        self.assertEqual(response.context.get(context_var), expected_value)

    def assert_correct_url(self, test_url_name, expected_url_path, test_url_args=None):
        # arbitrarily activate the english locale
        activate('en')
        my_path = reverse(test_url_name, args=test_url_args)
        self.assertEqual(my_path, f'{expected_url_path}')

    # Tests for API views
    #################
    def assert_dict_has_keys(self, my_dict, keys):
        # arbitrarily activate the english locale
        for key in keys:
            self.assertIn(key, my_dict)

    # Tests for forms (create, update, delete and form views)
    #################

    def assert_correct_form_class(self, test_view, expected_form_class):
        """
        check that the formview is using the correct form class
        :param test_view: the view to test
        :param expected_form_class: the expected form class
        """
        activate("en")
        self.assertEquals(test_view, expected_form_class)

    def assert_success_url(self, test_url, data=None, user=None, expected_url_name=None, expected_success_url=None,
                           use_anonymous_user=False, file_field_name=None, expected_code=302):
        """
        test that upon a successful form the view redirects to the expected success url
        :param test_url: URL being tested
        :param data: optional data to use when submitting the form
        :param user: an optional user that can be used to generate the response
        :param expected_url_name: the name of the url to which a successful submission should be redirected
        :param expected_success_url: the url to which a successful submission should be redirected
        :param use_anonymous_user: should this function be run without logging in a uer? if so, set this optional arg
        to true
        :param file_field_name: For the occasion a file is created for a model this is the name of the column the file
        data will be stored in
        """
        # arbitrarily activate the english locale
        activate('en')

        # if a user is provided in the arg, log in with that user
        if not use_anonymous_user:
            self.get_and_login_user(user)

        if data and file_field_name:
            with open(os.path.join(settings.BASE_DIR, "static", "img", "inventory", "good to go.jpg"), mode='rb') as fp:
                data[file_field_name] = fp
                response = self.client.post(test_url, data=data, )
        else:
            response = self.client.post(test_url, data=data)

        if response.context and 'form' in response.context:
            # If the data in this test is invaild the response will be invalid
            self.assertTrue(response.context_data['form'].is_valid(),
                            msg=f"\n\nTest data was likely invalid. \n\nHere's the error log from the form:\n"
                                f" {html2text(str(response.context_data['form'].errors))}"
                                f"Here's the data from the form:\n{response.context_data['form'].data}")

        # should always result in a redirect response
        self.assertEquals(expected_code, response.status_code)

        # if a url name was provided
        if expected_url_name:
            self.assertEquals(expected_url_name, resolve(response.url).view_name)

        if expected_success_url:
            self.assertRedirects(response=response, expected_url=expected_success_url)

    def assert_message_returned_url(self, test_url, data=None, user=None, expected_messages=None,
                                    use_anonymous_user=False):
        """
        test that upon a successful form the view redirects to the expected success url
        :param test_url: URL being tested
        :param data: optional data to use when submitting the form
        :param user: an optional user that can be used to generate the response
        :param expected_url_name: the name of the url to which a successful submission should be redirected
        :param use_anonymous_user: should this function be run without logging in a uer? if so, set this optional arg
        :param expected_messages: List of messages expected to be returned from the form_valid method
        data will be stored in
        """
        # arbitrarily activate the english locale
        activate('en')

        # if a user is provided in the arg, log in with that user
        if not use_anonymous_user:
            self.get_and_login_user(user)

        response = self.client.post(test_url, data=data)
        messages = list(get_messages(response.wsgi_request))
        for m in expected_messages:
            self.assertIn(m, [m.message for m in messages])

    def assert_form_valid(self, form_class, data, instance=None, initial=None):
        """
        assert that upon submission a form is valid.
        :param Form: the form instance to test
        :param data: the data to use when testing the form
        :param instance: an instance of some model to use when testing the form. applicable to ModelForms only
        :param initial: initial kwargs to pass into the form upon initialization
        """
        if instance:
            form = form_class(data=data, instance=instance, initial=initial)
        else:
            form = form_class(data=data, initial=initial)
        self.assertTrue(form.is_valid(),
                        msg=f"\n\nTest data was likely invalid. \n\nHere's the error log from the form: \n{html2text(str(form.errors))}"
                            f"Here's the data from the form:\n{form.data}")

    def assert_form_invalid(self, form_class, data, instance=None, initial=None):
        """
        assert that upon submission a form is invalid.
        :param Form: the form instance to test
        :param data: the data to use when testing the form
        :param instance: an instance of some model to use when testing the form. applicable to ModelForms only
        """
        if instance:
            form = form_class(data, instance=instance, initial=initial)
        else:
            form = form_class(data, initial=initial)
        self.assertFalse(form.is_valid())

    def assert_field_in_form(self, Form, field_name, instance=None, initial=None):
        """
        assert that a form contains a specific field
        :param Form: the form instance to test
        :param field_name: the name of the field to check for
        :param instance: an instance of some model to use when testing the form. applicable to ModelForms only
        """

        if instance:
            form = Form(instance=instance, initial=initial)
        else:
            form = Form(initial=initial)
        self.assertIn(field_name, form.fields)

    def assert_field_not_in_form(self, Form, field_name, instance=None, initial=None):
        """
        assert that a form does not contains a specific field
        :param Form: the form instance to test
        :param field_name: the name of the field to check for
        :param instance: an instance of some model to use when testing the form. applicable to ModelForms only
        """
        if instance:
            form = Form(instance=instance, initial=initial)
        else:
            form = Form(initial=initial)
        self.assertNotIn(field_name, form.fields)

    # Tests for models
    ##################
    def assert_unique_fields(self, model, field_names):
        """
        assert that a field within a model is unique
        :param model: the model class to test
        :param field_names: list of  field names to check
        """
        for field_name in field_names:
            field = [field for field in model._meta.fields if field.name == field_name][0]
            self.assertTrue(field.unique)

    def assert_mandatory_fields(self, model, field_names):
        """
        assert that a field within a model is mandatory (blank=False, null=False)
        :param model: the model class to test
        :param field_names: list of  field names to check
        """
        for field_name in field_names:
            field = [field for field in model._meta.fields if field.name == field_name][0]
            self.assertFalse(field.blank)
            self.assertFalse(field.null)

    def assert_non_mandatory_fields(self, model, field_names):
        """
        assert that a field within a model is not mandatory (blank=True, null=True)
        :param model: the model class to test
        :param field_names: list of  field names to check
        """
        for field_name in field_names:
            field = [field for field in model._meta.fields if field.name == field_name][0]
            self.assertTrue(field.blank)
            self.assertTrue(field.null)

    def assert_has_fields(self, model, fields):
        """
        assert that a model has specified field names
        :param model: the model class to test
        :param fields: list of  field names to check
        """
        model_field_list = [field.name for field in model._meta.fields] + \
                           [field.name for field in model._meta.many_to_many]
        for field in fields:
            self.assertIn(field, model_field_list)

    def assert_has_props(self, model, props):
        """
        assert that a model has specified props
        :param model: the model class to test
        :param props: list of  field names to check
        """
        for prop in props:
            self.assertTrue(hasattr(model, prop))














@tag("Grp", "Move", "Utils")
class TestGrpMove(TransactionTestCase):
    fixtures = ["initial_data.json"]

    def setUp(self):
        super().setUp()  # used to import fixtures

        # create group, tank and evnt
        self.grp = BioFactoryFloor.GrpFactory()
        self.evnt = BioFactoryFloor.EvntFactory()
        self.tank = BioFactoryFloor.TankFactory()
        self.tank.facic_id = self.evnt.facic_id
        self.tank.save()
        self.move_date = utils.naive_to_aware(datetime.now().date())
        self.final_tank = BioFactoryFloor.TankFactory()
        self.final_tank.facic_id = self.evnt.facic_id
        self.final_tank.save()
        self.cleaned_data = {
            "facic_id": self.evnt.facic_id,
            "evnt_id": self.evnt,
            "created_by": self.evnt.created_by,
            "created_date": self.evnt.created_date,
        }

    def test_grp_in_cont(self):
        # test a group with a moveDet is in one and only one tank:
        utils.enter_move(self.cleaned_data, None, self.tank, self.move_date, grp_pk=self.grp.pk)
        self.assertEqual(self.grp.current_cont()[0], self.tank)
        self.assertEqual(len(self.grp.current_cont()), 1)

    def test_cont_has_grp(self):
        # test a tank with a moveDet has one and only one group in it:
        utils.enter_move(self.cleaned_data, None, self.tank, self.move_date, grp_pk=self.grp.pk)
        indv_list, grp_list = self.tank.fish_in_cont()
        self.assertEqual(len(grp_list), 1)
        self.assertIn(self.grp, grp_list)

    def test_move_grp(self):
        # grp in one tank, gets moved, is in second tank and not in first tank
        utils.enter_move(self.cleaned_data, None, self.tank, self.move_date, grp_pk=self.grp.pk)
        indv_list, grp_list = self.tank.fish_in_cont()
        self.assertIn(self.grp, grp_list)
        utils.enter_move(self.cleaned_data, self.tank, self.final_tank, self.move_date, grp_pk=self.grp.pk)
        indv_list, grp_list = self.tank.fish_in_cont()
        self.assertNotIn(self.grp, grp_list)
        indv_list, grp_list = self.final_tank.fish_in_cont()
        self.assertIn(self.grp, grp_list)

    def test_two_grps_one_tank(self):
        #  put two grps into a single tank, make sure both are located:
        second_grp = BioFactoryFloor.GrpFactory()
        utils.enter_move(self.cleaned_data, None, self.tank, self.move_date, grp_pk=self.grp.pk)
        utils.enter_move(self.cleaned_data, None, self.tank, self.move_date, grp_pk=second_grp.pk)
        indv_list, grp_list = self.tank.fish_in_cont()
        self.assertEqual(len(grp_list), 2)
        self.assertIn(self.grp, grp_list)
        self.assertIn(second_grp, grp_list)

    def test_fix_jumped_tanks(self):
        # simulate accidentally recording group in wrong tank and correcting:
        # ie A->B, C->D (fish is in both B and D) ->E should correct this
        tank_a = BioFactoryFloor.TankFactory(name="A")
        tank_a.facic_id = self.evnt.facic_id
        tank_a.save()
        tank_b = BioFactoryFloor.TankFactory(name="B")
        tank_b.facic_id = self.evnt.facic_id
        tank_b.save()
        tank_c = BioFactoryFloor.TankFactory(name="C")
        tank_c.facic_id = self.evnt.facic_id
        tank_c.save()
        tank_d = BioFactoryFloor.TankFactory(name="D")
        tank_d.facic_id = self.evnt.facic_id
        tank_d.save()
        tank_e = BioFactoryFloor.TankFactory(name="E")
        tank_e.facic_id = self.evnt.facic_id
        tank_e.save()
        # need three dates to ensure unique moving events, to keep django test env happy
        move_a_date = (datetime.now() - timedelta(days=2)).date()
        move_b_date = (datetime.now() - timedelta(days=1)).date()
        move_c_date = datetime.now().date()

        utils.enter_move(self.cleaned_data, tank_a, tank_b, move_a_date, grp_pk=self.grp.pk)
        utils.enter_move(self.cleaned_data, tank_c, tank_d, move_b_date, grp_pk=self.grp.pk)
        self.assertIn(tank_b, self.grp.current_cont())
        self.assertIn(tank_d, self.grp.current_cont())
        utils.enter_move(self.cleaned_data, None, tank_e, move_c_date, grp_pk=self.grp.pk)
        self.assertIn(tank_e, self.grp.current_cont())
        self.assertNotIn(tank_c, self.grp.current_cont())
        self.assertNotIn(tank_d, self.grp.current_cont())

    def test_origin_only_tank(self):
        #  move group with only origin, make sure group is still in original tank
        utils.enter_move(self.cleaned_data, None, self.tank, self.move_date, grp_pk=self.grp.pk)
        utils.enter_move(self.cleaned_data, self.tank, None, self.move_date, grp_pk=self.grp.pk)
        indv_list, grp_list = self.tank.fish_in_cont()
        self.assertIn(self.grp, grp_list)

    def test_origin_destination_tank(self):
        #  move group with origin == destination, make sure group is in original tank:
        utils.enter_move(self.cleaned_data, None, self.tank, self.move_date, grp_pk=self.grp.pk)
        utils.enter_move(self.cleaned_data, self.tank, self.tank, self.move_date, grp_pk=self.grp.pk)

        indv_list, grp_list = self.tank.fish_in_cont()
        self.assertIn(self.grp, grp_list)


@tag("Grp", "Move", "Cnt", "Utils")
class TestGrpMoveCnt(TransactionTestCase):
    fixtures = ["initial_data.json"]

    def setUp(self):
        super().setUp()  # used to import fixtures

        # create group, tank and evnt
        self.grp = BioFactoryFloor.GrpFactory()
        self.final_grp = BioFactoryFloor.GrpFactory()
        self.evnt = BioFactoryFloor.EvntFactory()
        self.tank = BioFactoryFloor.TankFactory()
        self.tank.facic_id = self.evnt.facic_id
        self.tank.save()
        self.move_date = utils.naive_to_aware(datetime.now().date())
        self.final_tank = BioFactoryFloor.TankFactory()
        self.final_tank.facic_id = self.evnt.facic_id
        self.final_tank.save()
        self.cleaned_data = {
            "facic_id": self.evnt.facic_id,
            "evnt_id": self.evnt,
            "created_by": self.evnt.created_by,
            "created_date": self.evnt.created_date,
        }

    def test_whole_grp(self):
        # Move whole group, record count:
        cnt_val = randint(0, 100)
        utils.enter_move_cnts(self.cleaned_data, self.tank, self.final_tank, self.move_date, nfish=cnt_val,
                              start_grp_id=self.grp, whole_grp=True)
        self.assertEqual(self.grp.count_fish_in_group(), cnt_val)

    def test_partial_grp(self):
        # Move partial group, record counts:
        cnt_val = randint(0, 100)
        start_cnt, end_cnt, data_entered = utils.enter_move_cnts(self.cleaned_data, self.tank, self.final_tank, self.move_date, nfish=cnt_val,
                                                                 start_grp_id=self.grp, whole_grp=False)
        end_grp = end_cnt.anix_id.grp_id
        self.assertEqual(self.grp.count_fish_in_group(), -cnt_val)  # fish taken out of this group
        self.assertEqual(end_grp.count_fish_in_group(), cnt_val)

    def test_whole_grp_with_end_grp(self):
        # Move whole group into new end group. record counts, make sure original group is invalid:
        cnt_val = randint(0, 100)
        utils.enter_move_cnts(self.cleaned_data, self.tank, self.final_tank, self.move_date, nfish=cnt_val,
                              start_grp_id=self.grp, end_grp_id=self.final_grp, whole_grp=True)
        self.assertEqual(self.grp.grp_valid, False)
        self.assertEqual(self.final_grp.count_fish_in_group(), cnt_val)

    def test_partial_grp_with_end_grp(self):
        # Move partial group into new group, record counts:
        cnt_val = randint(0, 100)
        utils.enter_move_cnts(self.cleaned_data, self.tank, self.final_tank, self.move_date, nfish=cnt_val,
                              start_grp_id=self.grp, end_grp_id=self.final_grp, whole_grp=False)
        self.assertEqual(self.grp.count_fish_in_group(), -cnt_val)  # fish taken out of this group
        self.assertEqual(self.final_grp.count_fish_in_group(), cnt_val)


@tag("Grp", "Cnt", "Utils")
class TestGrpCnt(TransactionTestCase):
    fixtures = ["initial_data.json"]

    def setUp(self):
        super().setUp()  # used to import fixtures

        # create group, put them in a tank:
        self.grp = BioFactoryFloor.GrpFactory()
        self.evnt = BioFactoryFloor.EvntFactory()
        self.tank = BioFactoryFloor.TankFactory()
        self.tank.facic_id = self.evnt.facic_id
        self.tank.save()
        self.final_tank = BioFactoryFloor.TankFactory()
        self.final_tank.facic_id = self.evnt.facic_id
        self.final_tank.save()
        self.cleaned_data = {
            "facic_id": self.evnt.facic_id,
            "evnt_id": self.evnt,
            "created_by": self.evnt.created_by,
            "created_date": self.evnt.created_date,
        }
        self.anix, self.contx, data_entered = utils.enter_contx(self.tank, self.cleaned_data, grp_pk=self.grp.pk,
                                                                final_flag=True, return_anix=True)

    def test_zero_cnt(self):
        # test that with no details present, count returns zero
        self.assertEqual(self.grp.count_fish_in_group(), 0)

    def test_simple_cnt(self):
        # test groups record a single count correctly
        cnt_val = randint(0, 100)
        utils.enter_cnt(self.cleaned_data, cnt_val, self.evnt.start_date, anix_pk=self.anix.pk, cnt_code="Fish in Container")
        self.assertEqual(self.grp.count_fish_in_group(), cnt_val)

    def test_two_cnts_one_grp(self):
        # add two counts in different containers and make sure group record proper count
        cnt_val = randint(0, 100)
        utils.enter_cnt(self.cleaned_data, cnt_val, self.evnt.start_date, self.anix.pk, cnt_code="Fish in Container")
        # sometimes factories will reuse an event/tank which will prevent new contx's and cnt's from being entered.
        # this loop ensures that new data does get added
        data_entered = False
        while not data_entered:
            anix, contx, data_entered = utils.enter_contx(self.final_tank, self.cleaned_data, grp_pk=self.grp.pk, final_flag=True, return_anix=True)

        utils.enter_cnt(self.cleaned_data, cnt_val, self.evnt.start_date, anix.pk, cnt_code="Fish in Container")
        self.assertEqual(self.grp.count_fish_in_group(), 2 * cnt_val)

    def test_program_grp_cnt(self):
        #  take two types of eggs from group in same event.
        init_cnt = randint(300, 500)
        cnt_one_val = randint(0, 100)
        cnt_two_val = randint(0, 100)
        utils.enter_cnt(self.cleaned_data, init_cnt, self.evnt.start_date, self.anix.pk, cnt_code="Eggs Added")
        cnt = utils.enter_cnt(self.cleaned_data, 0, self.evnt.start_date, self.anix.pk, cnt_code="Eggs Removed")[0]
        utils.enter_cnt_det(self.cleaned_data, cnt, cnt_one_val, "Program Group Split", "EQU")
        utils.enter_cnt_det(self.cleaned_data, cnt, cnt_two_val, "Program Group Split", "PEQU")
        self.assertEqual(self.grp.count_fish_in_group(), init_cnt - cnt_one_val - cnt_two_val)

    def test_aboslute_cnt(self):
        #  take eggs from a group and then record absolute count the following day.
        init_cnt = randint(300, 500)
        cnt_one_val = randint(5, 100)
        cnt_final_val = randint(0, 5)
        next_day_evnt = BioFactoryFloor.EvntFactory()
        next_day_evnt.facic_id = self.evnt.facic_id
        next_day_evnt.start_datetime = self.evnt.start_datetime + timedelta(days=1)
        next_day_evnt.save()
        new_cleaned_data = self.cleaned_data.copy()
        new_cleaned_data["evnt_id"] = next_day_evnt
        end_anix, end_contx, data_entered = utils.enter_contx(self.tank, new_cleaned_data, final_flag=None,
                                                              grp_pk=self.grp.pk, return_anix=True)

        utils.enter_cnt(self.cleaned_data, init_cnt, self.evnt.start_date, self.anix.pk, cnt_code="Eggs Added")
        cnt = utils.enter_cnt(self.cleaned_data, 0, self.evnt.start_date, self.anix.pk, cnt_code="Eggs Removed")[0]
        utils.enter_cnt_det(self.cleaned_data, cnt, cnt_one_val, "Program Group Split", "EQU")
        utils.enter_cnt(new_cleaned_data, cnt_final_val, next_day_evnt.start_date, end_anix.pk, cnt_code="Egg Count")
        self.assertEqual(self.grp.count_fish_in_group(), cnt_final_val)


@tag("Utils")
class TestCollGetter(TransactionTestCase):
    fixtures = ["initial_data.json"]

    def setUp(self):
        super().setUp()  # used to import fixtures

    def test_ints_found(self):
        coll_id = utils.coll_getter("FP")
        self.assertIsNotNone(coll_id)

    def test_name_found(self):
        coll_id = utils.coll_getter("Fall Parr")
        self.assertIsNotNone(coll_id)

    def test_WP_found(self):
        # WP is redundent case, appears in both Wild Parr and wild pre smolt
        coll_id = utils.coll_getter("WP")
        self.assertEqual(coll_id.name, "Wild Parr (WP)", coll_id.name)
