"""
Custom exception handling for the AutoTrader API.
"""

import logging

from django.core.exceptions import PermissionDenied, ValidationError as DjangoValidationError
from django.http import Http404
from rest_framework import exceptions as drf_exceptions
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that normalizes all error responses to
    a consistent format:

    {
        "error": true,
        "code": "error_code",
        "message": "Human-readable message",
        "details": { ... }  # optional
    }
    """
    # Convert Django exceptions to DRF exceptions
    if isinstance(exc, Http404):
        exc = drf_exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = drf_exceptions.PermissionDenied()
    elif isinstance(exc, DjangoValidationError):
        exc = drf_exceptions.ValidationError(detail=exc.message_dict if hasattr(exc, "message_dict") else exc.messages)

    # Let DRF handle the exception first
    response = drf_exception_handler(exc, context)

    if response is None:
        # Unhandled exception -- log and return 500
        logger.exception(
            "Unhandled exception in %s",
            context.get("view", "unknown view"),
            exc_info=exc,
        )
        response = Response(
            {
                "error": True,
                "code": "internal_server_error",
                "message": "An unexpected error occurred. Please try again later.",
            },
            status=500,
        )
        return response

    # Normalize the response body
    error_code = _get_error_code(exc)
    message = _get_error_message(exc, response)
    details = _get_error_details(response)

    response.data = {
        "error": True,
        "code": error_code,
        "message": message,
    }

    if details:
        response.data["details"] = details

    return response


def _get_error_code(exc):
    """Derive a machine-readable error code from the exception."""
    code_map = {
        drf_exceptions.ValidationError: "validation_error",
        drf_exceptions.AuthenticationFailed: "authentication_failed",
        drf_exceptions.NotAuthenticated: "not_authenticated",
        drf_exceptions.PermissionDenied: "permission_denied",
        drf_exceptions.NotFound: "not_found",
        drf_exceptions.MethodNotAllowed: "method_not_allowed",
        drf_exceptions.Throttled: "throttled",
    }

    for exc_class, code in code_map.items():
        if isinstance(exc, exc_class):
            return code

    if hasattr(exc, "default_code"):
        return exc.default_code

    return "error"


def _get_error_message(exc, response):
    """Extract a human-readable message from the exception."""
    if isinstance(exc, drf_exceptions.ValidationError):
        return "Validation failed. Check the 'details' field for specifics."
    if isinstance(exc, drf_exceptions.Throttled):
        wait = exc.wait
        return f"Request rate limit exceeded. Try again in {int(wait)} seconds."
    if hasattr(exc, "detail"):
        detail = exc.detail
        if isinstance(detail, str):
            return detail
        if isinstance(detail, list) and len(detail) > 0:
            return str(detail[0])
    return "An error occurred."


def _get_error_details(response):
    """Extract structured error details for validation errors."""
    if response.status_code != 400:
        return None

    data = response.data
    if isinstance(data, dict):
        # Flatten DRF's nested error structure
        details = {}
        for field, errors in data.items():
            if isinstance(errors, list):
                details[field] = [str(e) for e in errors]
            elif isinstance(errors, str):
                details[field] = [errors]
            else:
                details[field] = errors
        return details if details else None
    if isinstance(data, list):
        return {"non_field_errors": [str(e) for e in data]}
    return None


class AutoTraderAPIException(drf_exceptions.APIException):
    """Base exception class for AutoTrader-specific API errors."""

    status_code = 500
    default_detail = "An internal error occurred."
    default_code = "autotrader_error"


class VINDecodingError(AutoTraderAPIException):
    """Raised when VIN decoding fails."""

    status_code = 502
    default_detail = "Unable to decode VIN. The external service may be unavailable."
    default_code = "vin_decoding_error"


class ListingNotActiveError(AutoTraderAPIException):
    """Raised when an operation requires an active listing."""

    status_code = 400
    default_detail = "This listing is no longer active."
    default_code = "listing_not_active"
