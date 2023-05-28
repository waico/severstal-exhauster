from typing import List
from fastapi import APIRouter, UploadFile, HTTPException
from pydantic import BaseModel, parse_obj_as

from database.services import DatabaseService

class ModelSchema(BaseModel):
    id: int | None = None
    name: str
    description: str | None = None
    path: str

    class Config:
        orm_mode = True


router = APIRouter(prefix='/models', tags=["models"])
db = DatabaseService()


@router.get("/")
async def all_models() -> List[ModelSchema]:
    return parse_obj_as(List[ModelSchema], db.get_models())


@router.post("/")
async def create_model(model: ModelSchema) -> ModelSchema:
    return model


@router.get("/{model_id}/")
async def get_model(model_id: int) -> ModelSchema:
    model = ModelSchema(name='Sample', path='s3', type='sd')
    return model


@router.post("/{model_id}/upload/")
async def upload_mlflow_model(model_id: int, file: UploadFile):

    if file.content_type != 'application/zip':
        raise HTTPException(400, detail="Invalid document type. Pass MLFlow zip archive")

    model_location = f"{file.filename}"
    with open(model_location, "wb+") as file_object:
        file_object.write(file.file.read())

    return {"info": f"file '{file.filename}' saved at '{model_location}'"}


@router.post("/{model_id}/predict/")
async def predict(model_id: int) -> None:
    pass