from django.urls import path

from . import views

# /accounts?min_balance=100&max_balance=1000&status=in_collection`
urlpatterns = [
    path("", views.AccountListView.as_view(), name="accounts-list"),
    path("csv", views.upload_csv, name="upload-csv"),
]
