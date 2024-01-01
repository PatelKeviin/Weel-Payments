from django.db import models
from django.db.models.functions import Now


# Create your models here.
class Card(models.Model):
    id = models.AutoField(primary_key=True)
    number = models.CharField(max_length=16, unique=True)
    exp_date = models.DateField("expiry date")
    cvc_code = models.CharField("security code", max_length=3)
    owner_name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=12, decimal_places=2)
    active = models.BooleanField(default=True)

    class Meta:
        # UNIQUE contraint for (number) values
        constraints = [models.UniqueConstraint(fields=["number"], name="unique_card")]

    def __str__(self):
        return f"<Card number='{self.number}' owner='{self.owner_name}' active='{self.active}'>"


class CardControl(models.Model):
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
    id = models.AutoField(primary_key=True)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    type = models.CharField(
        max_length=4,
        choices=CATEGORY_TYPE,
        default=CATEGORY,
    )
    value = models.CharField(max_length=30)
    active = models.BooleanField(default=True)

    class Meta:
        # UNIQUE contraint for (Card, Type, Value) values
        constraints = [
            models.UniqueConstraint(
                fields=["card", "type", "value"], name="unique_card_control"
            )
        ]

    def __str__(self):
        return f"<CardControl card='{self.card.number}' type='{self.type}' value='{self.value}'>"


class Transaction(models.Model):
    APPROVED = "APPR"
    DECLINED = "DEC"
    STATUS = {APPROVED: "Approved", DECLINED: "Declined"}
    id = models.AutoField(primary_key=True)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    timestamp = models.DateTimeField("creation timestamp", db_default=Now())
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=4,
        choices=STATUS,
    )
    message = models.CharField(max_length=100, default="")

    def __str__(self):
        return f"<Transaction card='{self.card.number}' amount='{self.amount}' status='{self.status}'>"
