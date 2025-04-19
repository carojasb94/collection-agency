"""Test cases for Accounts"""

import io

import pytest
from django.urls import reverse

from accounts.models import Client, Consumer, Debt


@pytest.mark.django_db
def test_upload_csv_success(client):
    csv_content = """client reference no,balance,status,consumer name,consumer address,ssn
abcd1234,100.50,IN_COLLECTION,John Doe,"123 Main St, City",111-11-1111
abcd1234,200.00,PAID_IN_FULL,Jane Smith,"456 Elm St, Town",222-22-2222
"""
    file = io.StringIO(csv_content)
    file.name = "test.csv"

    response = client.post(
        reverse("upload-csv"),
        {"file": file},
        format="multipart",
    )

    assert response.status_code == 200
    assert "2 debts created" in response.json()["message"]

    client_obj = Client.objects.get(reference_no="abcd1234")
    assert client_obj.name == "Client abcd1234"

    assert Client.objects.count() == 1
    assert Consumer.objects.count() == 2
    assert Debt.objects.count() == 2

    debt = Debt.objects.first()
    assert debt.status in ["IN_COLLECTION", "PAID_IN_FULL"]
    assert debt.client == client_obj
    assert debt.consumers.exists()


@pytest.mark.django_db
def test_upload_csv_missing_file(client):
    response = client.post(reverse("upload-csv"))
    assert response.status_code == 400
    assert response.json()["error"] == "CSV file is required"


@pytest.mark.django_db
def test_upload_csv_invalid_method(client):
    response = client.get(reverse("upload-csv"))
    assert response.status_code == 405
    assert response.json()["error"] == "Only POST method allowed"


@pytest.mark.django_db
def test_upload_csv_invalid_csv(client):
    csv_content = "wrong,header,here\nbad,data,here"
    file = io.StringIO(csv_content)
    file.name = "bad.csv"

    response = client.post(
        reverse("upload-csv"),
        {"file": file},
        format="multipart",
    )

    assert response.status_code == 500
    assert "error" in response.json()
