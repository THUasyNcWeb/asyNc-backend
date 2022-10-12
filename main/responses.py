from django.http import HttpResponse, JsonResponse

def internal_error_response():
    return JsonResponse({"code": 1003, "message": "INTERNAL_ERROR", "data": {}}, status = 500, headers = {'Access-Control-Allow-Origin':'*'})

def unauthorized_response():
    return JsonResponse({"code": 1001, "message": "UNAUTHORIZED", "data": {}}, status = 401, headers = {'Access-Control-Allow-Origin':'*'})