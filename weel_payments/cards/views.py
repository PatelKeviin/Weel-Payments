from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Card, CardControl, Transaction
from .serializers import (
    CardSerializer,
    CardControlSerializer,
    TransactionSerializer,
    TransactionPayloadSerializer,
)


class CardListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        """
        List all existing cards
        """
        cards = Card.objects.all()
        serializer = CardSerializer(cards, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        Create a new card
        """
        data = {
            "number": request.data.get("number"),
            "cvc_code": request.data.get("cvc_code"),
            "exp_date": request.data.get("exp_date"),
            "owner_name": request.data.get("owner_name"),
            "balance": request.data.get("balance"),
            "active": request.data.get("active"),
        }
        serializer = CardSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CardControlListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        """
        List all existing card controls
        """
        card_controls = CardControl.objects.all()
        serializer = CardControlSerializer(card_controls, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        Create a new card control
        """
        data = {
            "card": request.data.get("card"),
            "type": request.data.get("type"),
            "value": request.data.get("value"),
            "active": request.data.get("active"),
        }
        serializer = CardControlSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CardControlDetailAPIView(APIView):
    def get_object(self, card_control_id):
        """
        Helper method to get the object with given `card_control_id`
        """
        try:
            return CardControl.objects.get(id=card_control_id)
        except CardControl.DoesNotExist:
            return None

    def delete(self, request, card_control_id, *args, **kwargs):
        """
        Delete a given card control
        """
        card_control_instance = self.get_object(card_control_id)
        if not card_control_instance:
            return Response(
                {
                    "response": f"CardControl object with `card_control_id = {card_control_id}` does not exists."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        card_control_instance.delete()
        return Response(
            {
                "response": f"CardControl object with `card_control_id = {card_control_id}` is deleted."
            },
            status=status.HTTP_200_OK,
        )


class TransactionListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        """
        List all card transactions, both approved and declined
        """
        transactions = Transaction.objects.all()
        serializer = TransactionSerializer(transactions, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        Process a new transaction for the given card against its card controls
        """
        data = {
            "card": request.data.get("card"),
            "amount": request.data.get("amount"),
            "merchant": request.data.get("merchant"),
            "merchant_category": request.data.get("merchant_category"),
        }

        serializer = TransactionPayloadSerializer(data=data)
        if serializer.is_valid():
            try:
                card = Card.objects.get(id=data["card"], active=True)

                # Apply active card controls
                controls = CardControl.objects.filter(card=card, active=True)
                control_violated = False

                for control in controls:
                    if (
                        control.type == CardControl.CATEGORY
                        and control.value != data["merchant_category"]
                    ):
                        message = "Category control violation"
                        control_violated = True
                    elif (
                        control.type == CardControl.MERCHANT
                        and control.value != data["merchant"]
                    ):
                        message = "Merchant control violation"
                        control_violated = True
                    elif control.type == CardControl.MAX_AMOUNT and data[
                        "amount"
                    ] > float(control.value):
                        message = "Max amount  control violation"
                        control_violated = True
                    elif control.type == CardControl.MIN_AMOUNT and data[
                        "amount"
                    ] < float(control.value):
                        message = "Min amount  control violation"
                        control_violated = True

                    if control_violated:
                        transaction = Transaction.objects.create(
                            card=card,
                            amount=data["amount"],
                            status=Transaction.DECLINED,
                            message=message,
                        )

                        return Response(
                            {"status": "DECLINED", "reason": message},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                # Check for sufficient balance
                if card.balance < data["amount"]:
                    message = "Insufficient balance"

                    transaction = Transaction.objects.create(
                        card=card,
                        amount=data["amount"],
                        status=Transaction.DECLINED,
                        message=message,
                    )

                    return Response(
                        {"status": "DECLINED", "reason": message},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except Card.DoesNotExist as e:
                return Response(
                    {
                        "message": "Card not found. Please ensure card is valid and exists in our system."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except Exception as e:
                return Response(
                    {"message": f"Something went wrong. Please try again later. {e}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            else:
                # Update the card balance
                card.balance -= data["amount"]
                card.save()

                transaction = Transaction.objects.create(
                    card=card,
                    amount=data["amount"],
                    status=Transaction.APPROVED,
                )

                return Response(
                    {
                        "status": "APPROVED",
                        "id": transaction.id,
                        "remaining_balance": card.balance,
                    },
                    status=status.HTTP_200_OK,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
