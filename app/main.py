from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database import Base, engine
from .routers import playlists, songs


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Playcatch API", version="1.0.0", lifespan=lifespan)
app.include_router(songs.router)
app.include_router(playlists.router)


@app.get("/health", tags=["infra"])
def health():
    return {"status": "ok"}
