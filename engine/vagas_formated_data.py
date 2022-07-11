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


def getUrlFromCourseID_Vagas(course_id):
    url_base = "https://www.vagas.com.br/vagas-de-{term}/"
    course = getCourse(course_id)
    if course_id == 1:
        print(f'Course ({course[0]},{course[1]}) is not a valid course')
    else:
        str = urllib.parse.quote_plus("Estagio-" + course[1])
        url = url_base.format(term=str)
        return url

    return


def getJobsFromCourseID_VagasF(driver, course_id):
    url = getUrlFromCourseID_Vagas(course_id)
    job_link_list = []
    driver.get(url)
    # Find the load button and click
    while True:
        try:
            print('Loading page...')
            sleep(4)
            scroll(driver)
            # Find the load button and click
            buttons = driver.find_elements(By.XPATH, '//*[@id="maisVagas"]')
            buttons[0].location_once_scrolled_into_view
            buttons[0].click()
            sleep(2)
        except Exception as exception:
            traceback.print_exc()
            print('No more jobs!')
            break

    print("Moving onto parsing...")
    # html parsing
    try:
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
    except Exception as exception:
        traceback.print_exc()
        return

    for script in soup(["script", "style"]):
        script.extract()    # rip it out

    # find all jobs
    vaga_odd = soup.findAll("li", {"class": "vaga odd"})
    vaga_even = soup.findAll("li", {"class": "vaga even"})
    vaga_total = vaga_even + vaga_odd
    print("DEBUG|Found vagas: ", len(vaga_total))

    # loops over all vaga_total
    for vagas in vaga_total:
        job_link_list.append("https://www.vagas.com.br" + vagas.a["href"])

    return


def getJobDetails(driver, job_url, course_id):
    print(f'Getting Job Details: ')
    try:
        job_url = trimUrlAtRefid(job_url)
        print(f'\n--> Getting Job Detail Page\n[{job_url}]')
        driver.get(job_url)
        sleep(3)
        # html parsing
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
#
        vaga_counter += 1
        # Extract job title
        vaga_title = soup.find(
            "h1", {"class": "job-shortdescription__title"}).get_text()

        # Extract job description
        vaga_description = soup.find(
            "li", {"class": "job-breadcrumb__item--published"}).get_text()

        # Extract job publication date
        vaga_data = soup.find(
            "li", {"class": "job-breadcrumb__item--published"}).get_text()
        job_date = getJobDate(vaga_data)
        # Extract job Poster #TODO
        vaga_poster = soup.find(
            "h3", {"class", "job-shortdescription__company"}).get_text()
        # Extract job Locale #TODO
        vaga_locale = soup.find(
            "span", {"class", "info-localizacao"}).get_text()
        # Extract job Description
        container_vaga_desc = soup.find(
            "div", "job-tab-content job-description__text texto")
        vaga_desc_texto = container_vaga_desc.get_text()
        vaga_desc_texto = vaga_desc_texto.replace(
            ",", "-").replace(";", "-").replace("Descrição", " ")
        vaga_desc_words = vaga_desc_texto.split(' ')

        job_url = trimUrlVagas(job_url)
        job_title = cleanup(vaga_title)
        vaga_desc_texto = cleanup(vaga_desc_texto)
        vaga_desc_words = vaga_desc_texto.split(' ')
        join_vaga_desc = listToString(vaga_desc_words)
        job_text_desc = cleanup(join_vaga_desc)
        job_poster = cleanup(vaga_poster)
        job_locale = cleanup(vaga_locale)
        newJob = Job(job_url, int(course_id), job_title,
                     job_text_desc, job_poster, job_date, job_locale)
        print(f'\nNew Job Instanced at getJobDetails: {newJob}')
        print(f'URL: {newJob.url}')
        print(f'Course_ID: {newJob.course_id}')
        print(f'Title: {newJob.title}')
        print(f'Date: {newJob.date}')
        print(f'Poster: {newJob.poster}')
        print(f'Locale: {newJob.locale}')
#
        return newJob
    except IndexError as err:
        print(traceback.format_exception_only)
        print(err.__cause__.__str__)
        print('This means no description was found in page.')
    except Exception as exception:
        traceback.print_exc()
    return


def main():
    print("\n\n##############################")
    print("# Please Run scraper_main.py #")
    print("##############################\n\n")


if __name__ == '__main__':
    main()
