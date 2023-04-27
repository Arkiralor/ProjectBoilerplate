from typing import List

from fastapi import APIRouter, status, Body
from fastapi.encoders import jsonable_encoder

from utils.post_utils import PostUtils
from schema.response_schema import AlikeSearchResponse
from schema.request_schema import AlikeSearchRequest

router = APIRouter(
    prefix='/search',
    tags=['search']
)

@router.post("/", response_model=list[AlikeSearchResponse], status_code=status.HTTP_200_OK)
async def search_alike_post(term: AlikeSearchRequest = Body(...)):
    term = jsonable_encoder(term).get("phrase")
    resp = await PostUtils.search_for_posts_like_phrase(term=term)
    if resp.error:
        raise resp.to_exception()
    
    return resp.data