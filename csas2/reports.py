import os
from io import BytesIO

from django.utils.translation import activate, deactivate, gettext
from docx import Document
from html2text import html2text
from markdown import markdown
from textile import textile

from dm_apps import settings


def generate_tor(tor, lang):
    # figure out the filename
    target_dir = os.path.join(settings.BASE_DIR, 'media', 'temp')
    target_file = "temp_export.docx"
    target_file_path = os.path.join(target_dir, target_file)
    target_url = os.path.join(settings.MEDIA_ROOT, 'temp', target_file)

    if lang == "fr":
        template_file_path = os.path.join(settings.BASE_DIR, 'csas2', 'static', "csas2", "tor_template_fr.docx")
    else:
        template_file_path = os.path.join(settings.BASE_DIR, 'csas2', 'static', "csas2", "tor_template_en.docx")

    with open(template_file_path, 'rb') as f:
        source_stream = BytesIO(f.read())
    document = Document(source_stream)
    source_stream.close()

    activate(lang)
    dates = location = chair = "no meeting selected in terms of reference".upper()
    if tor.meeting:
        dates = tor.meeting.tor_display_dates
        if tor.meeting.is_virtual:
            location = gettext("Virtual Meeting")
        else:
            location = tor.meeting.location if tor.meeting.location else "TBD"
        chair = tor.meeting.chair if tor.meeting.chair else "TBD"

    field_dict = dict(
        TAG_TITLE=tor.process.tname,
        TAG_TYPE_SCOPE=tor.process.scope_type,
        TAG_LEAD_REGION=tor.process.lead_region.tname,
        TAG_DATES=dates,
        TAG_LOCATION=location,
        TAG_CHAIR=chair,
        TAG_CONTEXT=tor.context_fr if lang == "fr" else tor.context_en,
        TAG_OBJECTIVES=tor.objectives_fr if lang == "fr" else tor.objectives_en,
        TAG_EXPECTED_PUBLICATIONS=tor.expected_publications_fr if lang == "fr" else tor.expected_publications_en,
        TAG_PARTICIPATION=tor.participation_fr if lang == "fr" else tor.participation_en,
        TAG_REFERENCES=tor.references_fr if lang == "fr" else tor.references_en,
    )
    for p in document.paragraphs:
        inline = p.runs
        for i in range(len(inline)):
            text = inline[i].text
            if text in field_dict.keys():
                text = text.replace(text, field_dict[text])
                inline[i].text = text

    document.save(target_file_path)
    deactivate()
    return target_url
