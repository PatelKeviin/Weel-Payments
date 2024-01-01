from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ..models import Card, CardControl
from ..serializers import CardControlSerializer


class CardControlListAPITestCase(APITestCase):
    def test_create_card_control(self):
        """
        Ensure we can create a new card control for a given card
        """
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

        # Add new card controls
        url = reverse("card-controls")
        data = [
            {
                "card": card_id,
                "type": CardControl.MAX_AMOUNT,
                "value": "1000",
                "active": True,
            },
            {
                "card": card_id,
                "type": CardControl.MIN_AMOUNT,
                "value": "9.99",
                "active": True,
            },
            {
                "card": card_id,
                "type": CardControl.MERCHANT,
                "value": "Woolworths",
                "active": True,
            },
            {
                "card": card_id,
                "type": CardControl.CATEGORY,
                "value": "Grocery",
                "active": True,
            },
        ]

        for card_control_data in data:
            response = self.client.post(url, card_control_data)

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            for key in card_control_data:
                # Assert every key in the card control object
                self.assertEqual(response.data[key], card_control_data[key])

        self.assertEqual(CardControl.objects.count(), 4)

    # def test_create_card_control_using_invalid_card(self):
    #     url = reverse("card-controls")
    #     # Invalid card number
    #     data = {
    #         "number": "0000000000000000",
    #         "cvc_code": "113",
    #         "exp_date": "2026-06-12",
    #         "owner_name": "Phillip Patek",
    #         "balance": "510.15",
    #         "active": True,
    #     }
    #     response = self.client.post(url, data)
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    #     # Missing required `number` field
    #     data = {
    #         "cvc_code": "382",
    #         "exp_date": "01/31/2023",
    #         "owner_name": "Chris Brown",
    #         "balance": "510.15",
    #         "active": True,
    #     }
    #     response = self.client.post(url, data)
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_list_cards(self):
    #     """
    #     Ensure we can list all existing cards
    #     """
    #     # Create new cards
    #     expected_data = [
    #         {
    #             "number": "5555555555554444",
    #             "cvc_code": "123",
    #             "exp_date": "2024-03-12",
    #             "owner_name": "Kevin Patel",
    #             "balance": 500,
    #             "active": False,
    #         },
    #         {
    #             "number": "2211555555554444",
    #             "cvc_code": "777",
    #             "exp_date": "2024-10-29",
    #             "owner_name": "Steve Smith",
    #             "balance": 100.99,
    #             "active": True,
    #         },
    #     ]
    #     Card.objects.create(**expected_data[0])
    #     Card.objects.create(**expected_data[1])

    #     url = reverse("cards")
    #     response = self.client.get(url)

    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(
    #         len(response.data), Card.objects.count()
    #     )  # Ensure the count matches

    #     for response_obj, expected_obj in zip(response.data, expected_data):
    #         for key in expected_obj:
    #             self.assertEqual(response_obj[key], expected_obj[key])
