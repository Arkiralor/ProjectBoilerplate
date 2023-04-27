from fastapi import FastAPI

from controllers import search

app = FastAPI()

app.include_router(search.router)
