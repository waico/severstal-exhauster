import datetime

from sqlalchemy import  Column, Integer, String, Boolean, ForeignKey, DateTime, ARRAY
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Dataset(Base):
    __tablename__ = "datasets"
 
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    path = Column(String)


class Equipment(Base):
    __tablename__ = "equipments"
 
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)

    nodes = relationship("Node", back_populates="equipment")


class Node(Base):
    __tablename__ = "nodes"
 
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)

    equipment_id = Column(Integer, ForeignKey("equipments.id"))
    equipment = relationship("Equipment", back_populates="nodes")


class Tag(Base):
    __tablename__ = "tags"
 
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)

    equipment_id = Column(Integer, ForeignKey("equipments.id"))
    equipment = relationship("Equipment")

    node_id = Column(Integer, ForeignKey("nodes.id"))
    node = relationship("Node")


class Model(Base):
    __tablename__ = "models"
 
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    path = Column(String)


class Prediction(Base):
    __tablename__ = "predictions"
 
    id = Column(Integer, primary_key=True, index=True)
    path = Column(String)

    model_id = Column(Integer, ForeignKey("models.id"))
    model = relationship("Model")

    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    dataset = relationship("Dataset")
