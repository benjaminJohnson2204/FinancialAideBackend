from abc import ABC

from rest_framework import serializers

from users.models import *


class RegisterRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields =[
            'username',
            'email',
            'password',
        ]

    def create(self, validated_data):
        # Have to use "create_user" to hash password instead of using raw password
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )


class LoginRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username',
            'password'
        ]


class ResetPasswordRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'email',
        ]


class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'id',
        ]

