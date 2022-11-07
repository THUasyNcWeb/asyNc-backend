"""
This .py file contains most commenly used responses in views.py

Created by sxx
"""
from django.http import JsonResponse


# return commen internal error response
def internal_error_response(error=""):
    """
        return commen internal error response
    """
    return JsonResponse(
        {
            "code": 1003,
            "message": "INTERNAL_ERROR",
            "data": {
                "error":error
            }
        },
        status=500,
        headers={
            'Access-Control-Allow-Origin':'*'
        }
    )


# return commen unauthorized response
def unauthorized_response():
    """
        return commen unauthorized response
    """
    return JsonResponse(
        {"code": 1001, "message": "UNAUTHORIZED", "data": {}},
        status=401,
        headers={'Access-Control-Allow-Origin':'*'}
    )


# return commen page not found response
def not_found_response():
    """
        return commen page not found response
    """
    return JsonResponse(
        {
            "code": 1000,
            "message":
            "NOT_FOUND",
            "data": {}
        },
        status=404,
        headers={
            'Access-Control-Allow-Origin':'*'
        }
    )


def post_data_format_error_response(error=""):
    """
        return post data format error
    """
    return JsonResponse(
        {
            "code": 8,
            "message": "POST_DATA_FORMAT_ERROR",
            "data": {
                "error": error
            }
        },
        status=400,
        headers={'Access-Control-Allow-Origin':'*'}
    )


def invalid_page(error=""):
    """
        invalid_page response
    """
    return JsonResponse(
        {
            "code": 5,
            "message": "INVALID_PAGE",
            "data": {
                "error": error
            }
        },
        status=400,
        headers={'Access-Control-Allow-Origin':'*'}
    )


def news_not_found(error=""):
    """
        invalid_page response
    """
    return JsonResponse(
        {
            "code": 9,
            "message": "NEWS_NOT_FOUND",
            "data": {
                "error": error
            }
        },
        status=400,
        headers={'Access-Control-Allow-Origin':'*'}
    )
