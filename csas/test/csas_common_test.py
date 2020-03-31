from django.contrib.auth.models import User, Group

EXPECTED_NAV = 'csas/csas_nav.html'
EXPECTED_CSS = 'csas/csas_css.css'

TEST_PASSWORD = 'test1234'


# use when a user needs to be logged in.
def login_csas_user(test_case):
    user_name = "Csas"
    if User.objects.filter(username=user_name):
        user = User.objects.get(username=user_name)
    else:
        csas_group = Group(name="csas_admin")
        csas_group.save()

        user = User.objects.create_user(username=user_name, first_name="Hump", last_name="Back",
                                        email="Hump.Back@dfo-mpo.gc.ca", password=TEST_PASSWORD)
        user.groups.add(csas_group)
        user.save()

    test_case.client.login(username=user.username, password=TEST_PASSWORD)

    return user


# This is used to simulate calling the as_veiw() function normally called in the urls.py
# this will return a view that can then have it's internal methods tested
def setup_view(view, request, *args, **kwargs):

    view.request = request
    view.args = args
    view.kwargs = kwargs
    return view