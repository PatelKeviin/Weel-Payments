from rest_framework import serializers

from .models import Card, CardControl, Transaction


class FloatDecimalField(serializers.DecimalField):
    def to_representation(self, value):
        return float(super().to_representation(value))


class CardControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardControl
        fields = ["type", "value", "active", "card"]


class CardSerializer(serializers.ModelSerializer):
    balance = FloatDecimalField(max_digits=12, decimal_places=2)
    controls = CardControlSerializer(many=True, read_only=True, default=[])

    class Meta:
        model = Card
        fields = [
            "number",
            "exp_date",
            "cvc_code",
            "owner_name",
            "balance",
            "active",
            "controls",
        ]


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
