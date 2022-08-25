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
from datetime import date

# Amount of jobs to fetch before getting details. Set to 0 to allow as many as possible.
max_jobs = 100  # 0 = unlimited
# Base link for Infojobs Internship search
link_base = "https://www.infojobs.com.br/empregos.aspx?tipocontrato=4&palabra={term}"

# Gets job links from a search term


def getJobDate(string):
    job_date = date.today()
    # print(f'\ngetJobDate: {string.split()}')
    if string == 'Ontem':
        return job_date - timedelta(days=1)
    elif string == 'Hoje':
        return job_date
    job_day = string.split()[0]
    job_month = string.split()[1]
    if int(job_day):
        job_date = job_date.replace(day=int(job_day))
    if job_month == 'jan':
        job_date = job_date.replace(month=1)
    elif job_month == 'fev':
        job_date = job_date.replace(month=2)
    elif job_month == 'mar':
        job_date = job_date.replace(month=3)
    elif job_month == 'abr':
        job_date = job_date.replace(month=4)
    elif job_month == 'mai':
        job_date = job_date.replace(month=5)
    elif job_month == 'jun':
        job_date = job_date.replace(month=6)
    elif job_month == 'jul':
        job_date = job_date.replace(month=7)
    elif job_month == 'ago':
        job_date = job_date.replace(month=8)
    elif job_month == 'set':
        job_date = job_date.replace(month=9)
    elif job_month == 'out':
        job_date = job_date.replace(month=10)
    elif job_month == 'nov':
        job_date = job_date.replace(month=11)
    elif job_month == 'dez':
        job_date = job_date.replace(month=12)
    return job_date


def getUrl_Infojobs(term):
    if term == None:
        # General search & Order by Newest First
        str = urllib.parse.quote_plus("Estágio&campo=griddate&orden=desc")
    else:
        # Search term is Course Name
        str = urllib.parse.quote_plus(term)
    url = link_base.format(term=str)
    return url

# Gets job details from a job link with a course id


def getJobDetails(driver, job_url, course_id):
    print(f'--> driver.get({job_url})')  # Print job url
    try:
        driver.get(job_url)
        sleep(1)
        html = driver.page_source  # Get html
        soup = BeautifulSoup(html, 'html.parser')  # Parse html
        job_Header = soup.select_one('div#VacancyHeader')  # Find job header
    # Extract job title
        job_title = job_Header.find(
            'h2', {'class', 'font-weight-bolder'}).get_text()
    # Extract job description
        job_text_desc = soup.find(
            'p', {'class', 'mb-16 text-break white-space-pre-line'}).get_text().strip()
    # Extract job poster
        if job_Header.select_one('div.h4 > a[href]') != None:
            job_poster = job_Header.select_one('div.h4 > a[href]').get_text()
        else:
            job_poster = "Empresa Confidencial"
    # Extract job date
        job_date = soup.find('div', {'class', 'caption'}).get_text().strip()
    # Extract job location
        job_locale = soup.find(
            'div', {'class', 'text-medium mb-4'}).get_text().strip()

    # Polishing Job Details
        job_title = cleanup(job_title)
        job_text_desc = treat_text(cleanup(job_text_desc))
        job_poster = cleanup(job_poster)
        job_date = getJobDate(job_date)
        job_locale = job_locale.split(',', 1)[0]
        job_locale = cleanup(job_locale)

        newJob = Job(job_url, int(course_id), job_title,
                     job_text_desc, job_poster, job_date, job_locale)
        # print(f'\nNew Job Instanced at getJobDetails: {newJob}')
        return newJob
    except Exception as exception:
        traceback.print_exc()
    return

# Gets job details for each job from a job url list with a course id


def getJobsFromUrlList_Infojobs(driver, jobUrlList, course_id):
    jobList = []
    for count, jobUrl in enumerate(jobUrlList):  # Iterate through jobUrlList
        print(f'\nJob {count}/{len(jobUrlList)} for course #{course_id}:')
        job = getJobDetails(driver, jobUrl, course_id)  # Get job details
        print(f'Got job details: {job}')  # Print job details
        jobList.append(job)  # Add job to jobList
    return jobList

#  Gets a list of jobs from a course id


def getJobsFromCourseID(driver, course_id):
    print(f'\nGetting Jobs from Course ID: {course_id}')
    if course_id == 1:
        url = getUrl_Infojobs(None)
    else:
        courseName = getCourse(course_id)[1]
        url = getUrl_Infojobs(courseName)

    jobUrlList = []
    # Populate URL List
    while True:
        try:
            print(f'\n--> driver.get({url})')
            driver.get(url)
            sleep(1)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
        except Exception:
            traceback.print_exc()
            break

        # Notice Agreement
        try:
            # if notice agreement button exists
            if soup.select("button#didomi-notice-agree-button"):
                print("\n--> Agreeing to didomi notice")
                # click it
                driver.find_element_by_id("didomi-notice-agree-button").click()
                sleep(1)
        except Exception:
            traceback.print_exc()
            print("Exception thrown in Notice Agree")
            continue

        # Find all job links in current page
        try:
            # job_cards = soup.find_all('div', {'class', 'card'})
            job_cards = soup.select('div.js_cardLink')  # Find all job cards
            print(f'\n--> Found {len(job_cards)} jobs')
            for job_card in job_cards:  # For each job card
                # If job card has a link
                if job_card.select_one('a.text-decoration-none').attrs['href']:
                    # TODO: Check if this is the correct way to get the href
                    job_href = job_card.select_one(
                        'a.text-decoration-none').attrs['href']  # Get href
                    job_url = urllib.parse.urljoin(
                        "https://www.infojobs.com.br/", job_href)  # Get full url
                    jobUrlList.append(job_url)  # Add to URL List
            print(f'Total job urls found: {len(jobUrlList)}')
        except Exception:
            traceback.print_exc()
            continue

        # Find next page
        try:
            if len(jobUrlList) >= max_jobs and max_jobs != 0:
                print(f'\n👍Found {max_jobs}(max_jobs) Jobs. Stopping.')
                break
            print(f'Finding next page...')
            next_button = soup.select_one(
                'li > a[title="Próxima"]')  # Find "next page" button
            if next_button.attrs['href']:  # If button has href
                next_url = next_button.attrs['href']  # Get href
                url = next_url  # Set url to next page
                # Print last 7 characters of url
                print(f'Found next URL: ...{url[-7:]}')
            else:
                print(f'No more pages to scrape')
                break
        except Exception:
            traceback.print_exc()
            break

    print(f'\nFound {len(jobUrlList)} Jobs')  # Print total jobs found
    # Get Jobs from URL List
    jobList = getJobsFromUrlList_Infojobs(driver, jobUrlList, course_id)
    print(f'Returning jobList with len:{len(jobList)}')
    return jobList
