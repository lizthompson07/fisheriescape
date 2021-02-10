from django.contrib.auth.models import User
from rest_framework import serializers


class CurrentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "username",
            "email"
        ]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "username",
            "full_name"
        ]

    full_name = serializers.SerializerMethodField()

    def get_full_name(self, instance):
        return instance.get_full_name()
