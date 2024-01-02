import uuid

from django.db import models
from django.db.models.functions import Now


class Card(models.Model):
    """
    Represents a Weel card
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    number = models.CharField(max_length=16, unique=True)
    exp_date = models.DateField("expiry date")
    cvc_code = models.CharField("security code", max_length=3)
    owner_name = models.CharField(max_length=100)
    balance = models.FloatField()
    active = models.BooleanField(default=True)

    class Meta:
        # Unique constraint to ensure each card number is unique
        constraints = [models.UniqueConstraint(fields=["number"], name="unique_card")]

    def __str__(self):
        """
        Returns a string representation of the Card instance
        """
        return f"<Card number='{self.number}' owner='{self.owner_name}' active='{self.active}'>"


class CardControl(models.Model):
    """
    Model to set various controls on a Card
    """

    CATEGORY = "CATG"
    MERCHANT = "MCHT"
    MAX_AMOUNT = "MXAM"
    MIN_AMOUNT = "MNAM"
    CATEGORY_TYPE = {
        CATEGORY: "Category",
        MERCHANT: "Merchant",
        MAX_AMOUNT: "Max Amount",
        MIN_AMOUNT: "Min Amount",
    }

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    card = models.ForeignKey(Card, related_name="controls", on_delete=models.CASCADE)
    type = models.CharField(
        max_length=4,
        choices=CATEGORY_TYPE,
        default=CATEGORY,
    )
    value = models.CharField(max_length=30)
    active = models.BooleanField(default=True)

    class Meta:
        # Unique constraint for the combination of card, type, and value
        constraints = [
            models.UniqueConstraint(
                fields=["card", "type", "value"], name="unique_card_control"
            )
        ]

    def __str__(self):
        """
        Returns a string representation of the CardControl instance
        """
        return f"<CardControl card='{self.card.number}' type='{self.type}' value='{self.value}'>"


class Transaction(models.Model):
    """
    Represents a financial transaction made using a Weel Card
    """

    APPROVED = "APPR"
    DECLINED = "DEC"
    STATUS = {APPROVED: "Approved", DECLINED: "Declined"}

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    timestamp = models.DateTimeField("creation timestamp", db_default=Now())
    amount = models.FloatField()
    status = models.CharField(
        max_length=4,
        choices=STATUS,
    )
    message = models.CharField(max_length=100, default="")

    def __str__(self):
        """
        Returns a string representation of the Transaction instance
        """
        return f"<Transaction card='{self.card.number}' amount='{self.amount}' status='{self.status}'>"
