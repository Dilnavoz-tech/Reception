from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken

from .models import User, BlacklistedAccessToken
from .utils import is_valid_tokens


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'role']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        user = User.objects.create(**validated_data)
        return user



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'role',  'created_at']


class ChangePasswordSerializer(serializers.Serializer):
    model = User
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class ChangeUserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'role']
        extra_kwargs = {
            'username': {'required': False},
            'role': {'required': False},
        }



class ChangeUserPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)




class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(required=True)
    access_token = serializers.CharField(required=True)

    def validate(self, data):
        refresh_token = data.get('refresh_token')
        access_token = data.get('access_token')
        if not is_valid_tokens(refresh_token, access_token):
            raise serializers.ValidationError('Access token or Refresh token is invalid or expired')
        refresh_blacklisted = BlacklistedToken.objects.filter(token__token=refresh_token).exists()
        access_blacklisted = BlacklistedAccessToken.objects.filter(token=access_token).exists()

        if refresh_blacklisted or access_blacklisted:
            raise serializers.ValidationError('Tokens are already in blacklist', code=400)
        return data




class SelfChangeUserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role']
        extra_kwargs = {
            'username': {'read_only': True},
            'role': {'read_only': True},  # Username va role ni o'zgartirib bo'lmaydi
        }
