from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.request import Request
from rest_framework.views import APIView

from admin_app.utils import RequestLogUtils
from auth.permissions import IsModerator
from core.boilerplate.response_template import Resp

from admin_app import logger

class RequestLogsAPI(APIView):
    permission_classes = (IsModerator,)

    def get(self, request:Request, *args, **kwargs):
        """
        Get all request Logs by page.
        """
        page = int(request.query_params.get("page", 1))

        resp = RequestLogUtils.get(page=page)
        
        return resp.to_response()
    
    def post(self, request:Request, *args, **kwargs):
        """
        Search for a request by a given term or path.
        """
        path = request.query_params.get("path", None)
        method = request.query_params.get("method", "GET")
        term = request.query_params.get("term", None)
        page = int(request.query_params.get("page", 1))

        if term:
            resp = RequestLogUtils.find_by_text(term=term, page=page)

        else:
            resp = RequestLogUtils.find_by_path(method=method, path=path, page=page)

        
        return resp.to_response()