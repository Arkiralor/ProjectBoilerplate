from rest_framework import status

from core.boilerplate.response_template import Resp
from database.collections import DatabaseCollections
from database.methods import SynchronousMethods

from admin_app import logger

class RequestLogUtils:

    VALID_METHODS = (
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE"
    )

    @classmethod
    def get(cls, page:int=1)->Resp:
        resp = Resp()
        results = SynchronousMethods.find(collection=DatabaseCollections.request_logs, page=page)

        resp.message = f"{len(results)} results retrieved."
        resp.data = {
            "page": page,
            "results": results
        }
        resp.status_code = status.HTTP_200_OK

        logger.info(resp.message)
        return resp
    
    @classmethod
    def find_by_path(cls, method:str="get", path:str=None, page:int=1)->Resp:
        resp = Resp()

        if not path:
            resp.error = "Invalid Path"
            resp.message = "Argument `path` is mandatory."
            resp.data = f"path: {path}"
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warn(resp.to_text())
            return resp
        
        if not method.upper() in cls.VALID_METHODS:
            resp.error = "Invalid Method"
            resp.message = "Argument `method` is invalid."
            resp.data = {
                "valid_methods": cls.VALID_METHODS,
                "method": method
            }
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warn(resp.to_text())
            return resp
        
        filter_dict = {
            "$and": [
                {
                    "method": method.upper()
                },
                {
                    "path": {
                        "$regex": path.lower()
                    }
                }
            ]
        }

        results = SynchronousMethods.find(filter_dict=filter_dict, collection=DatabaseCollections.request_logs, page=page)

        resp.message = f"{len(results)} results retrieved."
        resp.data = {
            "page": page,
            "results": results
        }
        resp.status_code = status.HTTP_200_OK

        logger.info(resp.message)
        return resp
    
    @classmethod
    def find_by_text(cls, term:str=None, page:int=1)->Resp:
        resp = Resp()

        if not term:
            resp.error = "Invalid Term"
            resp.message = "Argument `term` is mandatory."
            resp.data = f"term: {term}"
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warn(resp.to_text())
            return resp
        
        filter_dict = {
            '$text': {
                '$search': term
                }
            }
        
        results = SynchronousMethods.find(filter_dict=filter_dict, collection=DatabaseCollections.request_logs, page=page)

        resp.message = f"{len(results)} results retrieved."
        resp.data = {
            "page": page,
            "results": results
        }
        resp.status_code = status.HTTP_200_OK

        logger.info(resp.message)
        return resp


