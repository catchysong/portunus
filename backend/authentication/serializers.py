from django.contrib.auth import authenticate
from django.utils.translation import gettext as _
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from shared.email import PortunusMailer
from .models import User


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
        )


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "password")
        extra_kwargs = {"password": {"write_only": True}, "email": {"validators": []}}

    def validate(self, data):
        self.user = authenticate(
            request=self.context["request"], email=data["email"], password=data["password"]
        )
        if not self.user:
            raise ValidationError(_("Invalid username or password"))

        return data

    def save(self):
        return self.user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email",)


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email",)

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_unusable_password()
        user.save()
        PortunusMailer.send_account_creation_notice(user)
        return user
