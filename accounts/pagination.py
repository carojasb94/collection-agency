""" Pagination class for Accounts app"""

from rest_framework.pagination import LimitOffsetPagination


class CustomLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 50
    max_limit = 1000
