from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.v1 import ingest
from app.api.v1 import matcher as match
from app.api.v1 import analysis
from app.db.crud import init_db



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs on startup — create DB tables if they don't exist
    init_db()
    yield
    # Runs on shutdown (nothing to clean up for now)


app = FastAPI(lifespan=lifespan)

app.include_router(ingest.router)
app.include_router(match.router)
app.include_router(analysis.router)