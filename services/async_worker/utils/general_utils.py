import spacy
from spacy.language import Language as ln
from spacy_langdetect import LanguageDetector
import en_core_web_md

from fastapi import status
from fastapi.exceptions import HTTPException

from config.constants import ProjectConstants


class LanguageHandlers:
    '''
    Class to handle language detection in blogposts while adding a new blog-post:
    '''
    input_text: str = None
    confidence_threshold: float = 0.82
    max_length: int = 2_000_000

    def __init__(self, input_text: str):
        '''
        Initialization method for the class:
        '''
        self.input_text = input_text

    def __repr__(self):
        '''
        Representation method for the class:
        '''
        return f"{self.input_text}"

    def detect_language(self):
        '''
        Method to detect the language of the passed text:
        '''
        try:
            ## MAJOR CHANGE in Spacy v3:
            ## Language.factory() no longer accepts a class directly as the first arg.
            ## Instead, now it calls a tagged decorator that calls a function that return the class-pointer.
            ln.factory("language_detector", func=create_lang_detector)

            ## Loading the NLP model to the nlp object
            nlp = en_core_web_md.load(disable=[None])

            nlp.max_length = self.max_length

            nlp.add_pipe("language_detector", last=True)

            ## Initial parsing of the text by the nlp object
            doc = nlp(self.input_text)
            lang_code = doc._.language.get("language")
            confidence_score = doc._.language.get("score")

            if confidence_score >= self.confidence_threshold and lang_code in ProjectConstants.LANG_DICT.keys():
                return ProjectConstants.LANG_DICT.get(lang_code)
            else:
                lang_code = "default"
                return ProjectConstants.LANG_DICT.get(lang_code)

        except Exception as ex:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"{ex}"
            )

    @classmethod
    def check_if_similiar(cls, sample_text: str, tested_text: str):
        """
        Classmethod to check if two given texts are cosine-similiar
        Args:
            sample_text (str): The text that is provided by the user
            tested_text (str): The text that is recieved from the database
        Returns:
            bool: If the two texts are similiar
        """

        try:
            nlp = en_core_web_md.load(disable=[None])
            nlp.max_length = cls.max_length

            sample_doc = nlp(sample_text)
            tested_doc = nlp(tested_text)

            sim_index = sample_doc.similarity(tested_doc)

            if sim_index >= cls.confidence_threshold:
                resp = {
                    "are_alike": True,
                    "confidence": sim_index,
                }
            else:
                resp = {
                    "are_alike": False,
                    "confidence": sim_index,
                }

            return resp
        except Exception as ex:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"{ex}"
            )


@ln.factory('language_detector')
def create_lang_detector(nlp, name):
    '''
    function to create language model.
    '''
    return LanguageDetector()


if __name__ == "__main__":
    pass