from vagas_formated_data import getJobDetails
from scraper_aux import *
import instance.driver
from Job import Job
from instance.config import config
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from time import sleep
from unicodedata import normalize
# from configparser import ConfigParser
import traceback


def getJobsFrom_VagasG(driver):
    jobList = []
    urls = [
        "https://www.vagas.com.br/vagas-de-estagio?m%5B%5D=Empresa+e+Home+Office",
        "https://www.vagas.com.br/vagas-de-estagio?m%5B%5D=100%25+Home+Office"
    ]
    for url in urls:
        driver.get(url)
        sleep(3)

        # Find the load button and click
        while True:
            try:
                print('Loading page...')
                # scroll(driver)
                sleep(1)
                # button = driver.find_element_by_xpath('//*[@id="maisVagas"]')
                buttons = driver.find_elements(
                    By.XPATH, '//*[@id="maisVagas"]')
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
            script.extract()  # rip it out

        # find all jobs
        vaga_odd = soup.findAll("li", {"class": "vaga odd"})
        vaga_even = soup.findAll("li", {"class": "vaga even"})
        vaga_total = vaga_even + vaga_odd

        # loops over all vaga_total
        print(f'Found {len(vaga_total)} jobs!')
        for count, vagas in enumerate(vaga_total):
            print(f'\n## Parsing job {count} of {len(vaga_total)}')
            link = trimUrlVagas("https://www.vagas.com.br" + vagas.a["href"])
            job = getJobDetails(driver, link, 1)
            print(f'Appending: {job}')
            jobList.append(job)
    return jobList


if __name__ == '__main__':
    print("\n\n##############################")
    print("# Please Run scraper_main.py #")
    print("##############################\n\n")
