from rest_framework import serializers

from .models import Consumer, Debt


class ConsumerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consumer
        fields = ["id", "name", "is_entity"]


class DebtSerializer(serializers.ModelSerializer):
    consumers = ConsumerSerializer(many=True)

    class Meta:
        model = Debt
        fields = ["id", "balance", "status", "client", "consumers"]
