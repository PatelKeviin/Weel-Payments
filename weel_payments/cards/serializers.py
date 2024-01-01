from rest_framework import serializers

from .models import Card, CardControl, Transaction


class FloatDecimalField(serializers.DecimalField):
    def to_representation(self, value):
        return float(super().to_representation(value))


class CardSerializer(serializers.ModelSerializer):
    balance = FloatDecimalField(max_digits=12, decimal_places=2)

    class Meta:
        model = Card
        fields = ["number", "exp_date", "cvc_code", "owner_name", "balance", "active"]


class CardControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardControl
        fields = ["card", "type", "value", "active"]


class TransactionSerializer(serializers.Serializer):
    card = serializers.CharField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    merchant = serializers.CharField()
    merchant_category = serializers.CharField()


# class TransactionSerializer(serializers.ModelSerializer):
#     timestamp = serializers.ReadOnlyField()

#     class Meta:
#         model = Transaction
#         fields = ["card", "timestamp", "amount", "status", "message"]
