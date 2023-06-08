import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle, \
    PageTemplate
# from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.platypus import *
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.units import inch
# from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

import random
import argparse
import pandas as pd
import duckdb
import os
from matplotlib import pyplot as plt


START_DATE = '2022-02-05 00:00:00'
END_DATE = '2022-02-06 00:00:00'
PATH_DIR_DATA_RAW = '../../data/raw'
PATH_DIR_DATA_RESULTS = '../../data/submissions'

parser = argparse.ArgumentParser()
parser.add_argument('-id', '--input-data', nargs=1, dest='PATH_DIR_DATA_RAW', required=False, default=PATH_DIR_DATA_RAW,
                    help=f'''Полный путь к директории c данными, по умолчанию {PATH_DIR_DATA_RAW}. 
                    ''')
parser.add_argument('-ir', '--input-results', nargs=1, dest='PATH_DIR_DATA_RESULTS', required=False, default=PATH_DIR_DATA_RESULTS,
                    help=f'''Полный путь к директории с прогнозами, по умолчанию {PATH_DIR_DATA_RESULTS}. 
                    ''')
parser.add_argument('-sd', '--startdate', nargs=1, dest='START_DATE', required=False, default=START_DATE,
                    help='''Интересуемое время начала. Вводится в формате 'YYYY-mm-dd HH:MM:SS', например, '2022-02-05 00:00:00'. 
                    Не забудьте нижнее подчеркивание между датой и временем. Архив должен содержать введенную дату. 
                    Необязательный параметр''')
parser.add_argument('-ed', '--enddate', nargs=1, dest='END_DATE', required=False, default=END_DATE,
                    help='''Интересуемое время окончания. Вводится в формате 'YYYY-mm-dd HH:MM:SS', например, '2022-02-06 00:00:00'. 
                    ''')
parse = parser.parse_args()
params = vars(parse)

START_DATE = params['START_DATE'][0]
END_DATE = params['END_DATE'][0]
PATH_DIR_DATA_RAW = params['PATH_DIR_DATA_RAW']
PATH_DIR_DATA_RESULTS = params['PATH_DIR_DATA_RESULTS']

print(START_DATE, END_DATE, PATH_DIR_DATA_RAW, PATH_DIR_DATA_RESULTS)


# Загрузка данных
X_test_path = os.path.join(PATH_DIR_DATA_RAW, 'X_test.parquet')
y_m3_path = os.path.join(PATH_DIR_DATA_RESULTS, 'submission_2.parquet')
y_rul_path = os.path.join(PATH_DIR_DATA_RESULTS, 'submission_3.parquet')

query_telemetry = f"""
SELECT * FROM '{X_test_path}'
WHERE DT >= '{START_DATE}' AND DT <= '{END_DATE}';
"""
query_m3 = f"""
SET memory_limit='15GB';
SELECT * FROM '{y_m3_path}'
WHERE DT >= '{START_DATE}' AND DT <= '{END_DATE}';
"""
query_rul = f"""
SET memory_limit='15GB';
SELECT * FROM '{y_rul_path}'
WHERE DT >= '{START_DATE}' AND DT <= '{END_DATE}';
"""
telemetry = duckdb.sql(query_telemetry).df()
y_m3 = duckdb.sql(query_m3).df()
y_rul = duckdb.sql(query_rul).df()
print(telemetry.shape, y_m3.shape, y_rul.shape)


# Стили для pdf

pdfmetrics.registerFont(TTFont('DejaVuSerif','DejaVuSerif.ttf', 'UTF-8'))
styles = getSampleStyleSheet() # дефолтовые стили
# the magic is here
styles['Normal'].fontName='DejaVuSerif'
styles['Heading1'].fontName='DejaVuSerif'


centered = ParagraphStyle(fontName='DejaVuSerif', name='centered',
                          fontSize=20,
                          leading=16,
                          alignment=1,
                          spaceAfter=10)

sub_centered = ParagraphStyle(fontName='DejaVuSerif', name='centered1',
                              fontSize=16,
                              leading=16,
                              alignment=1,
                              spaceAfter=10)

date_centered = ParagraphStyle(fontName='DejaVuSerif', name='centered2',
                               fontSize=24,
                               leading=16,
                               alignment=1,
                               spaceAfter=10)

pic_centered = ParagraphStyle(fontName='DejaVuSerif', name='centered3',
                              fontSize=12,
                              leading=16,
                              alignment=1,
                              spaceAfter=20)

pic_centered_vert = ParagraphStyle(fontName='DejaVuSerif', name='centered4',
                                   fontSize=12,
                                   leading=16,
                                   alignment=1,
                                   spaceBefore=20,
                                   spaceAfter=20)

table_head = ParagraphStyle(fontName='DejaVuSerif', name='table',
                            fontSize=12,
                            leading=16,
                            spaceAfter=20)

bold_centered = ParagraphStyle(fontName='DejaVuSerif', name='centered4',
                               fontSize=14,
                               leading=16,
                               alignment=1,
                               spaceAfter=20)

paragraph = ParagraphStyle(
    'default',
    fontName='DejaVuSerif',
    fontSize=12,
    leading=12,
    leftIndent=0,
    rightIndent=0,
    firstLineIndent=4,
    # alignment=TA_LEFT,
    spaceBefore=0,
    spaceAfter=0,
    # bulletFontName='Times-Roman',
    # bulletFontSize=10,
    # bulletIndent=0,
    # textColor= black,
    # backColor=None,
    # wordWrap=None,
    # borderWidth= 0,
    # borderPadding= 0,
    # borderColor= None,
    # borderRadius= None,
    # allowWidows= 1,
    # allowOrphans= 0,
    # textTransform=None,  # 'uppercase' | 'lowercase' | None
    # endDots=None,
    # splitLongWords=1,
)

section = ParagraphStyle(fontName='DejaVuSerif', name='section',
                         fontSize=18,
                         leading=16,
                         # alignment=1,
                         spaceAfter=20,
                         spaceBefore=0,
                         firstLineIndent=40,
                         )

def addPageNumber(canvas, doc):
    """
    Add the page number
    """
    page_num = canvas.getPageNumber()
    text = "{}".format(page_num)
    canvas.drawCentredString(doc.pagesize[0] / 2, 10 * mm, text)

def plot_telemetry(telemetry, exh_number):
    
    exh_name = f'ЭКСГАУСТЕР {exh_number}'
    exh_cols = [s for s in telemetry.columns if exh_name in s]
    current_cols = [s for s in exh_cols if 'ТОК' in s]
    temp_cols = [s for s in exh_cols if 'ТЕМПЕРАТУРА' in s]
    vibr_cols = [s for s in exh_cols if 'ВИБРАЦИЯ' in s]
    
    fig, ax = plt.subplots(figsize=(18,3))
    telemetry.set_index('DT')[vibr_cols].rolling('1T').mean().plot(ax=ax)
    fig.savefig(f'figs/{exh_number}_vibr.png')
    
    fig, ax = plt.subplots(figsize=(18,3))
    telemetry.set_index('DT')[temp_cols].rolling('1T').mean().plot(ax=ax)
    fig.savefig(f'figs/{exh_number}_temp.png')

    fig, ax = plt.subplots(figsize=(18,3))
    telemetry.set_index('DT')[current_cols].rolling('1T').mean().plot(ax=ax)
    fig.savefig(f'figs/{exh_number}_current.png')

    fig, ax = plt.subplots(figsize=(18,3))
    telemetry.set_index('DT')[[f'ЭКСГАУСТЕР {exh_number}. ДАВЛЕНИЕ МАСЛА В СИСТЕМЕ',]].rolling('1T').mean().plot(ax=ax)
    plt.legend()
    fig.savefig(f'figs/{exh_number}_oil_pr.png')
    plt.close()

def plot_m3(exh_number, y_m3):

    mask = y_m3[y_m3!=0].sum(axis=0, numeric_only=True)>0
    m3_malf = y_m3[y_m3!=0].sum(axis=0, numeric_only=True)[mask]
    cols = m3_malf.index.to_list()
    ccols = [s for s in cols if f'№{exh_number}' in s]
    if len(ccols) > 0:
        fig, ax = plt.subplots(figsize=(18,3))
        y_m3.set_index('DT')[ccols].plot(ax=ax)
        plt.legend()
        fig.savefig(f'figs/{exh_number}_m3.png')
        plt.close()

def plot_rul(exh_number, y_rul):
    mask = y_rul[y_rul!=2592000].sum(axis=0, numeric_only=True)>0
    rul_malf = y_rul[y_rul!=2592000].sum(axis=0, numeric_only=True)[mask]
    cols = rul_malf.index.to_list()
    ccols = [s for s in cols if f'№{exh_number}' in s]
    if len(ccols) > 0:
        fig, ax = plt.subplots(figsize=(18,3))
        (y_rul.set_index('DT')[ccols]/60/60/24).plot(ax=ax)
        plt.legend()
        plt.ylabel('Осталось дней до неисправности')
        fig.savefig(f'figs/{exh_number}_rul.png')
        plt.close()
        y_rul.set_index('DT')[ccols].plot()

    

def generate_exh_page(exh_number, telemetry, y_m3, y_rul):
    plot_telemetry(telemetry, exh_number)
    plot_m3(exh_number, y_m3)
    plot_rul(exh_number, y_rul)

    Story = []
    exh_name = f'ЭКСГАУСТЕР {exh_number}'
    Story.append(Paragraph(exh_name, centered))
    # Story.append(Spacer(1, 12))

    def _add_image(path):
        im1 = Image(path, width=18 * cm, height=3 * cm)
        im1.hAlign = 'CENTER'
        return im1
    # Графики телеметрии
    Story.append(_add_image(f'figs/{exh_number}_vibr.png'))
    Story.append(_add_image(f'figs/{exh_number}_temp.png'))
    Story.append(_add_image(f'figs/{exh_number}_current.png'))
    Story.append(_add_image(f'figs/{exh_number}_oil_pr.png'))

    Story.append(Paragraph('Неисправности M1', sub_centered))
    # Story.append(Spacer(1, 4))
    if os.path.exists(f'figs/{exh_number}_rul.png'):
        Story.append(_add_image(f'figs/{exh_number}_rul.png'))
    else:
        Story.append(Paragraph('Неисправности типа М1 на горизонте 30 дней не обнаружены', paragraph))

    Story.append(Paragraph('Неисправности M3', sub_centered))
    # Story.append(Spacer(1, 4))
    if os.path.exists(f'figs/{exh_number}_m3.png'):
        Story.append(_add_image(f'figs/{exh_number}_m3.png'))
    else:
        Story.append(Paragraph('Неисправностей типа M3 не обнаружено', paragraph))

    Story.append(PageBreak())
    return Story


sd = START_DATE.replace(' ', '_')
ed = END_DATE.replace(' ', '_')
doc = SimpleDocTemplate(f"reports/report__{sd}__{ed}.pdf",pagesize=A4,
                        rightMargin=72,leftMargin=72,
                        topMargin=72,bottomMargin=18)


Story=[]

# Титульная страница

Story.append(Spacer(1, 150))
Story.append(Paragraph('Отчет', centered))
Story.append(Paragraph('Техническое состояние эксгаустеров', centered))
Story.append(Spacer(1, 12))
Story.append(Paragraph(f'за период {START_DATE} - {END_DATE}', pic_centered))

Story.append(Spacer(1, 400))

formatted_time = datetime.datetime.now().strftime("%d.%m.%Y")
date_string = f"Дата генерации отчета: {formatted_time}"
Story.append(Paragraph(date_string, paragraph))
Story.append(PageBreak())

# Страницы эксгаустеров
for exh_number in range(4, 10):
    Story.extend(generate_exh_page(exh_number, telemetry, y_m3, y_rul))

doc.build(Story, onLaterPages=addPageNumber)
