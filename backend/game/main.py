from fastapi import FastAPI

from routes import router

app = FastAPI(title="Oponia Game")
app.include_router(router)
