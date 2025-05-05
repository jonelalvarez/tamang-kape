from rest_framework import serializers
from .models import CaffeineIntake, HealthTip, CaffeineProduct
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

def perform_create(self, serializer):
    serializer.save()  # <- this must be present

# ✅ Serializer for HealthTips
class HealthTipSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthTip
        fields = '__all__'

# ✅ Serializer for Caffeine Intake
class CaffeineIntakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaffeineIntake
        fields = '__all__'  # or explicitly add 'is_created' if using a custom list

# ✅ Serializer for User Registration (no email, added first_name & last_name)
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        user.is_active = validated_data.get('is_active', True)
        user.save()
        return user

# ✅ Login Serializer
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError("Invalid credentials.")

        if not user.is_active:
            raise serializers.ValidationError("This account is inactive. Please contact support.")

        data['user'] = user
        return data

# ✅ User Serializer (includes profile data and now first/last name)
class UserSerializer(serializers.ModelSerializer):
    weight = serializers.FloatField(source='userprofile.weight', read_only=True)
    bDate = serializers.DateField(source='userprofile.bDate', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined', 'weight', 'bDate', 'health_condition']

# ✅ Caffeine Product Serializer
class CaffeineProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaffeineProduct
        fields = ['id', 'drinkName', 'volumeML', 'calorie', 'caffeine', 'category', 'type', 'status']
