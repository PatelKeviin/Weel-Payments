from rest_framework.response import Response
from rest_framework import status

from .models import Card, CardControl, Transaction


def process_transaction(transaction_request):
    card_number = transaction_request.get("card")
    amount = transaction_request.get("amount")
    merchant = transaction_request.get("merchant")
    category = transaction_request.get("merchant_category")

    try:
        card = Card.objects.get(number=card_number, active=True)

        # Apply card controls
        controls = CardControl.objects.filter(card=card, active=True)
        # for control in controls:
        #     if control.control_type == "CATEGORY" and control.value != category:
        #         return JsonResponse(
        #             {"status": "declined", "reason": "Category control violation"},
        #             status=400,
        #         )
        #     if control.control_type == "MERCHANT" and control.value != merchant:
        #         return JsonResponse(
        #             {"status": "declined", "reason": "Merchant control violation"},
        #             status=400,
        #         )
        #     if control.control_type == "MAX_AMOUNT" and amount > float(control.value):
        #         return JsonResponse(
        #             {"status": "declined", "reason": "Max amount control violation"},
        #             status=400,
        #         )
        #     if control.control_type == "MIN_AMOUNT" and amount < float(control.value):
        #         return JsonResponse(
        #             {"status": "declined", "reason": "Min amount control violation"},
        #             status=400,
        #         )

        # Check for sufficient balance
        if card.balance < amount:
            message = "Insufficient funds"

            Transaction.objects.create(
                card=card, amount=amount, status=Transaction.DECLINED, message=message
            )

            return Response({"message": message}, status=status.HTTP_400_BAD_REQUEST)
    except Card.DoesNotExist as e:
        return Response(
            {"message": "Card not found"}, status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {"message": "Something went wrong. Please try again later."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    else:
        # Update the card balance
        card.balance -= amount
        card.save()

        Transaction.objects.create(
            card=card,
            amount=amount,
            status=Transaction.APPROVED,
        )

        return Response({"status": "Approved"}, status=status.HTTP_200_OK)
