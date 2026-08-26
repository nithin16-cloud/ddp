from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
import models  # noqa: F401 — ensures models are registered before create_all
from routers import auth_router

# Creates tables if they don't exist yet. Fine for development;
# use Alembic migrations instead once the schema stabilizes.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="LabLine API", version="0.1.0")

# Allow the frontend (served separately, e.g. via Live Server) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this to your actual frontend origin before deploying
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)


@app.get("/")
def root():
    return {"status": "LabLine API is running"}
