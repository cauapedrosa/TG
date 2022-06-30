import traceback
from unittest import skip

import psycopg2
from instance.config import config
from linkedin_scraper import getCourseList, getJobsFromCourse, saveJobToDB
import vagas_formated_data
from Job import Job


def saveJobGeneral(job):
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO vaga_geral(geral_url, geral_titulo, curso_id, geral_desc, geral_date, geral_local) VALUES(%s, %s, %s, %s, %s, %s)""",
            (job.url, job.title, job.course_id, job.desc, job.date, job.local))
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def saveJobFormatted(job):
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO vaga_formatada(formatada_url, curso_id, formatada_titulo, formatada_desc, f_date, f_local) VALUES(%s, %s, %s, %s);""",
            (job.url, job.title, job.course_id, job.desc, job.date, job.local))
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def main():
    flag = 1
    while (flag >0 ):
        print("\n#############################################")
        print("########  Starting scraper_main.py  #########")
        print("#############################################")
        print("####  Select an Option:             #########")
        print("# 0: Exit                                   #")
        print("# 1: Scrape Linkedin for All Courses        #")
        print("# 2: Scrape Linkedin for Specific Course ID #")
        print("# 3: Scrape Linkedin for Unclassified Jobs  #")
        print("# 4: Scrape Vagas for All Courses           #")
        print("# 5: Scrape Vagas for Specific Course ID    #")
        print("# 6: Scrape Vagas for Unclassified Jobs     #")
        print("#############################################")
        print("Selecting: ", end=" ")
        try:
            flag = int(input())
        except Exception as err:
            print("Please type a Number")
            continue

        #########
        ## Menu ##
        #########
        ## 0: Exit
        if flag == 0:
            print("Exiting...")
            flag = 0
        ## 1: Scrape Linkedin for All Courses
        elif flag == 1:
            try:
                print("You selected: Scrape Linkedin for All Courses")
                courseList = getCourseList()
                for course in courseList:
                    if course[0] == 1:
                        print("Course 1 is not a valid course")
                    else:
                        jobs = getJobsFromCourse(course[0])
                        for job in jobs:
                            saveJobToDB(job)
            except Exception as exception:
                traceback.print_exc()
                continue

        ## 2: Scrape Linkedin for Specific Course ID
        elif flag == 2:
            print("You selected: Scrape Linkedin for Specific Course ID")
            print(f'Select the course you wish to Scrape from the list:')
            printCourseList()
            aux = int(input())
            jobs = getJobsFromCourse(aux)
            for job in jobs:
                saveJobToDB(job)

        ## 3: Scrape Linkedin for Unclassified Jobs
        elif flag == 3:
            print("You selected: Scrape Linkedin for Unclassified Jobs")
        ## 4: Scrape Vagas for All Courses
        elif flag == 4:
            print("You selected: Scrape Vagas for All Courses")
        ## 5: Scrape Vagas for Specific Course ID
        elif flag == 5:
            print("You selected: Scrape Vagas for Specific Course ID")
        ## 6: Scrape Vagas for Unclassified Jobs
        elif flag == 6:
            print("You selected: Scrape Vagas for Unclassified Jobs")


def printCourseList():
    for course in getCourseList():
        print(f'{course[0]} - {course[1]}')


if __name__ == "__main__":
    main()
