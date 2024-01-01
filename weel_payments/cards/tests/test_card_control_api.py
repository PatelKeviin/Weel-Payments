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

    def test_create_card_control_using_invalid_payload(self):
        """
        Ensure 400 Bad Request response for an invalid card control payload
        """
        url = reverse("card-controls")
        # Invalid card and card control category
        data = {
            "card": "00000000-0000-0000-0000-9ce906cdb408",  # Card does not exist
            "type": "MISC",  # Card control category does not exist
            "value": "Food",
            "active": True,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_card_controls(self):
        """
        Ensure we can list all existing card controls
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

        # Add new card controls
        card_control_data = [
            {
                "card": card,
                "type": CardControl.MIN_AMOUNT,
                "value": "9.99",
                "active": True,
            },
            {
                "card": card,
                "type": CardControl.CATEGORY,
                "value": "Shopping",
                "active": True,
            },
        ]
        CardControl.objects.create(**card_control_data[0])
        CardControl.objects.create(**card_control_data[1])

        url = reverse("card-controls")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data), CardControl.objects.count()
        )  # Ensure the count matches

        for response_obj, expected_obj in zip(response.data, card_control_data):
            for key in expected_obj:
                if key == "card":
                    self.assertEqual(response_obj[key], expected_obj[key].id)
                else:
                    self.assertEqual(response_obj[key], expected_obj[key])


class CardControlDetailAPITestCase(APITestCase):
    def test_delete_card_control(self):
        """
        Ensure we can delete a card control
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
        # Add card control
        card_control_data = {
            "card": card,
            "type": CardControl.MERCHANT,
            "value": "Hungry Jacks",
            "active": True,
        }
        card_control = CardControl.objects.create(**card_control_data)

        url = reverse(
            "card-control-detail", kwargs={"card_control_id": card_control.id}
        )
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
