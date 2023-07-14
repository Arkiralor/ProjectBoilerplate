from collections import OrderedDict

from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.responses import Response

from schema.request_schema import AlikeSearchRequest
from schema.response_schema import AuthorSearchResponse, AlikeSearchResponse



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
            
        if type(self.data) == dict or type(self.data) == OrderedDict and not self.error:
            return self.data
        
        else:
            return {
                "error": self.error,
                "message": self.to_text(),
                "data": self.data
            }
    
    def to_text(self):
        return f"{self.error.upper() if self.error else None}{':' if self.error else None }{self.message}"
    
    def to_response(self):
        return Response(
            self.to_dict(),
            status=self.status_code
        )
        
    
    def to_exception(self):

        return HTTPException(
            detail=self.to_text(),
            status_code=self.status_code
        )