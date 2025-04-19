"""Views to handle accounts requests"""

import csv
import io

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.generics import ListAPIView

from .models import CollectionAgency, Client, Consumer, Debt
from .serializers import DebtSerializer
import logging

logger = logging.getLogger(__name__)


class AccountListView(ListAPIView):
    serializer_class = DebtSerializer

    def get_queryset(self):
        queryset = Debt.objects.select_related("client__agency").prefetch_related("consumers").all()
        min_balance = self.request.query_params.get("min_balance")
        max_balance = self.request.query_params.get("max_balance")
        consumer_name = self.request.query_params.get("consumer_name")
        status = self.request.query_params.get("status")
        agency_id = self.request.query_params.get("agency_id")

        if agency_id:
            queryset = queryset.filter(client__agency_id=agency_id)

        if min_balance:
            queryset = queryset.filter(amount__gte=min_balance)

        if max_balance:
            queryset = queryset.filter(amount__lte=max_balance)

        if status:
            queryset = queryset.filter(status=status)

        if consumer_name:
            queryset = queryset.filter(consumers__name__icontains=consumer_name)

        return queryset.distinct()


@csrf_exempt
def upload_csv(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method allowed"}, status=405)

    if "file" not in request.FILES:
        return JsonResponse({"error": "CSV file is required"}, status=400)

    try:
        csv_file = request.FILES["file"]
        decoded_file = csv_file.read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(decoded_file))
        created = 0
        duplicated = 0
        failed = 0
        # if agency_id is not specified, added to the default one
        default_agency = CollectionAgency.objects.first()

        for row in reader:
            client_ref = row["client reference no"].strip()
            balance = row["balance"]
            status = row["status"].strip()
            name = row["consumer name"].strip()
            address = row["consumer address"].strip()
            ssn = row["ssn"].strip()
            agency_id = row.get("agency_id")
            if agency_id:
                _agency = CollectionAgency.objects.filter(id=agency_id)
                if not _agency:
                    print(f"Agency with ID {agency_id} not found.")
                    # logger.error(f"Agency with ID {agency_id} not found.")
                    failed += 1
                    continue
            else:
                _agency = default_agency
            # Get or create the client
            client, exists = Client.objects.get_or_create(
                reference_no=client_ref,
                defaults={
                    "name": f"Client {client_ref}",
                    "agency": _agency,
                },
            )
            if not exists:
                print(f"CLIENT already exists with SNN:{ssn}")

            # Get or create the consumer
            consumer, exists = Consumer.objects.get_or_create(
                ssn=ssn,
                defaults={
                    "name": name,
                    "address": address,
                    "is_entity": False,
                },
            )
            if not exists:
                print(f"Consumer already exists with SNN:{ssn}")

            # Create the debt
            debt = Debt.objects.create(
                balance=balance,
                status=status,
                client_reference_no=client_ref,
                client=client,
            )
            debt.consumers.add(consumer)
            created += 1

        return JsonResponse(
            {
                "status": "success",
                "data": {
                    "created": created,
                    "duplicated": duplicated,
                    "failed": failed,
                },
                "message": "File processed.",
            }
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
