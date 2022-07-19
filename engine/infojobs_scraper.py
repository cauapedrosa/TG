# Internals
from Job import Job
from scraper_aux import *
# Externals
from instance.config import config
from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
import urllib.parse
import traceback

link_base = "https://www.infojobs.com.br/empregos.aspx?tipocontrato=4&palabra={term}"


def getUrl_Infojobs(term):
    if term == None:
        str = urllib.parse.quote_plus("Estágio")
    else:
        str = urllib.parse.quote_plus(term)
    url = link_base.format(term=str)
    return url


def getJobDetails(driver, job_url, course_id):
    print(f'--> driver.get({job_url})')
    try:
        driver.get(job_url)
        sleep(3)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

    # Extract job title
        job_title = soup.find(
            'h2', {'class', 'font-weight-bolder'}).get_text()
    # Extract job description
        job_text_desc = soup.find(
            'p', {'class', 'mb-16 text-break white-space-pre-line'}).get_text().strip()
    # Extract job company
        job_poster = soup.select_one('a[title]').get_text()
    # Extract job date
        job_date = soup.find('div', {'class', 'caption'}).get_text().strip()
    # Extract job location
        job_locale = soup.find(
            'div', {'class', 'text-medium mb-4'}).get_text().strip()

    # Polishing Job Details
        job_title = cleanup(job_title)
        job_text_desc = cleanup(job_text_desc)
        job_poster = cleanup(job_poster)
        job_date = cleanup(job_date)
        job_locale = job_locale.split(',', 1)[0]
        job_locale = cleanup(job_locale)

        newJob = Job(job_url, int(course_id), job_title,
                     job_text_desc, job_poster, job_date, job_locale)
        print(f'\nNew Job Instanced at getJobDetails: {newJob}')
        return newJob
    except Exception as exception:
        traceback.print_exc()
    return


def getJobsFromUrlList_Infojobs(driver, jobUrlList, course_id):
    counter = 1
    jobList = []
    for jobUrl in jobUrlList:
        print(
            f'\nGetting Jobs from UrlList in Course #{course_id}: {counter}/{len(jobUrlList)}')
        job = getJobDetails(driver, jobUrl, course_id)
        jobList.append(job)
        counter += 1
    return jobList


def getJobsFromCourseID_InfoJobs(driver, course_id):
    print(f'\nGetting Jobs from Course ID: {course_id}')
    if course_id == 1:
        url = getUrl_Infojobs(None)
    else:
        courseName = getCourse(course_id)[1]
        url = getUrl_Infojobs(courseName)

    jobUrlList = []
    # Populate URL List
    while True:
        print(f'--> driver.get({url})')
        driver.get(url)
        sleep(3)
        try:
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
        except Exception as exception:
            traceback.print_exc()
            break

        # Find all job links in current page
        try:
            job_cards = soup.find_all('div', {'class', 'card'})
            for job_card in job_cards:
                job_href = job_card.find("div").find(
                    "a", {"class", "text-decoration-none"}).attrs['href']
                job_url = urllib.parse.urljoin(
                    "https://www.infojobs.com.br/", job_href)
                print(f'Appending Job URL: {job_url}')
                jobUrlList.append(job_url)
        except Exception:
            traceback.print_exc()
            continue

        # Find next page
        try:
            print(f'Finding next page...')
            next_url = soup.select_one('li > a[title="Próxima"]').attrs['href']
            if url == next_url | next_url == None:
                print(f'No more pages to scrape')
                break
            url = next_url
            print(f'Found next URL: {url}')
        except Exception:
            traceback.print_exc()
            break

    print(f'\nFound {len(jobUrlList)} Jobs')
    # Get Jobs from URL List
    jobList = getJobsFromUrlList_Infojobs(driver, jobUrlList, course_id)
    print(f'Returning jobList with len:{len(jobList)}')
    return jobList
