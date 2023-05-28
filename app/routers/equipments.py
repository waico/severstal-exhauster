from typing import List
from fastapi import APIRouter
from pydantic import BaseModel, parse_obj_as

from database.services import DatabaseService


class NodeSchema(BaseModel):
    id: int | None = None
    name: str
    description: str | None = None

    class Config:
        orm_mode = True


class EquipmentSchema(BaseModel):
    id: int | None = None
    name: str
    description: str | None = None

    nodes: List[NodeSchema] = []

    class Config:
        orm_mode = True


router = APIRouter(prefix='/equipment', tags=["equipment"])
db = DatabaseService()


@router.get("/")
async def all_equipments() -> List[EquipmentSchema]:
    return parse_obj_as(List[EquipmentSchema], db.get_equipments())


@router.post("/")
async def create_equipment(equipment: EquipmentSchema) -> EquipmentSchema:
    return equipment


@router.get("/{equipment_id}/")
async def get_equipment(equipment_id: int) -> EquipmentSchema:
    equipment = EquipmentSchema(id=equipment_id, name='Eskengauer')
    return equipment
