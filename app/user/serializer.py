from rest_framework import serializers
from . import services
from . import models


class CustomUserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)
    is_verified = serializers.BooleanField(read_only=True)

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
            # Распаковываем данные в service dataclass
        return services.UserDataClass(**data)


class VerifyAccountSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()

class CustomUserPutSerializer(serializers.ModelSerializer): # new serializer class
    class Meta:
        model = models.CustomUser
        fields = ['first_name', 'last_name']

class CustomUserLoginSerializer(serializers.ModelSerializer): # new serializer class
    class Meta:
        model = models.CustomUser
        fields = ['email', 'password']