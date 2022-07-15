# Internals
from Job import Job
import instance.driver
from instance.config import config
from vagas_general_data import getJobsFrom_VagasG
from vagas_formated_data import getJobsFromCourseID_VagasF
from linkedin_scraper import getUrlForCourse, getCourseList, getJobsFromUrl_Linkedin, getUrlForGeneralJobs, getUrlsForAllCourses
# Externals
import time
import traceback
from typing import final
import psycopg2
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

# Specify chrome locations
ser = Service(instance.driver.driver_location)
# Add options
opt = webdriver.ChromeOptions()
opt.binary_location = instance.driver.binary_location
driver = webdriver.Chrome(service=ser, options=opt)


def saveJobGeneral(job):
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO vaga_geral(URL, curso_id, titulo, descr, empresa, postDate, locale) VALUES(%s, %s, %s, %s, %s, %s, %s)""",
            (job.url, job.title, job.course_id, job.desc, job.date, job.locale))
        conn.commit()
        cur.close()
        print(f'Job {job.title} saved to vaga_geral!')
    except psycopg2.DatabaseError as error:
        print(f'Error: {error}')
    except Exception as error:
        traceback.print_exc()
    finally:
        if conn is not None:
            conn.close()


def saveJobFormatted(job):
    conn = None
    try:
        print(f'-> Inserting "{job.title}" into vaga_formatada')
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO vaga_formatada(URL, curso_id, titulo, descr, empresa, postDate, locale) VALUES(%s, %s, %s, %s, %s, %s, %s);""",
            (job.url, job.course_id, job.title, job.desc, job.poster, job.date, job.locale))
        conn.commit()
        cur.close()
        # print("Job saved to vaga_formatada with no exceptions!")
    except psycopg2.DatabaseError as error:
        print(f'Error: {error}')
    except Exception as error:
        traceback.print_exc()
    finally:
        if conn is not None:
            # print(f'Closing connection to database')
            conn.close()


def menu_main():
    print("\n#############################################")
    print("########  Starting scraper_main.py  #########")
    print("#############################################")
    print("####  Select an Option:             #########")
    print("# 0: Exit                                   #")
    print("# 1: Scrape Linkedin.com                    #")
    print("# 2: Scrape Vagas.com.br                    #")
    print("#############################################")
    print("Selecting: ", end=" ")
    try:
        flag = int(input())
    except Exception as err:
        print("Please type a Number")
    if flag == 0:
        return flag
    elif flag == 1:
        return menu_linkedin()
    elif flag == 2:
        return menu_vagas()
    return flag


def menu_linkedin():
    print("# 1: Scrape Linkedin for All Courses")
    print("# 2: Scrape Linkedin for Specific Course ID")
    print("# 3: Scrape Linkedin for Unclassified Jobs")
    print("Selecting: ", end=" ")
    try:
        flag = int(input())
    except Exception as err:
        print("Please type a Number")
    return flag


def menu_vagas():
    print("# 4: Scrape Vagas for All Courses")
    print("# 5: Scrape Vagas for Specific Course ID")
    print("# 6: Scrape Vagas for Unclassified Jobs")
    print("Selecting: ", end=" ")
    try:
        flag = int(input())
    except Exception as err:
        print("Please type a Number")
    return flag


def main():
    flag = menu_main()
    while (flag > 0):
        # 1: Scrape Linkedin for All Courses
        if flag == 1:
            print("You selected: Scrape Linkedin for All Courses")
            try:
                start = time.perf_counter()
                courseList = getCourseList()
                for course_id in courseList:
                    if course_id[0] == 1:
                        print("Course 1 is not a valid course")
                    else:
                        url = getUrlForCourse(course_id[0])
                        jobs = getJobsFromUrl_Linkedin(
                            driver, url, course_id[0])
                        for job in jobs:
                            saveJobFormatted(job)
            except Exception as exception:
                traceback.print_exc()
                continue
            finally:
                end = time.perf_counter()
                print(f'\nFinished in {round(end - start, 2)} seconds\n\n')
                flag = 0

        # 2: Scrape Linkedin for Specific Course ID
        elif flag == 2:
            print("You selected: Scrape Linkedin for Specific Course ID")
            try:
                print(f'Select the course you wish to Scrape from the list:')
                printCourseList()
                course_id = int(input())
                start = time.perf_counter()
                url = getUrlForCourse(course_id)
                jobs = getJobsFromUrl_Linkedin(driver, url, course_id)
                print(f'\nFound {len(jobs)} jobs for Course ID {course_id} !')
                print(f'\nSaving jobs to database...')
                counter = 0
                for job in jobs:
                    counter += 1
                    print(f'{counter}/{len(jobs)} = {job}')
                    saveJobFormatted(job)
            except Exception as exception:
                traceback.print_exc()
                continue
            finally:
                end = time.perf_counter()
                print(f'\nFinished in {round(end - start, 2)} seconds\n\n')

        # 3: Scrape Linkedin for Unclassified Jobs
        elif flag == 3:
            print("You selected: Scrape Linkedin for Unclassified Jobs")
            try:
                start = time.perf_counter()
                url = getUrlForGeneralJobs()
                jobs = getJobsFromUrl_Linkedin(driver, url, 1)
                for job in jobs:
                    print(f'Saving job {job.title} to database...')
                    saveJobGeneral(job)
            except Exception as exception:
                traceback.print_exc()
                continue
            finally:
                end = time.perf_counter()
                print(f'\nFinished in {round(end - start, 2)} seconds\n\n')
                flag = 0

        # 4: Scrape Vagas for All Courses
        elif flag == 4:
            print("You selected: Scrape Vagas for All Courses")
            try:
                start = time.perf_counter()
                courseList = getCourseList()
                for course_id in courseList:
                    if course_id[0] == 1:
                        print("Course 1 is not a valid course")
                    else:
                        jobs = getJobsFromCourseID_VagasF(driver, course_id[0])
                        print(
                            f'\nFound {len(jobs)} jobs for Course ID {course_id} !')
                        print(f'\nSaving jobs to database...')
                        for job in jobs:
                            saveJobFormatted(job)
            except Exception as exception:
                traceback.print_exc()
                continue
            finally:
                end = time.perf_counter()
                print(f'\nFinished in {round(end - start, 2)} seconds\n\n')
                flag = 0

        # 5: Scrape Vagas for Specific Course ID
        elif flag == 5:
            print("You selected: Scrape Vagas for Specific Course ID")
            try:
                start = time.perf_counter()
                print(f'Select the course you wish to Scrape from the list:')
                printCourseList()
                course_id = int(input())
                jobs = getJobsFromCourseID_VagasF(driver, course_id)
                print(f'Found {len(jobs)} jobs ! Now saving...')
                for job in jobs:
                    # saveJobFormatted(job)
                    print(f'Would now save job {job}')
            except Exception as exception:
                traceback.print_exc()
                break
            finally:
                end = time.perf_counter()
                print(f'\nFinished in {round(end - start, 2)} seconds\n\n')
                flag = 0

        # 6: Scrape Vagas for Unclassified Jobs
        elif flag == 6:
            print("You selected: Scrape Vagas for Unclassified Jobs")
            try:
                start = time.perf_counter()
                jobs = getJobsFrom_VagasG(driver)
                for job in jobs:
                    saveJobGeneral(job)
            except Exception as exception:
                traceback.print_exc()
                continue
            finally:
                end = time.perf_counter()
                print(f'\nFinished in {round(end - start, 2)} seconds\n\n')
                flag = 0


def printCourseList():
    for course in getCourseList():
        print(f'{course[0]} - {course[1]}')


if __name__ == "__main__":
    main()
