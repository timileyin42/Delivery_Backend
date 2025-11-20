from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from .utils import success_response


class CustomPagination(PageNumberPagination):
    """
    Custom pagination class with configurable page size.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'
    
    def get_paginated_response(self, data):
        """
        Return paginated response in custom format.
        """
        return Response(success_response(
            data={
                'count': self.page.paginator.count,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'total_pages': self.page.paginator.num_pages,
                'current_page': self.page.number,
                'results': data
            },
            message="Data retrieved successfully"
        ))


class LargePagination(PageNumberPagination):
    """
    Pagination for endpoints that need larger page sizes.
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200
