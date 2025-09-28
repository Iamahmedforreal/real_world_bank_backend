from rest_framework import serializers
from .models import Transaction, Account, Customer, Card, Loan
from django.contrib.auth.models import User
from django.db import transaction
from django.contrib.auth import authenticate

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True , min_length=8)
    password_confirm = serializers.CharField(write_only=True )
    phone = serializers.CharField(max_length=15 , unique=True)
    first_name = serializers.CharField(max_length=30 , wite_only=True)
    last_name = serializers.CharField(max_length=30 , write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name' , 'phone']

    def validate(self, data):
       if data['password'] != data['password_confirm']:
              raise serializers.ValidationError("Passwords do not match.")
       return data
    
    def validate_phone(self, value):
        if Customer.objects.filter(phone =value).exists():
            raise serializers.ValidationError("Phone number already in use.")
        return value
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        phone = validated_data.pop('phone')

        with transaction.atomic():
            user = User.objects.create_user(**validated_data)
            Customer.objects.create(user=user, phone_number=phone)

        return user
    
class loginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        password = data.get('password')
        username = data.get('username')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError("Invalid either password or phone number is incrorrect .")
            if not user.is_active:
                raise serializers.ValidationError("User is deactivated.")
            
            data['user'] = user
            return data
        
        else:
            raise serializers.ValidationError("Both username and password are required.")
            
        
        
