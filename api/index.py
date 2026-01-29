from fastapi import FastAPI
from mangum import Mangum

from backend.routes.analyzer import router as analyzer_router

app = FastAPI()

app.include_router(analyzer_router)

handler = Mangum(app)
