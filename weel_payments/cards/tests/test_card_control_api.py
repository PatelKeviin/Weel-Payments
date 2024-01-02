from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ..models import Card, CardControl
from ..serializers import CardControlSerializer


class CardControlListAPITestCase(APITestCase):
    CARD_CONTROL_URL = reverse("card-controls")

    @classmethod
    def setUpTestData(cls):
        cls.card_data = {
            "number": "5555555555554444",
            "cvc_code": "382",
            "exp_date": "2024-12-25",
            "owner_name": "Chris Brown",
            "balance": 510.15,
            "active": True,
        }
        cls.card = Card.objects.create(**cls.card_data)

    def create_card_control(self, control_data):
        return self.client.post(self.CARD_CONTROL_URL, control_data)

    def test_create_card_control(self):
        """
        Ensure we can create a new card control for a given card
        """
        card_id = self.card.id

        # Add new card controls
        control_types = [
            CardControl.MAX_AMOUNT,
            CardControl.MIN_AMOUNT,
            CardControl.MERCHANT,
            CardControl.CATEGORY,
        ]
        values = ["1000", "9.99", "Woolworths", "Grocery"]

        for control_type, value in zip(control_types, values):
            response = self.create_card_control(
                {
                    "card": self.card.id,
                    "type": control_type,
                    "value": value,
                    "active": True,
                }
            )

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data["type"], control_type)
            self.assertEqual(response.data["value"], value)

        self.assertEqual(CardControl.objects.count(), len(control_type))

    def test_create_card_control_using_invalid_payload(self):
        """
        Ensure 400 Bad Request response for an invalid card control payload
        """
        data = {
            "card": "00000000-0000-0000-0000-000000000000",  # Card does not exist
            "type": "MISC",  # Card control category does not exist
            "value": "Food",
            "active": True,
        }
        response = self.create_card_control(data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_card_controls(self):
        """
        Ensure we can list all existing card controls
        """
        # Add new card controls
        card_control_data = [
            {"type": CardControl.MIN_AMOUNT, "value": "9.99"},
            {"type": CardControl.CATEGORY, "value": "Shopping"},
        ]

        for control_data in card_control_data:
            control_data.update({"card": self.card, "active": True})
            CardControl.objects.create(**control_data)

        response = self.client.get(self.CARD_CONTROL_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data), len(card_control_data)
        )  # Ensure the count matches

        for response_obj, expected_obj in zip(response.data, card_control_data):
            for key in expected_obj:
                if key == "card":
                    self.assertEqual(response_obj[key], expected_obj[key].id)
                else:
                    self.assertEqual(response_obj[key], expected_obj[key])


class CardControlDetailAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.card_data = {
            "number": "5555555555554444",
            "cvc_code": "382",
            "exp_date": "2024-12-25",
            "owner_name": "Chris Brown",
            "balance": 510.15,
            "active": True,
        }
        cls.card = Card.objects.create(**cls.card_data)

        cls.card_control_data = {
            "card": cls.card,
            "type": CardControl.MERCHANT,
            "value": "Hungry Jacks",
            "active": True,
        }
        cls.card_control = CardControl.objects.create(**cls.card_control_data)

        cls.CARD_CONTROL_DETAIL_URL = reverse(
            "card-control-detail", kwargs={"card_control_id": cls.card_control.id}
        )

    def test_delete_card_control(self):
        """
        Ensure we can delete a card control
        """
        response = self.client.delete(self.CARD_CONTROL_DETAIL_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
