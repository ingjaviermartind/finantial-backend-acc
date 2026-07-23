from rest_framework.views import exception_handler
from rest_framework import status


def custom_exception_handler(exc, context):

    response = exception_handler(exc, context)

    return response