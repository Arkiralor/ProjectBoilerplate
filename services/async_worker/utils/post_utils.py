from fastapi import status

from database.collections import UserPostCollections
from database.methods import SynchronousMethods
from templates.func_response import Resp
from utils.language_utils import LanguageHandlers

class PostUtils:
    
    @classmethod
    async def search_for_posts_like_phrase(cls, term:str=None)->Resp:
        records = SynchronousMethods.all(collection=UserPostCollections.user_posts)
        results = []
        resp = Resp()

        for item in records:
            text = item.get('blurb')
            is_alike = LanguageHandlers.check_if_similiar(sample_text=term, tested_text=text)

            if is_alike.get('are_alike', False):
                sim_dict = {
                    'story': item,
                    'confidence': is_alike.get('confidence')
                }
                results.append(sim_dict)

        results = sorted(
            results, key=lambda data: data['confidence'], reverse=True)

        resp.message = f"Found matches for '{term}'."
        resp.data = results
        resp.status_code = status.HTTP_200_OK

        return resp
