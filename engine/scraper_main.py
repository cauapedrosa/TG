# Internals
from Job import Job
import instance.driver
from instance.config import config
import vagas_scraper as Vagas
import infojobs_scraper as Infojobs
import linkedin_scraper as Linkedin
from scraper_aux import *
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
# Print Stopwords
# print(f'\nStopwords: {getStopwords()}\n')


def saveJob(table, job):
    conn = None
    try:
        print(f'> Inserting into {table}')
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        if table == 'vaga_formatada':
            cur.execute("""INSERT INTO vaga_formatada (URL, curso_id, titulo, descr, empresa, postDate, locale) VALUES(%s, %s, %s, %s, %s, %s, %s)""",
                        (job.url, job.course_id, job.title, job.desc, job.poster, job.date, job.locale))
        else:
            cur.execute("""INSERT INTO vaga_geral (URL, curso_id, titulo, descr, empresa, postDate, locale) VALUES(%s, %s, %s, %s, %s, %s, %s)""",
                        (job.url, job.course_id, job.title, job.desc, job.poster, job.date, job.locale))
        conn.commit()
        cur.close()
        print(f'✅Success! Saved into {table}: {job.title}')
    except psycopg2.DatabaseError as error:
        print(f'⚠️Job {job}\nRaised Error: {error}')
    except Exception as error:
        print(f'⚠️Job {job}\nRaised Error: {error}')
        traceback.print_exc()
    finally:
        if conn is not None:
            conn.close()


def menu_main():
    print("\n\n#######################################################################")
    print("#     _____                                 __  ___      _            #")
    print("#    / ___/______________ _____  ___  _____/  |/  /___ _(_)___        #")
    print("#    \__ \/ ___/ ___/ __ `/ __ \/ _ \/ ___/ /|_/ / __ `/ / __ \       #")
    print("#   ___/ / /__/ /  / /_/ / /_/ /  __/ /  / /  / / /_/ / / / / /       #")
    print("#  /____/\___/_/   \__,_/ .___/\___/_/  /_/  /_/\__,_/_/_/ /_/        #")
    print("#                      /_/                                            #")
    print("#######################################################################")
    print("####  Select an Option:                                       #########")
    print("## 0: Exit                                                           ##")
    print("## 1: Scrape Linkedin for All Courses                                ##")
    print("## 2: Scrape Linkedin for Specific Course ID                         ##")
    print("## 3: Scrape Linkedin for Unclassified Jobs                          ##")
    print("## 4: Scrape Vagas for All Courses                                   ##")
    print("## 5: Scrape Vagas for Specific Course ID                            ##")
    print("## 6: Scrape Vagas for Unclassified Jobs                             ##")
    print("## 7: Scrape InfoJobs for All Courses                                ##")
    print("## 8: Scrape InfoJobs for Specific Course ID                         ##")
    print("## 9: Scrape InfoJobs for Unclassified Jobs                          ##")
    print("## 10: Scrape All Platforms for Specific Course ID                   ##")
    print("#######################################################################")
    print("Selecting: ", end=" ")
    try:
        flag = int(input())
    except Exception as err:
        err.print_exc()
        print("Please type a Number")
    return flag


def main():
    flag = menu_main()
    while (flag > 0):
        # 1: Scrape Linkedin for All Courses
        if flag == 1:
            print("You selected: Scrape Linkedin for All Courses")
            try:
                courseList = getCourseList()
                for course in courseList:
                    course_id = course[0]
                    if course_id == 1:
                        print(f"Skipping Course {course_id} - {course[1]}")
                    else:
                        scrape_Linkedin(driver, course_id, 'vaga_formatada')
            except Exception as exception:
                traceback.print_exc()
                continue
            finally:
                flag = menu_main()

        # 2: Scrape Linkedin for Specific Course ID
        elif flag == 2:
            print("You selected: Scrape Linkedin for Specific Course ID")
            try:
                print(f'Select the course you wish to Scrape from the list:')
                printCourseList()
                course = int(input())
                scrape_Linkedin(driver, course, 'vaga_formatada')
            except Exception as exception:
                traceback.print_exc()
                continue
            finally:
                flag = 2

        # 3: Scrape Linkedin for Unclassified Jobs
        elif flag == 3:
            print("You selected: Scrape Linkedin for Unclassified Jobs")
            try:
                scrape_Linkedin(driver, 1, 'vaga_geral')
            except Exception:
                traceback.print_exc()
                continue
            finally:
                # end = time.perf_counter()
                # print(f'\nFinished in {round(end - start, 2)} seconds\n\n')
                flag = menu_main()

        # 4: Scrape Vagas for All Courses
        elif flag == 4:
            print("You selected: Scrape Vagas for All Courses")
            try:
                start = time.perf_counter()
                courseList = getCourseList()
                for course in courseList:
                    course_id = course[0]
                    if course_id == 1:
                        print("Course 1 is not a valid course")
                    else:
                        scrape_Vagas(driver, course_id, 'vaga_formatada')
            except Exception as exception:
                traceback.print_exc()
                continue
            finally:
                end = time.perf_counter()
                print(f'\nFinished in {round(end - start, 2)} seconds\n\n')
                flag = menu_main()

        # 5: Scrape Vagas for Specific Course ID
        elif flag == 5:
            print("You selected: Scrape Vagas for Specific Course ID")
            try:
                start = time.perf_counter()
                print(f'Select the course you wish to Scrape from the list:')
                printCourseList()
                course = int(input())
                scrape_Vagas(driver, course, 'vaga_formatada')
            except Exception as exception:
                traceback.print_exc()
                break
            finally:
                end = time.perf_counter()
                print(f'\nFinished in {round(end - start, 2)} seconds\n\n')
                flag = 5

        # 6: Scrape Vagas for Unclassified Jobs
        elif flag == 6:
            print("You selected: Scrape Vagas for Unclassified Jobs")
            try:
                start = time.perf_counter()
                scrape_Vagas(driver, 1, 'vaga_geral')
            except Exception as exception:
                traceback.print_exc()
                continue
            finally:
                end = time.perf_counter()
                print(f'\nFinished in {round(end - start, 2)} seconds\n\n')
                flag = menu_main()

        # 7: Scrape InfoJobs for All Courses
        elif flag == 7:
            print("You selected: Scrape InfoJobs for All Courses")
            try:
                start = time.perf_counter()
                courseList = getCourseList()
                for course in courseList:
                    course_id = course[0]
                    if course_id == 1:
                        print(f"Course {course} is not a valid course")
                    else:
                        scrape_Infojobs(driver, course_id, 'vaga_formatada')
            except Exception:
                traceback.print_exc()
                continue
            finally:
                end = time.perf_counter()
                print(f'\nFinished in {round(end - start, 2)} seconds\n\n')
                flag = menu_main()

        # 8: Scrape InfoJobs for Specific Course ID
        elif flag == 8:
            print("You selected: InfoJobs for Specific Course ID")
            try:
                print(f'Select the course you wish to Scrape from the list:')
                printCourseList()
                course = int(input())
                scrape_Infojobs(driver, course, 'vaga_formatada')
            except Exception:
                traceback.print_exc()
                continue
            finally:
                flag = 8

        # 9: Scrape InfoJobs for Unclassified Jobs
        elif flag == 9:
            try:
                scrape_Infojobs(driver, 1, 'vaga_geral')
            except Exception:
                traceback.print_exc()
                continue
            finally:
                flag = menu_main()

        # 10: Scrape All Platforms for Specific Course ID
        elif flag ==10:
            print("You selected: All Platforms for Specific Course ID ")
            try:
                print(f'Select the course you wish to Scrape from the list:')
                printCourseList()
                course = int(input())

                while course not in range(1, len(getCourseList())+1):
                    print(f'Input "{course}" is not a valid course, try a number between 1 and {len(getCourseList())}...')
                    course = int(input())

                if course == 1:
                    table = 'vaga_geral'
                else:
                    table = 'vaga_formatada'
                print(f'Course ID: {course}, Table: {table}')
                scrape_Linkedin(driver, course, table)
                scrape_Vagas(driver, course, table)
                scrape_Infojobs(driver, course, table)
            except Exception:
                traceback.print_exc()
                continue
            finally:
                flag = 10



def scrape_Linkedin(driver, course_id, table_name):
    try:
        start = time.perf_counter()
        url = Linkedin.getUrlForCourse(course_id)
        jobs = Linkedin.getJobsFromUrl(driver, url, course_id)
        print(f'\nFound {len(jobs)} jobs for Course ID {course_id} !')
        print(f'\nSaving jobs to database...')
        for counter, job in enumerate(jobs):
            print(f'\n# {counter} / {len(jobs)}: {job}')
            saveJob(table_name, job)
    except Exception:
        traceback.print_exc()
    finally:
        end = time.perf_counter()
        print(f'\nFinished in {round(end - start, 2)} seconds\n\n')


def scrape_Vagas(driver, course_id, table_name):
    try:
        start = time.perf_counter()
        jobs = Vagas.getJobList(driver, course_id)
        print(f'\nFound {len(jobs)} jobs for Course ID {course_id} !')
        print(f'\nSaving jobs to database...')
        for counter, job in enumerate(jobs):
            print(f'\n# {counter} / {len(jobs)}: {job}')
            saveJob(table_name, job)
    except Exception:
        traceback.print_exc()
    finally:
        end = time.perf_counter()
        print(f'\nFinished in {round(end - start, 2)} seconds\n\n')


def scrape_Infojobs(driver, course_id, table_name):
    try:
        print(f'You selected: Scrape InfoJobs for Course {course_id}')
        start = time.perf_counter()
        jobs = Infojobs.getJobsFromCourseID(driver, course_id)
        print(f'\nFound {len(jobs)} jobs for Course ID {course_id} !')
        print(f'\nSaving jobs to database...')
        for counter, job in enumerate(jobs):
            print(f'\n# {counter} / {len(jobs)}: {job}')
            saveJob(table_name, job)
    except Exception:
        traceback.print_exc()
    finally:
        end = time.perf_counter()
        print(f'\nFinished in {round(end - start, 2)} seconds\n\n')


def printCourseList():
    print(f'ID - Course Name')
    for course in getCourseList():
        print(f'{course[0]} - {course[1]}')


if __name__ == "__main__":
    start = time.perf_counter()
    main()
    print(
        f'\n🔥 Total time elapsed: {round(time.perf_counter() - start, 2)} seconds\n')
