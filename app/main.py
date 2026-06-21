# main.py

from fastapi import FastAPI
from app.api.v1 import ingest  # adjust if your structure is different

app = FastAPI()

# Include your router
app.include_router(ingest.router)
