from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from post_app.utils import TagModelUtils, PostModelUtils


class CreatePostAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request:Request, *args, **kwargs)->Response:
        """
        Create a new user post.
        """
        resp = PostModelUtils.create(user=request.user, data=request.data)
        
        
        return resp.to_response()
    
    def put(self, request:Request, *args, **kwargs)->Response:
        """
        Update a user post.
        """
        id = request.data.get("id")
        data = request.data.get("update")

        resp = PostModelUtils.update(user=request.user, id=id, data=data)
        
        
        return resp.to_response()
    
    def patch(self, request:Request, *args, **kwargs)->Response:
        """
        Update a user post's tags.
        """
        id = request.data.get("id")
        data = request.data.get("tags", [])

        resp = PostModelUtils.update_tags(user=request.user, id=id, data=data)
        
        
        return resp.to_response()
    
    def delete(self, request:Request, *args, **kwargs)->Response:
        """
        Outright delete a user post.
        """
        id = request.data.get("id")
        resp = PostModelUtils.delete(user=request.user, id=id)
        
        
        return resp.to_response()
    

class PostAPI(APIView):
    permission_classes = (AllowAny,)

    def get(self, request:Request, *args, **kwargs)->Response:
        """
        Retrieve a specific user Post
        """
        _id = request.query_params.get("id")
        _all = bool(request.query_params.get("all", False))
        page = int(request.query_params.get("page", 1))

        if _all:
            resp = PostModelUtils.get_all(page=page)
        else:
            resp = PostModelUtils.get(id=_id)
        
        
        return resp.to_response()
    
    def post(self, request:Request, *args, **kwargs)->Response:
        """
        Search for a user Post via a search term.
        """
        term = request.query_params.get("search", "")
        page = int(request.query_params.get("page", 1))

        resp = PostModelUtils.search(term=term, page=page)        
        return resp.to_response()