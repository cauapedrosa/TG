from datetime import date, timedelta
from time import sleep
from unicodedata import normalize
import psycopg2
from instance.config import config


def scroll(driver):
    scroll_pause_time = 3
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to bottom
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load page
        sleep(scroll_pause_time)
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # If heights are the same it will exit the function
            break
        last_height = new_height


def listToString(s):
    # initialize an empty string
    str1 = " "

    # traverse in the string
    for ele in s:
        ele = ele.replace('\n',
                          ' ').replace('\xa0',
                                       ' ').replace(',',
                                                    ' | ').replace(';', ' | ')
        str1 = str1 + ' ' + ele + ' '

    # return string
    return str1


def trimUrlVagas(url):
    return url.split('?', 1)[0]


def trimUrlAtRefid(url):
    return url.split('?refId', 1)[0]


def cleanup(txt):
    txt = normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')
    txt = txt.replace(',', ' ').replace(';', ' ').replace('|', ' ')
    return txt.strip()


def cleanupDescr_Linkedin(txt):
    txt = txt.split('Exibir mais', 1)
    return txt[0].replace(';', ' ').replace('|', ' ')


def getCourseList():
    courseList = []
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("""SELECT * FROM curso;""")
        courseList = cur.fetchall()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    # print(f'getCourseList(): {courseList}')
    return courseList


def getCourse(course_id):
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("""SELECT * FROM curso WHERE curso_id = %s;""",
                    (course_id, ))
        course = cur.fetchone()
        # print("DEBUG: getCourse", course)
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f'Error in getCourse({course_id}):\n{error}')
    finally:
        if conn is not None:
            conn.close()
    return course


def getJobDate(text_date):
    text_date.strip("Publicada")
    today = date.today()
    # job_date = today.strftime("%Y/%m/%d")
    delta = timedelta(0)
    if text_date == "Hoje":
        delta = timedelta(0)
    elif text_date == "Ontem":
        delta = timedelta(days=1)
    elif text_date == "H?? 2 dias":
        delta = timedelta(days=2)
    elif text_date == "H?? 3 dias":
        delta = timedelta(days=3)
    elif text_date == "H?? 4 dias":
        delta = timedelta(days=4)
    elif text_date == "H?? 5 dias":
        delta = timedelta(days=5)
    elif text_date == "H?? 6 dias":
        delta = timedelta(days=6)
    elif text_date == "H?? 7 dias":
        delta = timedelta(days=7)
    elif text_date == "H?? 1 semana":
        delta = timedelta(weeks=1)
    elif text_date == "H?? 2 semanas":
        delta = timedelta(weeks=2)
    elif text_date == "H?? 3 semanas":
        delta = timedelta(weeks=3)
    elif text_date == "H?? 1 m??s":
        delta = timedelta(days=30)
    job_date = (today - delta)
    # print(f'getVagaDate({text_date} [d:{delta}]: {job_date})')
    return job_date
