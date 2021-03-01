from django.template import loader
from django.utils.translation import gettext as _, get_language, activate
from html2text import html2text

from dm_apps.context_processor import my_envr
from dm_apps.utils import custom_send_mail
from lib.functions.custom_functions import listrify


class Email:
    def __init__(self, request, email_template_path, from_email, recipient_list, subject_en, subject_fr=None, message_en=None, message_fr=None):
        self.request = request
        self.from_email = from_email
        self.recipient_list = recipient_list
        self.subject_en = subject_en
        self.subject_fr = subject_fr
        self.message_en = message_en
        self.message_fr = message_fr
        self.email_template_path = email_template_path

    def __str__(self):
        return f"FROM: {self.from_email}\n" \
               f"TO: {self.recipient_list}\n" \
               f"SUBJECT: {self.get_subject}\n" \
               f"HTML MESSAGE:{html2text(self.get_html_message())}\n" \
               f"MESSAGE:{self.get_text_message()}"

    def as_table(self):
        return f'<table class="table table-sm table-bordered">' \
               f'<tr><th>{_("From")}</th><td>{self.from_email}</td></tr>' \
               f'<tr><th>{_("To")}</th><td>{listrify(self.recipient_list)}</td></tr>' \
               f'<tr><th>{_("Subject")}</th><td>{self.get_subject}</td></tr>' \
               f'<tr><th>{_("Message Body")}</th><td>{self.get_message()}</td></tr></table>'

    def to_dict(self):
        return {
            "from": self.from_email,
            "to": listrify(self.recipient_list),
            "subject": self.get_subject,
            "message": self.get_message()
        }

    def get_html_message(self):
        t = loader.get_template(self.email_template_path)
        context = self.get_context_data()
        rendered = t.render(context)
        return rendered

    def get_text_message(self):
        if self.message_en or self.message_fr:
            if self.message_en and self.message_fr:
                msg = f"*** un message français suivra \n\n\n{self.message_en} " \
                      f"\n\n ******************************************************************** \n\n {self.message_fr}"
            elif self.message_en:
                msg = self.message_en
            else:
                msg = self.message_fr
            return msg

    def get_message(self):
        """ use this if you only want one message. It will help you decide which one has content """
        text_msg = self.get_text_message()
        html_msg = self.get_html_message()
        # basically, if there is a text message, send in that.
        if text_msg:
            return text_msg
        return html_msg

    def get_subject(self):
        lang = get_language()
        subject = str()
        if self.subject_en:
            activate('en')
            subject += self.subject_en
        if self.subject_fr:
            if len(subject) > 0:
                subject += " / "
            activate('fr')
            subject += self.subject_fr
        activate(lang)
        return subject

    def get_context_data(self):
        context = dict()
        context.update(my_envr(self.request))
        return context

    def send(self):
        custom_send_mail(
            subject=self.get_subject(),
            html_message=self.get_html_message(),
            text_message=self.get_text_message(),
            from_email=self.from_email,
            recipient_list=self.recipient_list
        )
