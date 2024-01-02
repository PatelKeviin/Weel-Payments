from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ..models import Card
from ..serializers import CardSerializer


class CardListAPITestCase(APITestCase):
    CARD_URL = reverse("cards")

    @classmethod
    def setUpTestData(cls):
        cls.valid_card_data = {
            "number": "5555555555554444",
            "cvc_code": "382",
            "exp_date": "2024-12-25",
            "owner_name": "Chris Brown",
            "balance": 510.15,
            "active": True,
        }

    def create_card(self, data):
        return self.client.post(self.CARD_URL, data)

    def test_create_card(self):
        """
        Ensure we can create a new card
        """
        response = self.create_card(self.valid_card_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Card.objects.count(), 1)

        for key in self.valid_card_data:
            self.assertEqual(response.data[key], self.valid_card_data[key])

    def test_create_card_with_invalid_date(self):
        invalid_data = self.valid_card_data.copy()
        invalid_data["exp_date"] = "01/31/2023"  # Invalid date format

        response = self.create_card(invalid_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_card_without_number(self):
        incomplete_data = self.valid_card_data.copy()
        incomplete_data.pop("number")  # Remove required 'number' field

        response = self.create_card(incomplete_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_cards(self):
        """
        Ensure we can list all existing cards
        """
        expected_data = [
            {
                "number": "5555555555554444",
                "cvc_code": "123",
                "exp_date": "2024-03-12",
                "owner_name": "Kevin Patel",
                "balance": 500,
                "active": False,
            },
            {
                "number": "2211555555554444",
                "cvc_code": "777",
                "exp_date": "2024-10-29",
                "owner_name": "Steve Smith",
                "balance": 100.99,
                "active": True,
            },
        ]
        for card_data in expected_data:
            Card.objects.create(**card_data)

        response = self.client.get(self.CARD_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data), len(expected_data)
        )  # Ensure the count matches

        for response_obj, expected_obj in zip(response.data, expected_data):
            for key in expected_obj:
                self.assertEqual(response_obj[key], expected_obj[key])
