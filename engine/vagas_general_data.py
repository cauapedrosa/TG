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

        # Find the load button and click
        while True:
            try:
                driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);")
                print('Loading page...')
                sleep(2)
                # button = driver.find_element_by_xpath('//*[@id="maisVagas"]')
                buttons = driver.find_elements(By.XPATH,
                                               '//*[@id="maisVagas"]')
                print(f'DEBUG| buttons: {buttons}')
                buttons[0].click()
                print('Waiting for more jobs...')
                sleep(2)
            except Exception as exception:
                traceback.print_exc()
                break

        # html parsing
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # find all jobs
        vaga_odd = soup.findAll("li", {"class": "vaga odd"})
        vaga_even = soup.findAll("li", {"class": "vaga even"})
        vaga_total = vaga_even + vaga_odd
        print("DEBUG|Found vagas: ", len(vaga_total))

        for script in soup(["script", "style"]):
            script.extract()  # rip it out

        # loops over all vaga_total
        counter = 0
        for vagas in vaga_total:
            try:
                counter += 1
                print(f'''DEBUG| Extracting Vaga #{counter}''')
                # Extract job title
                vaga_title = vagas.a["title"]
                # print(f'Title: {vaga_title}')

                # Extract job link
                vaga_link = "https://www.vagas.com.br" + vagas.a["href"]

                # Extract job description
                driver.get(vaga_link)
                sleep(2)
                html_desc = driver.page_source
                soup_vaga_desc = BeautifulSoup(html_desc, 'html.parser')

                # Extract company name
                container_vaga_empresa = vagas.findAll("span",
                                                       {"class": "emprVaga"})
                vaga_empresa = container_vaga_empresa[0].text.strip()

                # Extract job publication date
                container_data = vagas.findAll("span",
                                               {"class": "data-publicacao"})
                vaga_date = container_data[0].text

                # Extract job relevance
                container_vaga_nivel = vagas.findAll("span",
                                                     {"class": "nivelVaga"})
                vaga_nivel = container_vaga_nivel[0].text.strip()

                # print("Unprocessed date: ", vaga_data)
                vaga_date = getJobDate(vaga_date)
                # print("Processed date: ", vaga_data)

                container_vaga_desc = soup_vaga_desc.find(
                    "div", "job-tab-content job-description__text texto")
                vaga_desc_texto = container_vaga_desc.get_text()
                vaga_desc_texto = vaga_desc_texto.replace(",", "-").replace(
                    ";", "-").replace("Descrição", " ")

            except Exception as exception:
                traceback.print_exc()
                continue

            try:
                vaga_title = cleanup(vaga_title)
                vaga_desc_texto = cleanup(vaga_desc_texto)
                vaga_nivel = cleanup(vaga_nivel)
                vaga_empresa = cleanup(vaga_empresa)
                vaga_desc_words = vaga_desc_texto.split(' ')
                join_vaga_desc = listToString(vaga_desc_words)
                print(f'Vaga #{counter} de {len(vaga_total)}')
                print(f'## Title| {vaga_title}')
                print(f'## Nivel| {vaga_nivel}')
                print(f'## Data | {vaga_date}')
                print(f'## Descr|{join_vaga_desc[0:70]}[...]')
                print(f'## Empresa| {vaga_empresa}')
                print('\n')
                j = Job(vaga_link, 0, vaga_title, vaga_desc_texto, vaga_date)
                jobList.append(j)
                print(f'Appended J({j}) to jobList')
            except Exception as exception:
                traceback.print_exc()
                continue

    return jobList


def main():
    print("\n\n##############################")
    print("# Please Run scraper_main.py #")
    print("##############################\n\n")


if __name__ == '__main__':
    main()
