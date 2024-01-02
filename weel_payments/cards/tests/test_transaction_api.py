from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ..models import Card, CardControl, Transaction


class TransactionListAPITestCase(APITestCase):
    TRANSACTION_URL = reverse("transactions")

    @classmethod
    def setUpTestData(cls):
        cls.card_data = {
            "number": "5555555555554444",
            "cvc_code": "382",
            "exp_date": "2024-12-25",
            "owner_name": "Chris Brown",
            "balance": 51000.15,
            "active": True,
        }
        cls.card = Card.objects.create(**cls.card_data)

    def create_transaction(self, card_id, amount, merchant, category):
        """
        Helper method to create new transaction
        """
        transaction_data = {
            "card": card_id,
            "amount": amount,
            "merchant": merchant,
            "merchant_category": category,
        }
        return self.client.post(self.TRANSACTION_URL, transaction_data)

    def test_create_transaction_without_controls(self):
        balance = self.card.balance
        amount = 10.33
        response = self.create_transaction(
            self.card.id, amount, "Woolworths", "Grocery"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "APPROVED")

        # Assert updated balance
        new_balance_expected = balance - amount
        new_balance = Card.objects.get(id=self.card.id).balance
        self.assertAlmostEqual(
            new_balance,
            new_balance_expected,
            places=2,
            msg="Balance not updated correctly",
        )

    def test_create_transaction_with_controls(self):
        # TODO: Parameterize test method for better readability
        card_id = self.card.id

        # Add card controls
        card_controls_data = [
            {
                "card": self.card,
                "type": CardControl.MAX_AMOUNT,
                "value": "999.99",
                "active": True,
            },
            {
                "card": self.card,
                "type": CardControl.MIN_AMOUNT,
                "value": "10",
                "active": True,
            },
            {
                "card": self.card,
                "type": CardControl.MERCHANT,
                "value": "Coles",
                "active": True,
            },
            {
                "card": self.card,
                "type": CardControl.CATEGORY,
                "value": "Grocery",
                "active": True,
            },
        ]
        for card_control_data in card_controls_data:
            CardControl.objects.create(**card_control_data)

        # Add an invalid transaction (amount > MAX_AMOUNT allowed)
        response = self.create_transaction(self.card.id, 1000, "Coles", "Grocery")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "DECLINED")

        # Add an invalid transaction (amount < MIN_AMOUNT allowed)
        response = self.create_transaction(self.card.id, 5, "Coles", "Grocery")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "DECLINED")

        # Add an invalid transaction (merchant `Aldi` not allowed)
        response = self.create_transaction(self.card.id, 1000, "Aldi", "Grocery")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "DECLINED")

        # Add an invalid transaction (merchant category `Utilities` not allowed)
        response = self.create_transaction(self.card.id, 1000, "Coles", "Utilities")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "DECLINED")

        # Add a valid transaction that meets ALL card control restrictions
        response = self.create_transaction(self.card.id, 89, "Coles", "Grocery")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "APPROVED")

    def test_create_transaction_with_insufficient_balance(self):
        card_id = self.card.id

        # Add a new transaction
        response = self.create_transaction(
            self.card.id, 100_000, "Woolworths", "Grocery"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "DECLINED")
        self.assertEqual(response.data["reason"], "Insufficient balance")

    def test_list_transactions(self):
        """
        Ensure we can list all existing processed card transactions, both approved and declined
        """
        card_id = self.card.id

        # Add new transactions
        expected_data = [
            {
                "card": self.card.id,
                "amount": 199_500,
                "status": Transaction.DECLINED,
            },
            {
                "card": self.card.id,
                "amount": 699.99,
                "status": Transaction.APPROVED,
            },
        ]
        self.create_transaction(self.card.id, 199_500, "Rolex", "Fashion")
        self.create_transaction(self.card.id, 699.99, "Apple", "Electronics")

        response = self.client.get(self.TRANSACTION_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data), Transaction.objects.count()
        )  # Ensure the count matches

        for response_obj, expected_obj in zip(response.data, expected_data):
            for key in expected_obj:
                self.assertEqual(response_obj[key], expected_obj[key])
