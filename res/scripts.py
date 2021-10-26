from .models import Achievement

def save_achievements():
    for a in Achievement.objects.all():
        a.user = a.application.applicant
        a.save()