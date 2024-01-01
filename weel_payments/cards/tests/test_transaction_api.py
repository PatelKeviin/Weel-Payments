from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ..models import Card, CardControl, Transaction


class TransactionListAPITestCase(APITestCase):
    def test_create_transaction_without_controls(self):
        # Add a new card
        card_data = {
            "number": "5555555555554444",
            "cvc_code": "382",
            "exp_date": "2024-12-25",
            "owner_name": "Chris Brown",
            "balance": 510.15,
            "active": True,
        }
        card = Card.objects.create(**card_data)
        card_id = card.id

        # Add a new transaction
        url = reverse("transactions")
        transaction_data = {
            "card": card_id,
            "amount": 10.33,
            "merchant": "Woolworths",
            "merchant_category": "Grocery",
        }

        response = self.client.post(url, transaction_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "APPROVED")

        # Assert updated balance
        new_balance_expected = card_data["balance"] - transaction_data["amount"]
        new_balance = Card.objects.get(id=card_id).balance
        self.assertEqual(new_balance, new_balance_expected)

    def test_create_transaction_with_controls(self):
        # Add a new card
        card_data = {
            "number": "5555555555554444",
            "cvc_code": "382",
            "exp_date": "2024-12-25",
            "owner_name": "Chris Brown",
            "balance": 1500.19,
            "active": True,
        }
        card = Card.objects.create(**card_data)
        card_id = card.id

        # Add card controls
        card_controls_data = [
            {
                "card": card,
                "type": CardControl.MAX_AMOUNT,
                "value": "999.99",
                "active": True,
            },
            {
                "card": card,
                "type": CardControl.MIN_AMOUNT,
                "value": "9.99",
                "active": True,
            },
            {
                "card": card,
                "type": CardControl.MERCHANT,
                "value": "Coles",
                "active": True,
            },
            {
                "card": card,
                "type": CardControl.CATEGORY,
                "value": "Grocery",
                "active": True,
            },
        ]
        for card_control_data in card_controls_data:
            CardControl.objects.create(**card_control_data)

        url = reverse("transactions")
        # Add an invalid transaction (amount > MAX_AMOUNT allowed)
        transaction_data = {
            "card": card_id,
            "amount": 1000,
            "merchant": "Coles",
            "merchant_category": "Grocery",
        }
        response = self.client.post(url, transaction_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "DECLINED")

        # Add an invalid transaction (amount < MIN_AMOUNT allowed)
        transaction_data = {
            "card": card_id,
            "amount": 5,
            "merchant": "Coles",
            "merchant_category": "Grocery",
        }
        response = self.client.post(url, transaction_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "DECLINED")

        # Add an invalid transaction (merchant `Aldi` not allowed)
        transaction_data = {
            "card": card_id,
            "amount": 1000,
            "merchant": "Aldi",
            "merchant_category": "Grocery",
        }
        response = self.client.post(url, transaction_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "DECLINED")

        # Add an invalid transaction (merchant category `Utilities` not allowed)
        transaction_data = {
            "card": card_id,
            "amount": 1000,
            "merchant": "Coles",
            "merchant_category": "Utilities",
        }
        response = self.client.post(url, transaction_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "DECLINED")

        # Add a valid transaction that meets ALL card control restrictions
        transaction_data = {
            "card": card_id,
            "amount": 89,
            "merchant": "Coles",
            "merchant_category": "Grocery",
        }
        response = self.client.post(url, transaction_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "APPROVED")

    def test_create_transaction_with_insufficient_balance(self):
        # Add a new card
        card_data = {
            "number": "5555555555554444",
            "cvc_code": "382",
            "exp_date": "2024-12-25",
            "owner_name": "Chris Brown",
            "balance": 15,
            "active": True,
        }
        card = Card.objects.create(**card_data)
        card_id = card.id

        # Process a new transaction
        url = reverse("transactions")
        transaction_data = {
            "card": card_id,
            "amount": 1000,
            "merchant": "Woolworths",
            "merchant_category": "Grocery",
        }

        response = self.client.post(url, transaction_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "DECLINED")
        self.assertEqual(response.data["reason"], "Insufficient balance")
