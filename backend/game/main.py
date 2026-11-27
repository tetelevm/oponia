from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from admin import setup_admin
from database import get_engine
from routes import router
from settings import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    if settings.admin_password.get_secret_value() and not hasattr(app.state, "admin"):
        app.state.admin = setup_admin(app, get_engine(), settings)

    yield


app = FastAPI(title="Oponia Game", lifespan=lifespan)
app.include_router(router)
