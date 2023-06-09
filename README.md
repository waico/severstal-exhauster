# severstal-exhauster

В репозитории содержится исходный код построения моделей машинного обучения и прототипа системы предиктивной аналитики.

Модели машинного обучения разработаны по трем задачам:

1. Определить наличие или отсутствие неисправности М1 на заданных интервалах тестовой выборки (временные ряды сигналов на тесте имеют искусственные пропуски).
2. Определять периоды, когда были любые неисправности М3 (аномальный режим работы техместа) на протяжении всего тестового интервала.
3. Определить время до простоя М1 с максимально возможным горизонтом - для каждой точки временного ряда тестовой выборки и указать вероятное значение времени до наступления отказа оборудования.

__Результаты прогнозов на приватной выборке по задачам доступны по ссылкам__:
-  [Задача 1](https://disk.yandex.com/i/FrliIthuhIxgMw)
-  [Задача 2](https://cloud.mail.ru/public/xNtu/Rz94iFcyd)
-  [Задача 3](https://drive.google.com/file/d/1RxTsrN7vPmGlcBILJBOIOlbwZk61_Svu/view)

-  [Задача 1 Переразмеченный М1](/data/submissions//Processed_toir2.xlsx)

## Структура Репозитория

```
.
├── README.md # Этот файл
├── app # Директория приложения визуализации и тестирования моделей
├── data # Директория для хранения данных
├── docs # Документация проекта
├── figs # Графики и изображения, используемые в проекте
├── models # Обученные модели и скрипты для их обучения
└── notebooks # Jupyter notebooks для визуализации и прототипирования
```

## Воспроизводимость построения моделей

Для повторения экспериментов по построению моделей поместите в директорию `data/raw` исходные данные:

```
data/raw
├── X_test.parquet
├── X_train.parquet
├── messages.xlsx
├── sample_submission_2.parquet
├── sample_submission_3.parquet
├── test_intervals.xlsx
└── y_train.parquet
```
### Задача 1 (Обнаружение M1)

В ноутбуках `notebooks/Task1Step1ProcessData.ipynb`, `notebooks/Task1Step2EDA.ipynb` и `notebooks/Task1Step4Solution.ipynb` содержится код разведочного анализа данных и проведения экспериментов по очистке данных, генерации признаков, подбору моделей машиного обучения и их оценке.
В ноутбуке `notebooks/Task1Step4Solution.ipynb` подготавливается прогноз по приватной чатсти датасета.

### Задача 2 (Обнаружение M3)

1. Запустите файл `notebooks/Task2Step1PrepareData.ipynb` для переразметки данных. В результате создастся новый файл с разметкой M3 неисправностей - `data/processed/y_train_fixed_M3.parquet`.

2. Запустите скрипт обучения моделей - `notebooks/Task2Step2Model.py`. В нем происходит генерация признаков, разбиене выборки, обучение моделей, оценка их качества, визуализация прогнозов и сериализация моделей в директорию `models/task2`. Обученные модели доступны по [ссылке](https://cloud.mail.ru/public/viwd/7TtLJ4bcS).

3. Для получения прогнозов на приватном датасете `X_test.parquet` запустите скрипт `notebooks/Task2Step3Inference.ipynb`. В результате сформируется файл `/data/submissions/submission_2.parquet`, который содержит прогноз наступления M3.

### Задача 3 (Оставшееся время до М1)
В ноутбуке `notebooks/Task3AllSteps.ipynb` содержится код исследований данных в разрезе 3ей задачи. В этом же файле содержатся результаты предварительной обработки данных и проверки различных гипотез о подходах к решению задачи. В этом же ноутбуке обучаются модели и готовится прогноз для приватной части лидерборда.

Файл с сабмишеном доступен по [ссылке](https://drive.google.com/file/d/1RxTsrN7vPmGlcBILJBOIOlbwZk61_Svu/view?usp=share_link).

## Описание решений
Для запуска полного решения перейдите в термина в каталог `solution` и выполните команду:
```
docker-compose up -d
```
Команда соберет и запустит севрер MLFlow с собственной БД PostgreSQL, сервис мониторинга моделей и БД Promitius, а также Grafana для визуализации мониторинга.

## Описание приложения
Прототип приложения разработан на FastAPI и Vue.js для применения моделей, сериализованных MLFlow. Модели можно использовать вне приложения, например, в виде контейнера MLFlow или оператора K8S. В приложении намеренно не используется перекладывание данный в локальную БД, а работа с наборами данных `parquet` напряму с помощью библиотеки `duckdb` для возможной работы и через S3 хранилища.
Вы можете загрузить набор данных в прилоежение и применить к нему каждую их трех разработанных моделей для получения результатов.

### Запуск приложения

Для запуска приложения перейдите в директорию `app` и установите зависимости командой:
```
pip install -r requirements.txt
```

Выполните скрипт инициализации, чтобы создать БД и наполнить ее начальными значениями, загрузить наборы данных и создать подготовленные модели:
```
python init.py
```

Запустите веб-сервер. Приложение будет доступно по адресу: `http://127.0.0.1:8000`
```
uvicorn main:app --reload
```
