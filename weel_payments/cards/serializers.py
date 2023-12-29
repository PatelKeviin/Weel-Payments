from rest_framework import serializers

from .models import Card, CardControl, Transaction


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ["number", "exp_date", "cvc_code", "owner_name", "balance", "active"]


class CardControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardControl
        fields = ["card", "type", "value", "active"]
