import csv
from django.db.utils import IntegrityError
import datetime
from publications import models


def process_themes(file_name):
    # This method is intended to work with a file that is ONLY themes
    data_file = open(file_name, encoding='utf-8')
    reader = csv.reader(data_file, delimiter=',')

    # skip the header row
    next(reader, None)

    theme_list = []
    for line in reader:
        themes = [t.strip().upper() for t in line[0].split(' | ')]
        for theme in themes:
            if theme not in theme_list:
                theme_list.append(theme)

    for theme in theme_list:
        try:
            models.Theme(name=theme).save()
        except IntegrityError:
            pass

# data_theme_file_name = r'E:\Projects\Python\publications-inventory\Themes.csv'

data_tp_file_name = r'E:\Projects\Python\publications-inventory\pub_data.csv'

tp_reader = csv.reader(open(data_tp_file_name, encoding='utf-8'), delimiter=',')

# skip the header line
next(tp_reader, None)

# 0 Projects
# 1 Description
# 2 Pub year
# 3 Themes
# 4 Human Component
# 5 Linkage to Program
# 6 Ecosystem Component
for line in tp_reader:

    project = line[0].replace("\"", "")

    description = line[1].replace("\"", "").replace('\\n', '\n')

    year = line[2]
    if '-' in year:
        year = year.split('-')[1]

    themes = [t.strip().upper() for t in line[3].split(' | ')]

    try:
        publication = models.Publications.objects.get(pub_title=project)
    except models.Publications.MultipleObjectsReturned:
        print("found multiple projects matching:\n\n'" + project + "'\n\n")
        exit()
    except models.Publications.DoesNotExist:
        print("Creating new publication: " + project)
        publication = models.Publications(pub_title=project,
                                          pub_abstract=description,
                                          pub_year=datetime.date(int(year), 1, 1))
        publication.save()

    dirty = False
    for t in themes:
        theme = models.Theme.objects.get(name__exact=t)
        try:
            publication.theme.get(id=theme.id)
        except models.Theme.DoesNotExist:
            publication.theme.add(theme)
            dirty = True

    if dirty:
        publication.save()
        dirty = False


