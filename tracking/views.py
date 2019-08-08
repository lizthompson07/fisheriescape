import logging
import os

from datetime import timedelta
from shutil import rmtree

from bokeh import palettes
from bokeh.io import output_file, save
from bokeh.models import Title
from bokeh.plotting import figure
from django import forms
from django.contrib.auth.models import User
from django.db.models import Sum
from django.shortcuts import render
from django.contrib.auth.decorators import permission_required
from django.utils import timezone
from django.utils.timezone import now

from tracking.models import Visitor, Pageview, VisitSummary
from tracking.settings import TRACK_PAGEVIEWS
import numpy as np

log = logging.getLogger(__file__)

# tracking wants to accept more formats than default, here they are
input_formats = [
    '%Y-%m-%d %H:%M:%S',  # '2006-10-25 14:30:59'
    '%Y-%m-%d %H:%M',  # '2006-10-25 14:30'
    '%Y-%m-%d',  # '2006-10-25'
    '%Y-%m',  # '2006-10'
    '%Y',  # '2006'
]


class DashboardForm(forms.Form):
    start = forms.DateTimeField(required=False, input_formats=input_formats)
    end = forms.DateTimeField(required=False, input_formats=input_formats)


@permission_required('tracking.visitor_log')
def dashboard(request):
    "Counts, aggregations and more!"
    end_time = now()
    start_time = end_time - timedelta(days=7)
    defaults = {'start': start_time, 'end': end_time}

    form = DashboardForm(data=request.GET or defaults)
    if form.is_valid():
        start_time = form.cleaned_data['start']
        end_time = form.cleaned_data['end']

    # determine when tracking began
    try:
        obj = Visitor.objects.order_by('start_time')[0]
        track_start_time = obj.start_time
    except (IndexError, Visitor.DoesNotExist):
        track_start_time = now()

    # If the start_date is before tracking began, warn about incomplete data
    warn_incomplete = (start_time < track_start_time)

    # queries take `date` objects (for now)
    user_stats = Visitor.objects.user_stats(start_time, end_time)
    visitor_stats = Visitor.objects.stats(start_time, end_time)
    if TRACK_PAGEVIEWS:
        pageview_stats = Pageview.objects.stats(start_time, end_time)
    else:
        pageview_stats = None

    # get the last 100 page visits
    page_visits = Pageview.objects.all().order_by("-view_time")
    if len(page_visits) > 101:
        page_visits = page_visits[:100]

    context = {
        'form': form,
        'track_start_time': track_start_time,
        'warn_incomplete': warn_incomplete,
        'user_stats': user_stats,
        'visitor_stats': visitor_stats,
        'pageview_stats': pageview_stats,
        'page_visits': page_visits,
    }
    context = summarize_data(context)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(base_dir, 'templates', 'tracking', 'temp')
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if "report_temp" in file:
                my_file = "tracking/temp/{}".format(file)

    context["report_path"] = my_file
    return render(request, 'tracking/dashboard.html', context)


@permission_required('tracking.visitor_log')
def user_history(request, user):
    my_user = User.objects.get(pk=user)

    # get the last 100 page visits
    page_visits = Pageview.objects.filter(visitor__user=my_user).order_by("-view_time")

    context = {
        'my_user': my_user,
        'page_visits': page_visits,
    }
    context = summarize_data(context, my_user)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(base_dir, 'templates', 'tracking', 'temp')
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if "report_temp" in file:
                my_file = "tracking/temp/{}".format(file)

    context["report_path"] = my_file

    return render(request, 'tracking/user_history.html', context)


def summarize_data(context, user=None):
    # prelim...

    # capture all lines of page view table in 2 summary tables
    for view in Pageview.objects.filter(summarized=False):
        # what app were they using?
        url_list = view.url.split("/")
        app_name = url_list[2] if len(url_list) > 2 else None

        # who is the user?
        my_user = view.visitor.user

        if my_user and app_name and app_name not in ["", "accounts", "login_required", "denied", "reset", "password-reset", "auth", "login",
                                                     "setlang", "shared", "tracking"]:
            # what is the date?
            my_date = timezone.datetime(view.view_time.year, view.view_time.month, view.view_time.day)

            # add view to visitSummary table
            # print(app_name)
            visit_summary_obj, created = VisitSummary.objects.get_or_create(
                date=my_date,
                application_name=app_name,
                user=my_user,
            )

            visit_summary_obj.page_visits += 1
            visit_summary_obj.save()

        # mark the view as summarized.
        view.summarized = True
        view.save()

    # get the list of apps
    if not user:
        app_list = [visit["application_name"] for visit in
                    VisitSummary.objects.all().values("application_name").order_by("application_name").distinct()]
    else:
        app_list = [visit["application_name"] for visit in
                    VisitSummary.objects.filter(user=user).values("application_name").order_by("application_name").distinct()]

    app_dict = {}
    final_app_dict = {}
    for app in app_list:
        # create a new file containing data
        if not user:
            result = VisitSummary.objects.filter(application_name=app).values('application_name').order_by(
                "application_name").distinct().annotate(dsum=Sum('page_visits'))
        else:
            result = VisitSummary.objects.filter(application_name=app, user=user).values('application_name').order_by(
                "application_name").distinct().annotate(dsum=Sum('page_visits'))
        app_dict[app] = result[0]["dsum"]
    for key, value in sorted(app_dict.items(), key=lambda item: item[1], reverse=True):
        final_app_dict[key] = value
    context["app_dict"] = final_app_dict

    # now for today
    app_dict = {}
    final_app_dict = {}
    for app in app_list:
        # create a new file containing data
        if not user:
            result = VisitSummary.objects.filter(application_name=app, date__year=timezone.now().year, date__month=timezone.now().month,
                                                 date__day=timezone.now().day).values('page_visits').order_by(
                "page_visits").aggregate(dsum=Sum('page_visits'))
        else:
            result = VisitSummary.objects.filter(application_name=app, user=user, date__year=timezone.now().year,
                                                 date__month=timezone.now().month,
                                                 date__day=timezone.now().day).values('page_visits').order_by(
                "page_visits").aggregate(dsum=Sum('page_visits'))

        if result["dsum"]:
            app_dict[app] = result["dsum"]

    for key, value in sorted(app_dict.items(), key=lambda item: item[1], reverse=True):
        final_app_dict[key] = value
    context["app_dict_today"] = final_app_dict

    if not user:
        # get the list of users
        user_list = [visit["user"] for visit in
                     VisitSummary.objects.all().values("user").order_by("user").distinct()]
        user_dict = {}
        final_user_dict = {}
        for my_user in user_list:
            # create a new file containing data
            result = VisitSummary.objects.filter(user=my_user).values('user').order_by(
                "user").distinct().annotate(dsum=Sum('page_visits'))
            user_dict[User.objects.get(pk=my_user)] = result[0]["dsum"]

        for key, value in sorted(user_dict.items(), key=lambda item: item[1], reverse=True):
            final_user_dict[key] = value

        context["user_dict"] = final_user_dict

        # get the list of users for TODAY
        user_list = [visit["user"] for visit in
                     VisitSummary.objects.all().values("user").order_by("user").distinct()]
        user_dict = {}
        final_user_dict = {}
        for my_user in user_list:
            # create a new file containing data
            result = VisitSummary.objects.filter(user=my_user, date__year=timezone.now().year, date__month=timezone.now().month,
                                                 date__day=timezone.now().day).values('page_visits').order_by(
                "page_visits").distinct().aggregate(dsum=Sum('page_visits'))
            if result["dsum"]:
                user_dict[User.objects.get(pk=my_user)] = result["dsum"]

        for key, value in sorted(user_dict.items(), key=lambda item: item[1], reverse=True):
            final_user_dict[key] = value

        context["user_dict_today"] = final_user_dict

    generate_page_visit_report(app_list, user=user)

    # delete any records older then three days
    Pageview.objects.filter(summarized=True).filter(view_time__lte=timezone.now() - timezone.timedelta(days=3)).delete()
    return context


def generate_page_visit_report(app_list, user=None):
    # start assigning files and by cleaning the temp dir
    base_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(base_dir, 'templates', 'tracking', 'temp')
    target_file = os.path.join(target_dir, 'report_temp_{}.html'.format(timezone.now().strftime("%H%M%S")))
    # target_file = os.path.join(target_dir, 'report_temp.html')

    try:
        rmtree(target_dir)
    except:
        print("no such dir.")
    os.mkdir(target_dir)

    # output to static HTML file
    output_file(target_file)

    p = figure(
        tools="pan,box_zoom,wheel_zoom,reset,save",
        x_axis_label='Date',
        y_axis_label='Pageviews',
        plot_width=800, plot_height=800,
        x_axis_type="datetime",
    )

    # p.add_layout(Title(text=title_eng, text_font_size="16pt"), 'above')

    # generate color palette
    if len(app_list) <= 2:
        colors = palettes.Set1[3][:len(app_list)]
    elif len(app_list) <= 9:
        colors = palettes.Set1[len(app_list)]
    elif len(app_list) <= 20:
        colors = palettes.Category20[len(app_list)]
    else:
        colors = palettes.viridis(len(app_list))

    # get a list of days
    if not user:
        date_list = [date["date"] for date in VisitSummary.objects.all().values("date").order_by("date").distinct()]
    else:
        date_list = [date["date"] for date in VisitSummary.objects.filter(user=user).values("date").order_by("date").distinct()]
    # prime counter variable
    i = 0
    for app in app_list:
        # create a new file containing data
        if not user:
            qs = VisitSummary.objects.filter(application_name=app).values('date').order_by("date").distinct().annotate(
                dsum=Sum('page_visits'))
        else:
            qs = VisitSummary.objects.filter(application_name=app, user=user).values('date').order_by("date").distinct().annotate(
                dsum=Sum('page_visits'))
        dates = [i["date"] for i in qs]
        counts = [i["dsum"] for i in qs]
        legend_title = "{}".format(app)
        p.line(dates, counts, legend=legend_title, line_color=colors[i], line_width=1)
        p.circle(dates, counts, legend=legend_title, fill_color=colors[i], line_color=colors[i], size=3)
        i += 1

    total_count = []
    for date in date_list:
        # create a new file containing data
        if not user:
            result = VisitSummary.objects.filter(date=date).values('date').order_by("date").distinct().annotate(dsum=Sum('page_visits'))
        else:
            result = VisitSummary.objects.filter(date=date, user=user).values('date').order_by("date").distinct().annotate(
                dsum=Sum('page_visits'))
        total_count.append(result[0]["dsum"])

    p.line(date_list, total_count, legend="total", line_color='black', line_width=3)
    p.circle(date_list, total_count, legend="total", fill_color='black', line_color="black", size=5)
    p.legend.location = "top_left"
    save(p)
