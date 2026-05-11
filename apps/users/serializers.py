from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'role' ,'role_display']
        read_only_fields = ['id','role']

class CreateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'password','first_name', 'last_name', 'email']
        read_only_fields = ['id']
        extra_kwargs = {
            'password': {"write_only": True},
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)