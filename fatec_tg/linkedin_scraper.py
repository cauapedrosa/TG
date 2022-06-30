from unittest import skip
import instance.driver
from instance.config import config
import psycopg2
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
# from bs4 import UnicodeDammit
from time import sleep
from datetime import date, timedelta
from unicodedata import normalize
import urllib.parse
# import charset_normalizer
import os
import csv
import traceback
# Internals
from vagas_general_data import getJobDate
from Job import Job

linkedin_base = "https://br.linkedin.com/jobs/search?keywords={term}&location=Brasil&geoId=106057199&trk=public_jobs_jobs-search-bar_search-submit&redirect=false&position=1&pageNum=0"
option = webdriver.ChromeOptions()
option.binary_location = instance.driver.binary_location
driver = webdriver.Chrome(instance.driver.driver_location, options=option)


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


def remover_acentos(txt):
    return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')


def cleanUrl(url):
    return url.split('?refId', 1)[0]


def cleanupTitle(txt):
    return txt.replace(',', ' ').replace(';', ' ').replace('|', ' ')


def cleanupDescr(txt):
    txt = txt.split('Exibir mais', 1)
    return txt[0].replace(';', ' ').replace('|', ' ').replace('  ', ' ')


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


def getCourse(courseID):
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("""SELECT * FROM curso WHERE curso_id = %s;""",
                    (courseID, ))
        course = cur.fetchone()
        # print("DEBUG: getCourse", course)
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return course


def getUrlsForAllCourses():
    urls = []
    courses = getCourseList()
    print(f'Getting URLs for All {len(courses)} Courses...')
    for course in courses:
        urls.append(getUrlForCourse(course[0]))
    print(f'Returning {len(urls)} URLs.')
    return urls


def getUrlForCourse(courseID):
    linkedin_base = "https://br.linkedin.com/jobs/search?keywords={term}&location=Brasil&geoId=106057199&trk=public_jobs_jobs-search-bar_search-submit&redirect=false&position=1&pageNum=0"
    course = getCourse(courseID)
    if courseID == 1:
        print(f'Course ({course[0]},{course[1]}) is not a valid course')
    else:
        str = urllib.parse.quote_plus("Estagio " + course[1])
        url = linkedin_base.format(term=str)
        return url


def getJobsFromCourse(courseID):
    if courseID == 1:
        return
    print(f'Getting Jobs From Course({courseID})')
    url = getUrlForCourse(courseID)
    print(f'Subject: {courseID} - {getCourse(courseID)[1]}')
    print(f'\n--> Getting Job List Page\n[{url}]')
    driver.get(url)

    sleep(2)
    #Find the load button and click
    i = 0
    while (i < 3):
        try:
            button = driver.find_element(
                '//*[@id="main-content"]/section[2]/button')
            button.click()
            sleep(2)
            i = i + 1
            print('pinto')
        except:
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            sleep(2)
            i = i + 1
    ## Scrape HTML
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    linkedin_jobs = soup.find_all('a', {'class': 'base-card__full-link'})
    print(f'Found {len(linkedin_jobs)} len(vaga_linkedins).')
    print("--------------------------------")
    print("Entering Extraction Loop: ")
    i = 0
    jobList = []
    for linkedin_job in linkedin_jobs:
        print("--------------------------------")
        i += 1
        print(
            f'Getting Job #{i}/{len(linkedin_jobs)} for Subect {courseID} - {getCourse(courseID)[1]}'
        )
        link = cleanUrl(linkedin_job['href'])
        jobList.append(getJobDetails(link, courseID))
    return jobList


def getJobDetails(url, courseID):
    print(f'Getting Job Details: ')
    try:
        url = cleanUrl(url)
        print(f'\n--> Getting Job Detail Page\n[{url}]')
        driver.get(url)
        sleep(3)

        ## Scrape HTML
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        #
        soup_join_form = soup.findAll("span", {"class": "join-form"})
        if (soup_join_form != []):
            print("\nFOUND SIGNUP FORM\n")
            return 0
        ## Extract job title
        job_linkedin_title = remover_acentos(soup.h1.string.strip())
        ## Extract Description
        container_vaga_desc = soup.findAll(
            "div", {"class": "description__text description__text--rich"})
        text_desc_raw = container_vaga_desc[0].get_text()
        ## Extract Time
        soup_post_time_ago = soup.find("span",
                                       {"class": "posted-time-ago__text"})
        text_post_time_ago = soup_post_time_ago.get_text().strip()
        print(f'\nNow Polishing Job Data')
        job_linkedin_title = cleanupTitle(job_linkedin_title)
        text_desc_clean = cleanupDescr(
            remover_acentos(listToString(text_desc_raw.split())))
        ## Get Job Posting Date
        job_date = getJobDate(text_post_time_ago)
        print(f'## CourseID: {courseID}')
        print(f'## Title: {job_linkedin_title}')
        print(f'## Date : {job_date}')
        # print(f'## Descr: {text_desc_clean}')
        j = Job(url, courseID, job_linkedin_title, text_desc_clean, job_date)
        return j
        # row_list.append(actual_list)
    except IndexError as err:
        print(traceback.format_exception_only)
        print(err.__cause__.__str__)
        print('This means no description was found in page.')
    except Exception as exception:
        traceback.print_exc()
    return


def saveCsv():
    row_list = [["LINK", "TITULO", "DESCR", "MATERIA"]]
    with open('./db/reports/linkedin_formated_data.csv', 'w',
              newline='') as file:
        writer = csv.writer(file, delimiter=';')
        print("--------------------------------")
        print("Writing to file...")
        writer.writerows(row_list)
        print(f'Done! {len(row_list)} jobs added to file')
    file.close()

    return


def saveJobToDB(job):
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO vaga_formatada(URL_format, curso_id, format_titulo, format_desc, postDate) VALUES(%s, %s, %s, %s, %s);""",
            (job.url, job.course_id, job.title, job.desc, job.date))
        conn.commit()
        # print(f'saveJobToDB(): {cur.fetchall()}')
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    print("\n\n##############################")
    print("# Please Run scraper_main.py #")
    print("##############################\n\n")
