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
        if Customer.objects.filter(phone_number =value).exists():
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
        
from django.db import transaction
from rest_framework import serializers

# Assuming Account and Transaction models are correctly imported
# from .models import Account, Transaction 
from rest_framework import serializers
from django.db import transaction
# Assuming Account and Transaction models are available in the scope
# from .models import Account, Transaction 

class TransctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields  = ['from_account', 'to_account', 'transaction_type', 'amount', ]
        read_only_fields = ['transaction_type'] # Set type as read-only, calculated in create/save
    
    def validate(self, data):
        from_account_id  = data.get('from_account')
        to_account_id = data.get('to_account')
        amount = data.get('amount')

        if not from_account_id and not to_account_id:
            raise serializers.ValidationError("Either from_account or to_account must be provided.")

        if from_account_id:
            try:
                from_account = Account.objects.get(id=from_account_id)
            except Account.DoesNotExist:
                raise serializers.ValidationError({'from_account': "From account not found."})
            data['from_account'] = from_account
        else:
            from_account = None

        if to_account_id:
            try:
                to_account = Account.objects.get(id=to_account_id)
            except Account.DoesNotExist:
                raise serializers.ValidationError({'to_account': "To account not found."})
            data['to_account'] = to_account
        else:
            to_account = None


        """we checking if the amount is greater than zero"""
        if amount <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
    

        """ We are checking if both accounts are active"""        
        if from_account and from_account.status != 'active':
            raise serializers.ValidationError("From account must be active to perform a transaction.")
        if to_account and to_account.status != 'active':
            raise serializers.ValidationError("To account must be active to perform a transaction.")
      
        """ We are checking if user is trying to send money from his own account"""
        if from_account:
            user = self.context['request'].user
            if from_account.customer.user != user:
                raise serializers.ValidationError("You can only send money from your own account.")
        """"" We are checking if user is trying to send money to his own account"""

        return data
    
    def create(self, validated_data):
      from_account = validated_data.get('from_account')
      to_account = validated_data.get('to_account')
      amount = validated_data.get('amount')

    # Handle transfer
      if from_account and to_account:
        if from_account.balance < amount:
            raise serializers.ValidationError("Insufficient funds.")
        from_account.balance -= amount
        to_account.balance += amount
        from_account.save()
        to_account.save()
        validated_data['transaction_type'] = 'transfer'

    # Handle deposit
      elif to_account:
        to_account.balance += amount
        to_account.save()
        validated_data['transaction_type'] = 'deposit'

    # Handle withdrawal
      elif from_account:
        if from_account.balance < amount:
            raise serializers.ValidationError("Insufficient funds.")
        from_account.balance -= amount
        from_account.save()
        validated_data['transaction_type'] = 'withdrawal'

      return Transaction.objects.create(**validated_data)

            

        