# Internals
from Job import Job
from scraper_aux import *
# Externals
from unittest import skip
from instance.config import config
from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
import urllib.parse
# import charset_normalizer
import csv
import traceback

linkedin_base = "https://br.linkedin.com/jobs/search?keywords={term}&location=Brasil&geoId=106057199&trk=public_jobs_jobs-search-bar_search-submit&redirect=false&position=1&pageNum=0"


def getUrlForGeneralJobs():
    str = urllib.parse.quote_plus("Estágio")
    url = linkedin_base.format(term=str)
    return url


def getUrlForCourse(course_id):
    course = getCourse(course_id)
    if course_id == 1:
        print(f'Course ({course}) is not a valid course')
    else:
        str = urllib.parse.quote_plus("Estagio " + course[1])
        url = linkedin_base.format(term=str)
        return url


def getUrlsForAllCourses():
    urls = []
    courses = getCourseList()
    print(f'Getting URLs for All {len(courses)} Courses...')
    for course in courses:
        urls.append(getUrlForCourse(course[0]))
    print(f'Returning {len(urls)} URLs.')
    return urls


def getJobsFromUrl_Linkedin(driver, url, course_id):
    if course_id == 1:
        print("# CourseID 1 - Searching for Unclassified Jobs")
    else:
        print(f'# Subject: {course_id} - {getCourse(course_id)[1]}')  # Tracker
    print(f'\n--> Getting Jobs from\n[{url}]')
    driver.get(url)
    sleep(3)

    # Find the load button and click
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
    # Scrape HTML
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    linkedin_jobs = soup.find_all('a', {'class': 'base-card__full-link'})
    print(f'Found {len(linkedin_jobs)} len(vaga_linkedins).')  # Tracker
    print("--------------------------------")
    print("Entering Extraction Loop: ")
    jobList = []
    for counter, linkedin_job in enumerate(linkedin_jobs):
        print("--------------------------------")
        # print(f'Getting Job #{counter}/{len(linkedin_jobs)} for Subect {course_id} - {getCourse(course_id)[1]}')    # Tracker
        link = trimUrlAtRefid(linkedin_job['href'])
        jobList.append(getJobDetails(driver, link, course_id))
    return jobList


def getJobDetails(driver, job_url, course_id):
    # print(f'Getting Job Details: ')
    try:
        job_url = trimUrlAtRefid(job_url)
        print(
            f'\n--> Getting Job Detail Page\n[{job_url}]')  # DEBUG
        driver.get(job_url)
        sleep(3)

        ## Scrape HTML ##
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # Check for Signup Form
        soup_join_form = soup.findAll("span", {"class": "join-form"})
        if (soup_join_form != []):
            print("\n\n###############\nFOUND SIGNUP FORM\n###############\n")
            return 0

        # Extract Job title
        job_title = cleanup(soup.h1.string.strip())
        # Extract Job Description
        container_vaga_desc = soup.findAll(
            "div", {"class": "description__text description__text--rich"})
        text_desc_raw = container_vaga_desc[0].get_text(" ")
        # Extract Job Poster
        job_poster = soup.findAll("span", {"class": "topcard__flavor"})[
            0].get_text(strip=True)
        # Extract Job Locale
        job_locale = soup.findAll("span", {"class": "topcard__flavor"})[
            1].get_text(strip=True)
        # Extract Time
        soup_post_time_ago = soup.find(
            "span", {"class": "posted-time-ago__text"})
        text_post_time_ago = soup_post_time_ago.get_text(strip=True)
        ## Polishing Job Data ##
        print(f'\nNow Polishing Job Data')
        job_title = cleanup(job_title)
        job_text_desc = cleanupDescr_Linkedin(
            cleanup(listToString(text_desc_raw.split())))
        # Get Job Posting Date
        job_date = getJobDate(text_post_time_ago)
        # print(f'## course_id: {course_id}')
        # print(f'## Title: {job_title}')
        # print(f'## Date : {job_date}')
        # print(f'## Poster: {job_poster}')
        # print(f'## Locale: {job_locale}')
        # print(f'## Descr: {text_desc_clean}')
        newJob = Job(job_url, int(course_id), job_title,
                     job_text_desc, job_poster, job_date, job_locale)
        print(f'\nNew Job Instanced at getJobDetails: {newJob}')  # DEBUG
        # print(f'URL: {newJob.url}')
        # print(f'Course_ID: {newJob.course_id}')
        # print(f'Title: {newJob.title}')
        # print(f'Date: {newJob.date}')
        # print(f'Poster: {newJob.poster}')
        # print(f'Locale: {newJob.locale}')

        return newJob
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


def main():
    print("\n\n##############################")
    print("# Please Run scraper_main.py #")
    print("##############################\n\n")


if __name__ == '__main__':
    main()
