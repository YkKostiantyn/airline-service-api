from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'role' ,'role_display']
        read_only_fields = ['id']

class CreateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'password','first_name', 'last_name', 'email', 'role']
        read_only_fields = ['id']
        extra_kwargs = {
            'password': {"write_only": True},
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def validate_username(self, validate_data):
        if not validate_data or not validate_data.strip():
            raise serializers.ValidationError('Username should not be empty')