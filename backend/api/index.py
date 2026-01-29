from fastapi import FastAPI
from mangum import Mangum

from app.routes.analyzer import router as analyzer_router
from app.routes.export import router as export_router

app = FastAPI()

app.include_router(analyzer_router)
app.include_router(export_router)

handler = Mangum(app)
