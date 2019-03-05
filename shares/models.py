from django.contrib.auth.models import User as AuthUser
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Server(models.Model):
    # Choices for server_type
    DSM = 1
    UBUNTU = 2
    SERVER_TYPE_CHOICES = (
        (DSM, 'DSM'),
        (UBUNTU, 'Ubuntu'),
    )
    hostname = models.CharField(max_length=200, verbose_name=_("hostname"))
    ip_address = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("IP address"))
    mac_address = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("MAC address"))
    server_type = models.IntegerField(choices=SERVER_TYPE_CHOICES, verbose_name=_("server type"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("notes"))
    color = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("color"))

    def __str__(self):
        return "{} ({})".format(self.hostname, self.get_server_type_display())

    class Meta:
        ordering = ["server_type", "hostname"]

    def get_absolute_url(self):
        return reverse('shares:server_detail', kwargs={'pk': self.id})


class User(models.Model):
    # Choices for server_type
    INITIATED = 1
    ACTIVE = 2
    DELETE = 3
    STATUS_CHOICES = (
        (INITIATED, 'Initiated'),
        (ACTIVE, 'Activated'),
        (DELETE, 'Flagged for deletion'),
    )
    user = models.OneToOneField(AuthUser, on_delete=models.DO_NOTHING, blank=True, null=True)
    username = models.CharField(max_length=200, verbose_name=_("username"))
    password = models.CharField(max_length=200, verbose_name=_("password"))
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name="users")
    notes = models.TextField(blank=True, null=True, verbose_name=_("notes"))
    status = models.IntegerField(default=1, choices=STATUS_CHOICES, verbose_name=_("status"))

    def __str__(self):
        return "{} on {}".format(self.username, self.server.hostname)

    class Meta:
        ordering = ["server", "username"]

    def get_absolute_url(self):
        return reverse('shares:user_detail', kwargs={'pk': self.id})


class Share(models.Model):
    name = models.CharField(max_length=200, verbose_name=_("name"))
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name="shares")
    local_path = models.CharField(max_length=200, blank=True, null=True, verbose_name=_("local path"))
    mounted_path = models.CharField(max_length=200, blank=True, null=True, verbose_name=_("mounted path"))
    network_path = models.CharField(max_length=200, blank=True, null=True, verbose_name=_("network path"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("notes"))
    users = models.ManyToManyField(User, related_name="shares", blank=True)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        ordering = ["server", "name"]

    def get_absolute_url(self):
        return reverse('shares:share_detail', kwargs={'pk': self.id})
