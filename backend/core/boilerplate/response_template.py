from collections import OrderedDict

from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.utils.serializer_helpers import ReturnDict

from core import logger

class Resp:
    error: str = None
    message: str = None
    data: dict or str or int or bool = None
    status_code: int = None

    def __init__(self, error:str=None, message:str=None, data:dict or str or int or bool=None, status_code:int=None)->None:
        if error:
            self.error = error
        if message:
            self.message = message
        if data:
            self.data = data
        if status_code:
            self.status_code = status_code

    def to_dict(self):
        if self.error:
            logger.warn(self.to_text())
            
        if (type(self.data) == dict or type(self.data) == OrderedDict or type(self.data) == ReturnDict) and not self.error:
            return self.data
        
        else:
            return {
                "error": self.error,
                "message": self.to_text(),
                "data": self.data
            }
    
    def to_text(self):
        return f"{self.error.upper()}:  {self.message}"
    
    def to_response(self):
        return Response(
            self.to_dict(),
            status=self.status_code
        )
        
    
    def to_exception(self):
        logger.warn(self.to_text())

        return APIException(
            detail=self.to_text(),
            code=self.error
        )