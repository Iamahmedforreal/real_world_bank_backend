from rest_framework import serializers
from .models import Transaction, Account, Customer, Card, Loan
from django.contrib.auth.models import User
from django.db import transaction
from django.contrib.auth import authenticate

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True , min_length=8)
    password_confirm = serializers.CharField(write_only=True )
    phone_number = serializers.CharField(max_length=15  ,  required=True )
    first_name = serializers.CharField(max_length=30 , write_only=True)
    last_name = serializers.CharField(max_length=30 , write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name' , 'phone_number']

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
        phone = validated_data.pop('phone_number')

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
        

class transctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields  = ['from_account', 'to_account', 'transaction_type', 'status']
        read_only_fields = ['status']

    def validate(self, data):
        from_account = data.get('from_account')
        to_account = data.get('to_account')
        amount = data.get('amount')

        if amount <= 0:
            raise serializers.ValidationError("Amount must be positive.")

        if from_account:
            """check if from_account is active"""
            if from_account.status != 'active':
                raise serializers.ValidationError("From account is not active.")
            
            """check if user who sending money is the owner of the account"""
            user = self.context['request'].user
            if from_account.customer.user != user:
                raise serializers.ValidationError("You do not own this account the from account.")
            
        if not to_account:
            raise serializers.ValidationError("To account must be specified.")

       
        
        return data
    
    def create(self, validated_data):
        from_account = validated_data.get('from_account')
        to_account = validated_data.get('to_account')
        amount = validated_data.get('amount')  

        with transaction.atomic():
            account = {}
            if from_account:
                account['from_account'] = Account.objects.select_for_update().get(id=from_account.id)
            if to_account:
                account['to_account'] = Account.objects.select_for_update().get(id=to_account.id)

            if from_account:
                if account['from_account'].balance < amount:
                    raise serializers.ValidationError("Insufficient funds in the from account.")
                user = self.context['request'].user
                if account['from_account'].customer.user != user:
                    raise serializers.ValidationError("You do not own the from account.")
                account['from_account'].balance -= amount
                account['from_account'].save()
            if to_account:
                account['to_account'].balance += amount
                account['to_account'].save()
            
            validated_data['status'] = (
                "transfer" if from_account and to_account else
                "deposit" if to_account else
                "withdrawal"
            )
                
            transaction_instance = Transaction.objects.create(**validated_data , satatus = "completed")
            return transaction_instance
                
            
        
   