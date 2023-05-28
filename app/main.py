from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routers import equipments, datasets, models, frontends


app = FastAPI()

app.include_router(equipments.router)
app.include_router(datasets.router)
app.include_router(models.router)
app.include_router(frontends.router)

app.mount("/static", StaticFiles(directory="static"), name="static")