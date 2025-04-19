"""Test cases for Accounts"""

from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import Client, CollectionAgency, Consumer, Debt


class CollectionAgencyTestCase(TestCase):
    """Test for CollectionAgency model."""

    def test_create_collection_agency(self):
        agency = CollectionAgency.objects.create(name="Agency A")
        self.assertEqual(agency.name, "Agency A")
        self.assertEqual(str(agency), "Agency A")


class ClientTestCase(TestCase):
    """Test for Client model."""

    def test_create_client(self):
        agency = CollectionAgency.objects.create(name="Agency A")
        client = Client.objects.create(name="Client 1", agency=agency)
        self.assertEqual(client.name, "Client 1")
        self.assertEqual(client.agency, agency)
        self.assertEqual(str(client), "Client 1")


class ConsumerTestCase(TestCase):
    """Test for Consumer model."""

    def test_create_consumer(self):
        consumer = Consumer.objects.create(name="John Doe", is_entity=False)
        self.assertEqual(consumer.name, "John Doe")
        self.assertEqual(consumer.is_entity, False)
        self.assertEqual(str(consumer), "John Doe")


class DebtTestCase(TestCase):
    """Test for Debt model."""

    def test_create_debt(self):
        agency = CollectionAgency.objects.create(name="Agency A")
        client = Client.objects.create(name="Client 1", agency=agency)
        consumer_1 = Consumer.objects.create(name="John Doe", is_entity=False)
        consumer_2 = Consumer.objects.create(name="Jane Smith", is_entity=False)

        debt = Debt.objects.create(amount=150.00, client=client)
        debt.consumers.add(consumer_1, consumer_2)  # Add multiple consumers

        self.assertEqual(debt.amount, 150.00)
        self.assertEqual(debt.client, client)
        self.assertIn(consumer_1, debt.consumers.all())
        self.assertIn(consumer_2, debt.consumers.all())
        self.assertEqual(debt.consumers.count(), 2)

    def test_debt_amount_validation(self):
        """Test for Debt amount validation (should raise error if amount is zero or negative)."""
        agency = CollectionAgency.objects.create(name="Agency A")
        client = Client.objects.create(name="Client 1", agency=agency)

        # Test for invalid (negative) amount
        with self.assertRaises(ValidationError):
            debt = Debt(amount=-1, client=client)
            debt.clean()  # Manually call clean to validate

        # Test for invalid (zero) amount
        with self.assertRaises(ValidationError):
            debt = Debt(amount=0, client=client)
            debt.clean()  # Manually call clean to validate


class RelationshipsTestCase(TestCase):
    """Test the relationships between models."""

    def test_client_has_debts(self):
        agency = CollectionAgency.objects.create(name="Agency A")
        client = Client.objects.create(name="Client 1", agency=agency)
        consumer_1 = Consumer.objects.create(name="John Doe", is_entity=False)
        debt = Debt.objects.create(amount=100.00, client=client)
        debt.consumers.add(consumer_1)

        # Test if client has the correct debts
        self.assertEqual(client.debts.count(), 1)
        self.assertEqual(client.debts.first().amount, 100.00)

    def test_consumer_has_debts(self):
        agency = CollectionAgency.objects.create(name="Agency A")
        client = Client.objects.create(name="Client 1", agency=agency)
        consumer_1 = Consumer.objects.create(name="John Doe", is_entity=False)
        debt = Debt.objects.create(amount=100.00, client=client)
        debt.consumers.add(consumer_1)

        # Test if consumer is related to the debt
        self.assertEqual(consumer_1.debts.count(), 1)
        self.assertEqual(consumer_1.debts.first().amount, 100.00)
