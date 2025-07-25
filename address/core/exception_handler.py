from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.transaction import TransactionManagementError
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    if isinstance(exc, TransactionManagementError):
        return Response(
            {"message": str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    if isinstance(exc, DjangoValidationError):
        messages = (
            exc.message_dict if hasattr(exc, 'message_dict') else exc.messages
        )
        return Response(
            {"message": messages},
            status=status.HTTP_400_BAD_REQUEST
        )

    response = exception_handler(exc, context)

    if response is None:
        if settings.DEBUG:
            raise exc
        return Response(
            {"message": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    data = response.data

    if 'detail' in data:
        data['message'] = data.pop('detail')

    if response.status_code == status.HTTP_403_FORBIDDEN:
        response.status_code = status.HTTP_401_UNAUTHORIZED

    response.data = data
    return response
