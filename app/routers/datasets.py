import duckdb
import pandas as pd

from typing import List
from fastapi import APIRouter, UploadFile
from pydantic import BaseModel, parse_obj_as

from database.services import DatabaseService


class DatasetSchema(BaseModel):
    id: int | None = None
    name: str
    description: str | None = None
    path: str | None = None

    class Config:
        orm_mode = True


router = APIRouter(prefix='/datasets', tags=["datasets"])
db = DatabaseService()


@router.get("/")
async def all_datasets() -> List[DatasetSchema]:
    return parse_obj_as(List[DatasetSchema], db.get_datasets())


@router.post("/")
async def create_dataset(dataset: DatasetSchema) -> DatasetSchema:
    return parse_obj_as(DatasetSchema, db.create_dataset(dataset.name, dataset.description, dataset.path))


@router.get("/{dataset_id}/")
async def query(dataset_id: int, query: str):

    """
    SELECT DT, "Y_ЭКСГАУСТЕР А/М №9_ЗАПОРНАЯ АРМАТУРА ЭКСГАУСТЕРА №9" FROM "storage/datasets/1-y_train.parquet" WHERE DT <= '2019-01-17'
    """

    dataset = db.get_dataset(dataset_id)
    duckdb.read_parquet(dataset.path)
    
    df = duckdb.sql(query).df()
    df.set_index('DT', inplace=True)
    df = df.resample('1d').max()
    return df.reset_index().to_json()


@router.post("/{dataset_id}/upload/")
async def upload_dataset(dataset_id: int, file: UploadFile) -> DatasetSchema:

    dataset = db.get_dataset(dataset_id)

    dataset_location = f"storage/datasets/{dataset.id}-{file.filename}"
    with open(dataset_location, "wb+") as file_object:
        file_object.write(file.file.read())

    dataset.path = dataset_location
    db.commit()

    return parse_obj_as(DatasetSchema, dataset)
