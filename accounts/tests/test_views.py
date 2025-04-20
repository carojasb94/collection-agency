# accounts/tests/test_views.py

import io
from django.test import TestCase, Client
from django.urls import reverse

from accounts.models import Client as ClientModel, Consumer, Debt, CollectionAgency
from rest_framework.test import APIClient


class AccountListViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.agency = CollectionAgency.objects.create(name="Agency A")
        self.client_obj = ClientModel.objects.create(
            name="Client 1", agency=self.agency, reference_no="ref1"
        )
        self.consumer1 = Consumer.objects.create(
            name="Alice", address="123 Main St", ssn="111-11-1111"
        )
        self.consumer2 = Consumer.objects.create(
            name="Bob", address="456 Oak Ave", ssn="222-22-2222"
        )

        self.debt1 = Debt.objects.create(
            balance=100.00,
            status="IN_COLLECTION",
            client_reference_no="ref1",
            client=self.client_obj,
        )
        self.debt1.consumers.add(self.consumer1)

        self.debt2 = Debt.objects.create(
            balance=200.00,
            status="PAID_IN_FULL",
            client_reference_no="ref2",
            client=self.client_obj,
        )
        self.debt2.consumers.add(self.consumer2)
        self.url = reverse("accounts-list")

    def test_list_all_debts(self):
        """Should return all debts with no filters applied."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 2)

    def test_filter_by_min_balance(self):
        """Should return debts with balance >= min_balance."""
        response = self.client.get(self.url, {"min_balance": 150})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["balance"], "200.00")

    def test_filter_by_max_balance(self):
        """Should return debts with balance <= max_balance."""
        response = self.client.get(self.url, {"max_balance": 150})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["balance"], "100.00")

    def test_filter_by_agency_id(self):
        """Should return debts belonging to the given agency ID."""
        response = self.client.get(self.url, {"agency_id": self.agency.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 2)

    def test_filter_by_status(self):
        """Should return debts matching the given status."""
        response = self.client.get(self.url, {"status": "IN_COLLECTION"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["status"], "IN_COLLECTION")

    def test_filter_by_consumer_name(self):
        """Should return debts where consumer name matches case-insensitive substring."""
        response = self.client.get(self.url, {"consumer_name": "ali"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertIn("Alice", response.data["results"][0]["consumers"][0]["name"])


class UploadCSVTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.agency = CollectionAgency.objects.create(name="Agency X")

    def test_upload_csv_success(self):
        """Test that uploading a valid CSV creates the expected Client, Consumer, and Debt records."""

        csv_content = """client reference no,balance,status,consumer name,consumer address,ssn
abcd1234,100.50,IN_COLLECTION,John Doe,"123 Main St, City",111-11-1111
abcd1234,200.00,PAID_IN_FULL,Jane Smith,"456 Elm St, Town",222-22-2222
"""
        file = io.StringIO(csv_content)
        file.name = "test.csv"

        response = self.client.post(
            reverse("upload-csv"),
            {"file": file},
            format="multipart",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            {
                "status": "success",
                "data": {"created": 2, "duplicated": 0, "failed": 0},
                "message": "File processed.",
            },
            response.json(),
        )

        client_obj = ClientModel.objects.get(reference_no="abcd1234")
        self.assertEqual(client_obj.name, "Client abcd1234")

        self.assertEqual(ClientModel.objects.count(), 1)
        self.assertEqual(Consumer.objects.count(), 2)
        self.assertEqual(Debt.objects.count(), 2)

        debt = Debt.objects.first()
        self.assertIn(debt.status, ["IN_COLLECTION", "PAID_IN_FULL"])
        self.assertEqual(debt.client, client_obj)
        self.assertTrue(debt.consumers.exists())

    def test_upload_csv_missing_file(self):
        """Test that a POST request without a CSV file returns a 400 error with an appropriate message."""

        response = self.client.post(reverse("upload-csv"))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "CSV file is required")

    def test_upload_csv_invalid_method(self):
        """Test that making a GET request to the upload endpoint returns a 405 Method Not Allowed error."""

        response = self.client.get(reverse("upload-csv"))
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json()["error"], "Only POST method allowed")

    def test_upload_csv_invalid_csv(self):
        """Test that uploading a CSV with invalid headers or content returns a 500 error with an error message."""
        csv_content = "wrong,header,here\nbad,data,here"
        file = io.StringIO(csv_content)
        file.name = "bad.csv"

        response = self.client.post(
            reverse("upload-csv"),
            {"file": file},
            format="multipart",
        )

        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json())

    def test_upload_csv_with_valid_and_invalid_agency_id(self):
        """Test that uploading a CSV with both valid and invalid agency_id results in correct processing."""

        # Mock CSV content, with 1 valid row and one with invalid agency_id
        csv_content = """client reference no,balance,status,consumer name,consumer address,ssn,agency_id
abcd1234,100.50,IN_COLLECTION,John Doe,"123 Main St, City",111-11-1111,
abcd1234,100.50,IN_COLLECTION,John Doe,"123 Main St, City",111-11-1111,{agency_id_valid}
abcd5678,200.00,PAID_IN_FULL,Jane Smith,"456 Elm St, Town",222-22-2222,999999
""".format(
            agency_id_valid=self.agency.id
        )  # Using the valid agency ID created in setup

        # Convert CSV content to a file-like object
        file = io.StringIO(csv_content)
        file.name = "test.csv"

        # Send POST request to upload the file
        response = self.client.post(
            reverse("upload-csv"),
            {"file": file},
            format="multipart",
        )

        # Verify the response status code is 200
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Check that the response indicates 2 records created and 1 failed
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["data"]["created"], 2)  # 2 records created
        self.assertEqual(data["data"]["failed"], 1)  # 1 failed due to invalid agency_id

        # Verify that the Client, Consumer, and Debt objects were created correctly
        self.assertEqual(Client.objects.count(), 2)
        self.assertEqual(Consumer.objects.count(), 2)
        self.assertEqual(Debt.objects.count(), 2)

        # Check that the client with a valid agency_id has the correct agency assigned
        client_valid = Client.objects.get(reference_no="abcd1234")
        self.assertEqual(client_valid.agency, self.agency)

        # Verify client with the wrong agency_id was not created
        client_invalid = Client.objects.filter(reference_no="abcd5678").first()
        self.assertIsNone(client_invalid)
