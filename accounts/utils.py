from django.conf import settings
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_text, force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext as _

from accounts.tokens import account_activation_token
from dm_apps.utils import custom_send_mail


def send_activation_email(user, request):
    current_site = get_current_site(request)
    mail_subject = 'Activate your DM Apps account / Activez votre compte Applications GD'
    message = render_to_string('registration/acc_active_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': force_text(urlsafe_base64_encode(force_bytes(user.pk))),
        'token': account_activation_token.make_token(user),
    })
    to_email = user.email
    from_email = settings.SITE_FROM_EMAIL
    custom_send_mail(
        html_message=message,
        subject=mail_subject,
        recipient_list=[to_email, ],
        from_email=from_email,
        user=user,
    )
    messages.success(request, _('A verification email was just send to {email_address}. In order to complete your registration, please follow the link'
                                ' in the message. <br><br>If the email does not appear within 1-2 minutes, please be sure to check your junk mail folder. '
                                '<br><br>The activation link will only remain valid for a limited period of time.').format(email_address=to_email))