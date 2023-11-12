import json

from PIL import Image
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# load all the lists from the JSON file
file = open('lists.json', encoding='utf-8')
string = file.read()
students = dict(json.loads(string)['students'][0])
students_id = dict(json.loads(string)['students_id'][0])
subjects_eqx = dict(json.loads(string)['subjects_eqx'][0])


# create one webdriver per student
class Drivers:
    op = webdriver.ChromeOptions()
    op.add_argument('headless')
    driver1 = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=op)
    driver1.set_window_size(1536, 864)
    driver2 = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=op)
    driver2.set_window_size(1536, 864)
    driver3 = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=op)
    driver3.set_window_size(1536, 864)
    driver4 = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=op)
    driver4.set_window_size(1536, 864)
    driver5 = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=op)
    driver5.set_window_size(1536, 864)
    driver6 = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=op)
    driver6.set_window_size(1536, 864)
    driver7 = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=op)
    driver7.set_window_size(1536, 864)
    driver8 = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=op)
    driver8.set_window_size(1536, 864)
    driver9 = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=op)
    driver9.set_window_size(1536, 864)
    driver10 = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=op)
    driver10.set_window_size(1536, 864)
    driver11 = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=op)
    driver11.set_window_size(1536, 864)
    driver12 = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=op)
    driver12.set_window_size(1536, 864)

    def all_drivers(self):
        return self.driver1, self.driver2, self.driver3, self.driver4, self.driver5, self.driver6, \
               self.driver7, self.driver8, self.driver9, self.driver10, self.driver11, self.driver12


drivers = Drivers()


# select a webdriver for a specific student
async def choose_driver(user_id):
    user = int(list(students_id.keys())[list(students_id.values()).index(str(user_id))])
    if user == 1:
        return drivers.driver1
    elif user == 2:
        return drivers.driver2
    elif user == 3:
        return drivers.driver3
    elif user == 4:
        return drivers.driver4
    elif user == 5:
        return drivers.driver5
    elif user == 6:
        return drivers.driver6
    elif user == 7:
        return drivers.driver7
    elif user == 8:
        return drivers.driver8
    elif user == 9:
        return drivers.driver9
    elif user == 10:
        return drivers.driver10
    elif user == 11:
        return drivers.driver11
    elif user == 12:
        return drivers.driver12


# get a cropped captcha from the uni's website with grades (EQX)
async def get_captcha(user_id):
    driver = await choose_driver(user_id)
    driver.get('http://eqx.meduniv.lviv.ua/student/')
    driver.save_screenshot(f"./captcha-{driver.session_id}.png")
    image_obj = Image.open(f"./captcha-{driver.session_id}.png")
    captcha = image_obj.crop((728, 578, 827, 615))
    captcha.save(f"./captcha-{driver.session_id}.png")
    return f"./captcha-{driver.session_id}.png"


# fill out the form and send a request to get the access to a grade book
async def process_captcha(user_id, subject, captcha):
    subject_key = ""
    for keys, values in subjects_eqx.items():
        if subject in values:
            subject_key = keys
        else:
            pass
    try:
        driver = await choose_driver(user_id)
        driver.find_element(By.NAME, 'group').send_keys('su_m03_2026')
        driver.find_element(By.NAME, 'department').send_keys(subject_key)
        driver.find_element(By.NAME, 'semestr').send_keys('4')
        driver.find_element(By.NAME, 'year').send_keys('2021/2022')
        driver.find_element(By.NAME, 'norobot').send_keys(captcha)
        driver.find_element(By.NAME, 'submit').submit()
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'marksize')))
        except TimeoutException:
            return False
    except:
        return False


# get the grades from the gradebook
async def get_grades(user_id, name):
    driver = await choose_driver(user_id)
    user = int(list(students.keys())[list(students.values()).index(str(name).lower())])
    try:
        fetched = driver.find_element(By.XPATH, f'//table[@class="marksize"]/tbody/tr[{user + 1}]')
        fetched_subject = driver.find_element(By.XPATH,
                                              '//div[@name="journal_info"]/fieldset/table/tbody/tr[3]/td[2]').text
    except NoSuchElementException:
        return "Неправильно вказаний предмет."
    zan = 0
    grades = f"Дисципліна: <b>{fetched_subject}</b>\n\n"
    for row in fetched.text.splitlines():
        if ". " in row:
            whitelist = set("АаБбВвГгҐґДдЕеЄєЖжЗзИиІіЇїЙйКкЛлМмНнОоПпРрСсТтУуФфХхЦцЧчШшЩщьЮюЯя '`")
            new = ''.join(filter(whitelist.__contains__, row))
            grades += new.lstrip() + "\n"
        else:
            zan += 1
            grades += f"\nЗаняття {zan}:  <b>{row}</b>"
    return grades
