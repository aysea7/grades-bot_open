import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials


SAMPLE_SPREADSHEET_ID = "Оцінки 5 семестр"
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
client = gspread.authorize(creds)
spreadsheet = client.open(SAMPLE_SPREADSHEET_ID)

file = open('lists.json', encoding='utf-8')
string = file.read()
students = dict(json.loads(string)['students'][0])
subjects_sheets = dict(json.loads(string)['subjects_sheets'][0])
topics = dict(json.loads(string)['topics'][0])


# adds a grade for a particular subject for a particular test (topic)
async def add(subject_raw, name, topic, grade):
    subject = ""
    for keys, values in subjects_sheets.items():
        if str(subject_raw).lower() in values:
            subject = keys
        else:
            pass
    if subject == "":
        return "Такого предмета не існує."
    user_cell = str(int(list(students.keys())[list(students.values()).index(str(name).lower())]) + 1)
    topic_cell = str(topics.get(str(topic))[0])
    spreadsheet.values_update(range=f"'{subject}'!{topic_cell + user_cell}", params={'valueInputOption': 'USER_ENTERED'}, body={'values': [[grade]]})
    return "Бал успішно додано."


# returns a list of grades and their corresponding percentages (grade/max. grade * 100%) for a specific topic of a specific subject (all students)
async def look(subject_raw, topic):
    subject = ""
    for keys, values in subjects_sheets.items():
        if str(subject_raw).lower() in values:
            subject = keys
        else:
            pass
    if subject == "":
        return "Такого предмета не існує."
    topic_cells = topics.get(str(topic))
    main_topic_cell = topic_cells[0]
    max_topic_cell = topic_cells[1]
    percent_topic_cell = topic_cells[2]
    fetched_grades = spreadsheet.values_get(range=f"'{subject}'!{main_topic_cell}2:{main_topic_cell}13")
    try:
        t = fetched_grades['values']
    except:
        return "За цю тему ще ні в кого немає балів."
    fetched_maximum = spreadsheet.values_get(range=f"'{subject}'!{max_topic_cell}2:{max_topic_cell}13")
    fetched_percent_grades = spreadsheet.values_get(range=f"'{subject}'!{percent_topic_cell}2:{percent_topic_cell}13")
    fetched_student_list = spreadsheet.values_get(range=f"'{subject}'!A2:A13")

    grades_quantity = 0
    for i in fetched_grades['values']:
        grades_quantity += 1
    if grades_quantity < 12:
        to_add = 12 - grades_quantity
        for i in range(to_add):
            fetched_grades['values'].append([])

    grades = f"Дисципліна: <b>{subject}</b>\n" \
             f"Заняття: <b>{topic}</b>\n\n"
    number = 0
    for grade, percent, student in zip(fetched_grades['values'], fetched_percent_grades['values'], fetched_student_list['values']):
        number += 1
        try:
            new_percent = percent[0]
            if str(percent[0]).endswith(',00%'):
                new_percent = str(percent[0])[:-4] + '%'
            grades += f"{number}. {student[0]}:  {grade[0]}/{fetched_maximum['values'][0][0]} <b>({new_percent})</b>\n\n"
        except IndexError:
            grades += f"{number}. <u>{student[0]}</u>\n\n"
    return grades
