"""Models representing the accounts app"""

from django.core.exceptions import ValidationError
from django.db import models


class CollectionAgency(models.Model):
    """A debt collection agency that works with multiple clients."""

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Client(models.Model):
    """Organization that hires a collection agency to collect debt on their behalf."""

    name = models.CharField(max_length=255)
    agency = models.ForeignKey(CollectionAgency, on_delete=models.CASCADE, related_name="clients")
    reference_no = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name


class Consumer(models.Model):
    """Describes the person/entity that owe the debt."""

    name = models.CharField(max_length=255)
    address = models.TextField()
    ssn = models.CharField(max_length=11, unique=False)  # e.g., '123-45-6789'
    is_entity = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    pass


class Debt(models.Model):
    """The amount owed by one or more consumers"""

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="debts")
    consumers = models.ManyToManyField(Consumer, related_name="debts")
    client_reference_no = models.CharField(max_length=64)
    status = models.CharField(max_length=32)

    def clean(self):
        """Validates that the amount is greater than zero."""
        if self.amount <= 0:
            raise ValidationError("Amount must be greater than zero.")

    def __str__(self):
        return f"Debt #{self.id} (${self.amount})"
