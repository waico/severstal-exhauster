import sqlalchemy

from pathlib import Path

from database.services import DatabaseService
from database.models import Base
from database.settings import ENGINE

Path('database.db').unlink(missing_ok=True)
Path('storage/datasets/').mkdir(parents=True, exist_ok=True)
Path('storage/predictions/').mkdir(parents=True, exist_ok=True)

engine = sqlalchemy.create_engine(ENGINE)
Base.metadata.create_all(bind=engine)

db = DatabaseService()
db.create_dataset('y_Train', 'train data', f'storage/datasets/{1}-y_train.parquet')

equpment_names = [
    'ЭКСГАУСТЕР А/М №4',
    'ЭКСГАУСТЕР А/М №5',
    'ЭКСГАУСТЕР А/М №6',
    'ЭКСГАУСТЕР А/М №7',
    'ЭКСГАУСТЕР А/М №8',
    'ЭКСГАУСТЕР А/М №9'
]

node_names = [
    'Ротор',
    'Электродвигатель',
    'Корпус',
    'Подшипник опорно-упорный',
    'Подшипник опорный',
    'Электроаппаратура',
    'Кожух муфты'
]

for equpment_name in equpment_names:
    eq = db.create_equipment(equpment_name, None)
    for node_name in node_names:
        db.create_node(node_name, None, eq)


db.create_model('First model', 'Определяет наличие или отсутствие неисправности М1 на заданных интервалах тестовой выборки (временные ряды сигналов на тесте имеют искусственные пропуски).', 'storage/models/first_model')
db.create_model('Second model', 'Определяет периоды, когда были любые неисправности М3 (аномальный режим работы техместа) на протяжении всего тестового интервала.', 'storage/models/second_model')
db.create_model('Third model', 'Определяет время до простоя М1 с максимально возможным горизонтом - для каждой точки временного ряда тестовой выборки и указать вероятное значение времени до наступления отказа оборудования.', 'storage/models/third_model')
