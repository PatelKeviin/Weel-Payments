from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ..models import Card
from ..serializers import CardSerializer


class CardListAPITestCase(APITestCase):
    # def setUp(self):
    #     pass

    def test_create_card(self):
        """
        Ensure we can create a new card
        """
        url = reverse("cards")
        data = {
            "number": "5555555555554444",
            "cvc_code": "382",
            "exp_date": "2024-12-25",
            "owner_name": "Chris Brown",
            "balance": 510.15,
            "active": True,
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Card.objects.count(), 1)

        for key in data:
            self.assertEqual(response.data[key], data[key])

    def test_create_invalid_card(self):
        url = reverse("cards")
        # Invalid date format for `exp_date` field
        data = {
            "number": "5555555555554444",
            "cvc_code": "382",
            "exp_date": "01/31/2023",
            "owner_name": "Chris Brown",
            "balance": 510.15,
            "active": True,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Missing required `number` field
        data = {
            "cvc_code": "382",
            "exp_date": "01/31/2023",
            "owner_name": "Chris Brown",
            "balance": 510.15,
            "active": True,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_cards(self):
        """
        Ensure we can list all existing cards
        """
        # Create new cards
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
        Card.objects.create(**expected_data[0])
        Card.objects.create(**expected_data[1])

        url = reverse("cards")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data), Card.objects.count()
        )  # Ensure the count matches

        for response_obj, expected_obj in zip(response.data, expected_data):
            for key in expected_obj:
                self.assertEqual(response_obj[key], expected_obj[key])
