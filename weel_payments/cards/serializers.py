from rest_framework import serializers

from .models import Card, CardControl, Transaction


class CardControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardControl
        fields = ["type", "value", "active", "card"]


class CardSerializer(serializers.ModelSerializer):
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
