from django.conf import settings
from django.template import loader

from dm_apps.context_processor import my_envr
from dm_apps.emails import Email


class FeedBackEmail(Email):
    def get_subject_en(self):
        return self.instance.subject

    def get_message_en(self):
        return self.instance.comment

    recipient_list = 'reed.orpen@dfo-mpo.gc.ca'
    #'DFO.PAC.SGCM-MSCS.PAC.MPO@dfo-mpo.gc.ca'