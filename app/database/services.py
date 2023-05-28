import sqlalchemy

from typing import List
from sqlalchemy.orm import sessionmaker

from .settings import ENGINE
from .models import Base, Dataset, Equipment, Node, Model


class DatabaseService():

    def __init__(self) -> None:
        engine = sqlalchemy.create_engine(ENGINE)
        Base.metadata.create_all(bind=engine)

        Session = sessionmaker(autoflush=False, bind=engine)
        self.session = Session()
    

    def _create_and_commit(self, instance: object):
        self.session.add(instance)
        self.session.commit()


    def get_datasets(self):
        return self.session.query(Dataset).all()


    def get_dataset(self, id: int) -> Dataset:
        return self.session.get(Dataset, id)
    
    
    def create_dataset(self, name, description, path) -> Dataset:
        dataset = Dataset(name=name, description=description, path=path)
        self._create_and_commit(dataset)
        return dataset


    def get_equipments(self) -> List[Equipment]:
        return self.session.query(Equipment).all()
    

    def create_equipment(self, name, description) -> Equipment:
        equipment = Equipment(name=name, description=description)
        self._create_and_commit(equipment)
        return equipment

    
    def create_node(self, name, description, equipment: Equipment) -> None:
        node = Node(name=name, description=description, equipment=equipment)
        self._create_and_commit(node)


    def create_model(self, name, description, path) -> None:
        model = Model(name=name, description=description, path=path)
        self._create_and_commit(model)
        return model


    def get_models(self):
        return self.session.query(Model).all()


    def commit(self) -> None:
        self.session.commit()
