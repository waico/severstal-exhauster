# Генератор отчетов в формате pdf

```
usage: report.py [-h] [-id PATH_DIR_DATA_RAW] [-ir PATH_DIR_DATA_RESULTS] [-sd START_DATE] [-ed END_DATE]

optional arguments:
  -h, --help            show this help message and exit
  -id PATH_DIR_DATA_RAW, --input-data PATH_DIR_DATA_RAW
                        Полный путь к директории c данными, по умолчанию ../../data/raw.
  -ir PATH_DIR_DATA_RESULTS, --input-results PATH_DIR_DATA_RESULTS
                        Полный путь к директории с прогнозами, по умолчанию ../../data/submissions.
  -sd START_DATE, --startdate START_DATE
                        Интересуемое время начала. Вводится в формате 'YYYY-mm-dd HH:MM:SS', например, '2022-02-05 00:00:00'. Не забудьте
                        нижнее подчеркивание между датой и временем. Архив должен содержать введенную дату. Необязательный параметр
  -ed END_DATE, --enddate END_DATE
                        Интересуемое время окончания. Вводится в формате 'YYYY-mm-dd HH:MM:SS', например, '2022-02-06 00:00:00'.
```

Отчеты генерируются в поддиректорию `reports`.