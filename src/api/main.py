from fastapi import FastAPI
from src.api.routes import router

app = FastAPI(title="Marathonbet Results API")
app.include_router(router)
