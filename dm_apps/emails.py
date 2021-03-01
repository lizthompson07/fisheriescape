from django.template import loader
from django.utils.translation import gettext as _

from dm_apps.context_processor import my_envr
from lib.functions.custom_functions import listrify

class Email:
    def __init__(self, request, email_template_path, from_address, to_list, subject_en, subject_fr=None, message_en=None, message_fr=None):
        self.request = request
        self.from_address = from_address
        self.to_list = to_list
        self.subject_en = subject_en
        self.subject_fr = subject_fr
        self.message_en = message_en
        self.message_fr = message_fr
        self.email_template_path = email_template_path

    def __str__(self):
        return f"FROM: {self.from_address}\nTO: {self.to_list}\nSUBJECT: {self.get_subject}\nMESSAGE:{self.get_message()}"

    def as_table(self):
        return f'<table class="table table-sm table-bordered">' \
               f'<tr><th>{_("From")}</th><td>{self.from_address}</td></tr>' \
               f'<tr><th>{_("To")}</th><td>{listrify(self.to_list)}</td></tr>' \
               f'<tr><th>{_("Subject")}</th><td>{self.get_subject}</td></tr>' \
               f'<tr><th>{_("Message Body")}</th><td>{self.get_message()}</td></tr></table>'

    def to_dict(self):
        return {
            "from": self.from_address,
            "to": listrify(self.to_list),
            "subject": self.get_subject,
            "message": self.get_html_message()
        }

    def get_html_message(self):
        t = loader.get_template(self.email_template_path)
        context = self.get_context_data()
        rendered = t.render(context)
        return rendered

    def get_text_message(self):
        if self.message_en or self.message_fr:
            if self.message_en and self.message_fr:
                msg = f"*** un message français suivra \n\n\n{self.message_en} \n\n ******************************************************************** \n\n {self.message_fr}"
            elif self.message_en:
                msg = self.message_en
            else:
                msg = self.message_fr
            return msg

    def get_message(self):
        text_msg = self.get_text_message()
        html_msg = self.get_html_message()
        if self.get_text_message():
            return

    def get_subject(self):
        pass

    def get_context_data(self):
        context = dict()
        context.update(my_envr(self.request))
        return context
