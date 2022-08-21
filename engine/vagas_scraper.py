# from instance.config import config
from Job import Job
from scraper_aux import *
# import instance.driver
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import urllib.parse
from time import sleep
from unicodedata import normalize
import traceback


def getUrlFromCourseID(course_id):
    url_base = "https://www.vagas.com.br/vagas-de-{term}/"
    course = getCourse(course_id)
    # print(f'Getting URL from Course ID: {course_id} || Course: {course}') # Log
    if course_id == 1:
        str = urllib.parse.quote_plus("Estagio")
        url = url_base.format(term=str)
    else:
        str = urllib.parse.quote_plus("Estagio-" + course[1])
        url = url_base.format(term=str)
    return url


def getJobList(driver, course_id):
    url = getUrlFromCourseID(course_id)
    jobList = []
    driver.get(url)
    sleep(5)

    # Find the load button and click
    while True:
        try:
            print('Loading page...')
            # scroll(driver)
            sleep(1)
            # Find the load button and click
            buttons = driver.find_elements(By.XPATH, '//*[@id="maisVagas"]')
            buttons[0].location_once_scrolled_into_view
            buttons[0].click()
        except Exception as exception:
            traceback.print_exc()
            print('No more jobs!')
            break

    print("Moving onto parsing...")
    # html parsing
    try:
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
    except Exception:
        traceback.print_exc()
        return

    for script in soup(["script", "style"]):
        script.extract()    # rip it out

    # find all jobs
    vaga_odd = soup.findAll("li", {"class": "vaga odd"})
    vaga_even = soup.findAll("li", {"class": "vaga even"})
    jobUrlList = vaga_even + vaga_odd

    # loops over all vaga_total
    for count, vagas in enumerate(jobUrlList):
        print(f'\nJob {count}/{len(jobUrlList)} for course #{course_id}:')
        link = trimUrlVagas("https://www.vagas.com.br" + vagas.a["href"])
        jobList.append(getJobDetails(driver, link, course_id))
    return jobList


def getJobDetails(driver, job_url, course_id):
    print(f'\nGetting Job Details: ')
    try:
        job_url = trimUrlAtRefid(job_url)
        print(f'--> Getting Job Detail Page\n[{job_url}]')
        sleep(1)
        driver.get(job_url)
        sleep(5)
        # html parsing
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
#
        # Extract job title
        vaga_title = soup.find(
            "h1", {"class": "job-shortdescription__title"}).get_text()
        # Extract job publication date
        vaga_data = soup.find(
            "li", {"class": "job-breadcrumb__item--published"}).get_text()
        job_date = getJobDate(vaga_data)
        # Extract job Poster #TODO
        vaga_poster = soup.find(
            "h2", {"class", "job-shortdescription__company"}).get_text()
        # Extract job Locale #TODO
        vaga_locale = soup.find(
            "span", {"class", "info-localizacao"}).get_text()
        # Extract job Description
        container_vaga_desc = soup.find(
            "div", "job-tab-content job-description__text texto")
        vaga_desc_texto = container_vaga_desc.get_text()
        vaga_desc_texto = vaga_desc_texto.replace(
            ",", "-").replace(";", "-").replace("Descrição", " ")

        job_url = trimUrlVagas(job_url)
        job_title = cleanup(vaga_title)
        vaga_desc_texto = cleanup(vaga_desc_texto)
        job_text_desc = treat_text(cleanup(vaga_desc_texto))
        job_poster = cleanup(vaga_poster)
        job_locale = cleanup(vaga_locale)
        newJob = Job(job_url, int(course_id), job_title,
                     job_text_desc, job_poster, job_date, job_locale)
        print(f'--> Job Details: {newJob}')
        return newJob
    except IndexError as err:
        print(traceback.format_exception_only)
        print(err.__cause__.__str__)
        print('This means no description was found in page.')
    except Exception as exception:
        traceback.print_exc()
    return


if __name__ == '__main__':
    print("\n\n##############################")
    print("# Please Run scraper_main.py #")
    print("##############################\n\n")
