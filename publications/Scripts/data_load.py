import csv
from django.db.utils import IntegrityError, DataError
import datetime
from publications import models


def process_lookup(file_name, mod):
    # This method is intended to work with a file that is ONLY themes
    data_file = open(file_name, encoding='utf-8')
    reader = csv.reader(data_file, delimiter=',')

    # skip the header row
    next(reader, None)

    val_list = []
    for line in reader:
        if line and line[0].strip():
            vals = [t.strip().upper() for t in line[0].split(' | ')]
            for val in vals:
                if val and val not in val_list:
                    val_list.append(val)

    for val in val_list:
        try:
            mod(name=val).save()
        except IntegrityError:
            pass
        except DataError:
            print("String too long:\n'" + str(val) + "'\n")

data_theme_file_name = r'E:\Projects\Python\publications-inventory\Themes.csv'
process_lookup(data_theme_file_name, models.Theme)

data_human_file_name = r'E:\Projects\Python\publications-inventory\HumanComponents.csv'
process_lookup(data_human_file_name, models.HumanComponents)

data_linkage_file_name = r'E:\Projects\Python\publications-inventory\Linkage.csv'
process_lookup(data_linkage_file_name, models.EcosystemComponents)

data_ecosystem_file_name = r'E:\Projects\Python\publications-inventory\Ecosystem.csv'
process_lookup(data_ecosystem_file_name, models.ProgramLinkage)

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
# 7 Sites
# 8 Publications
for line in tp_reader:

    project_title = line[0].replace("\"", "")

    description = line[1].replace("\"", "").replace('\\n', '\n')

    year = line[2]
    if '-' in year:
        year = year.split('-')[1]

    themes = [t.strip().upper() for t in line[3].split(' | ')]

    humans = [h.strip().upper() for h in line[4].split(' | ')]

    linkages = [l.strip().upper() for l in line[5].split(' | ')]

    ecosystems = [e.strip().upper() for e in line[6].split(' | ')]

    sites = [s.strip() for s in line[7].split(' | ')]

    publications = [p.strip() for p in line[8].split(' | ')]

    try:
        project = models.Project.objects.get(title=project_title)
    except models.Project.MultipleObjectsReturned:
        print("found multiple projects matching:\n\n'" + project_title + "'\n\n")
        exit()
    except models.Project.DoesNotExist:
        print("Creating new publication: " + project_title)
        project = models.Project(title=project_title, abstract=description)
        project.save()

    dirty = False
    for t in themes:
        if not t:
            # skip any blank lines
            continue

        theme = models.Theme.objects.get(name__exact=t)
        try:
            project.theme.get(id=theme.id)
        except models.Theme.DoesNotExist:
            project.theme.add(theme)
            dirty = True

    for h in humans:
        if not h:
            continue

        human = models.HumanComponents.objects.get(name__exact=h)
        try:
            project.human_component.get(id=human.id)
        except models.HumanComponents.DoesNotExist:
            project.human_component.add(human)
            dirty = True

    for l in linkages:
        if not l:
            continue

        link = models.ProgramLinkage.objects.get(name__exact=l)
        try:
            project.program_linkage.get(id=link.id)
        except models.ProgramLinkage.DoesNotExist:
            project.program_linkage.add(link)
            dirty = True

    for e in ecosystems:
        if not e:
            continue

        try:
            ecosystem = models.EcosystemComponents.objects.get(name__exact=e)
        except models.EcosystemComponents.DoesNotExist:
            print("Ecosystem does not exist: '" + str(e) + "'")

        try:
            project.ecosystem_component.get(id=ecosystem.id)
        except models.EcosystemComponents.DoesNotExist:
            project.ecosystem_component.add(ecosystem)
            dirty = True

    if dirty:
        project.save()
        dirty = False

    if project:
        print("Adding sites to project: " + str(project))
        for s in sites:
            try:
                site = models.Site(project=project, value=s)
                site.save()
            except DataError:
                print("Error adding publication: " )
                print(s)

        for p in publications:
            try:
                publication = models.Publication(project=project, value=p)
                publication.save()
            except DataError:
                print("Error adding publication: " )
                print(p)
