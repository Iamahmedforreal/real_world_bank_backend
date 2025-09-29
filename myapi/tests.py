

# Create your tests here.
from django.test import TestCase
from django.contrib.auth.models import User
from .serializers import RegisterSerializer, TransctionSerializer
from .models import Customer, Account, Transaction


class RegisterSerializerTest(TestCase):
    def test_valid_registration(self):
        data = {
            "username": "michael",
            "email": "michael@example.com",
            "password": "StrongPass123",
            "password_confirm": "StrongPass123",
            "first_name": "Michael",
            "last_name": "Jordan",
            "phone_number": "+252612345678"
        }

        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        user = serializer.save()
        self.assertEqual(user.username, "michael")
        self.assertTrue(User.objects.filter(username="michael").exists())
        self.assertTrue(Customer.objects.filter(user=user).exists())

    def test_password_mismatch(self):
        data = {
            "username": "wrongpass",
            "email": "wrong@example.com",
            "password": "StrongPass123",
            "password_confirm": "DifferentPass",
            "first_name": "Wrong",
            "last_name": "Test",
            "phone_number": "+252611111111"
        }

        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("Passwords do not match.", str(serializer.errors))


class TransactionSerializerTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="sender", password="StrongPass123")
        self.user2 = User.objects.create_user(username="receiver", password="StrongPass123")

        self.customer1 = Customer.objects.create(user=self.user1, phone_number="+252600000001")
        self.customer2 = Customer.objects.create(user=self.user2, phone_number="+252600000002")

        self.account1 = Account.objects.create(customer=self.customer1, account_number="111", balance=500)
        self.account2 = Account.objects.create(customer=self.customer2, account_number="222", balance=100)

    def test_valid_transaction(self):
        data = {
            "from_account": self.account1.id,
            "to_account": self.account2.id,
            "amount": 100,
            "transaction_type": "transfer"
        }

        serializer = TransctionSerializer(data=data, context={"request": type("Request", (), {"user": self.user1})()})
        self.assertTrue(serializer.is_valid(), serializer.errors)

        transaction = serializer.save()
        self.assertEqual(transaction.amount, 100)
        self.account1.refresh_from_db()
        self.account2.refresh_from_db()
        self.assertEqual(self.account1.balance, 400)
        self.assertEqual(self.account2.balance, 200)

    def test_insufficient_funds(self):
        data = {
            "from_account": self.account1.id,
            "to_account": self.account2.id,
            "amount": 1000,
            "transaction_type": "transfer"
        }

        serializer = TransctionSerializer(data=data, context={"request": type("Request", (), {"user": self.user1})()})
        self.assertFalse(serializer.is_valid())
        self.assertIn("Insufficient funds", str(serializer.errors))
