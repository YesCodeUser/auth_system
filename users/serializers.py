from rest_framework import serializers
from .models import User, Role, UserRole


class UserRegisterSerializer(serializers.ModelSerializer):
    password_repeat = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'password_repeat', 'first_name', 'last_name', 'surname']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_repeat']:
            raise serializers.ValidationError("Passwords are different")
        del attrs['password_repeat']
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        default_role = Role.objects.get(name='user')
        UserRole.objects.create(user=user, role=default_role)
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'surname', 'is_deleted', 'created_at', 'updated_at']


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'surname']

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.surname = validated_data.get('surname', instance.surname)
        instance.save()
        return instance
