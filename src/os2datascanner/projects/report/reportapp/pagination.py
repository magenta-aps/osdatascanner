# from rest_framework import pagination
from django.conf import settings
from rest_framework import pagination
from rest_framework.response import Response


class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 10  # change the records per page from here
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({
            'previous': self.get_previous_link(),
            'next': self.get_next_link(),
            'count': self.page.paginator.count,
            'page_number': self.page.number,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })
