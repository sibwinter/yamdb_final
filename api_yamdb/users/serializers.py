from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from users.validators import SelfValidate

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
        model = User


class RegisterSerializer(serializers.Serializer):
    username_validator = UnicodeUsernameValidator()
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all()),
                    username_validator]
    )
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    def create(self, validated_data):
        user, created = User.objects.get_or_create(**validated_data)
        return user

    class Meta:
        validators = [
            SelfValidate(fields=['username']),

        ]


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)
