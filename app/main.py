from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from routers import equipments, datasets, models, frontends


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(equipments.router)
app.include_router(datasets.router)
app.include_router(models.router)
app.include_router(frontends.router)

app.mount("/static", StaticFiles(directory="static"), name="static")
