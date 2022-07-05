import instance.driver
from Job import Job
import psycopg2
from instance.config import config
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from time import sleep
from datetime import date, datetime, timedelta
import datetime
import os
from unicodedata import normalize
import csv
from configparser import ConfigParser
import argparse
import traceback



def listToString(s):

    # initialize an empty string
    str1 = " "

    # traverse in the string
    for ele in s:
        ele = ele.replace('\n',
                          ' ').replace('\xa0',
                                       ' ').replace(',',
                                                    ' | ').replace(';', ' | ')
        str1 = str1 + ' ' + ele + ' '

    # return string
    return str1


def insert_vaga_geral(vaga_link, vaga_title, vaga_nivel, join_vaga_desc,
                      vaga_data):
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO vaga_geral(geral_url, geral_titulo, geral_cargo, geral_desc, geral_data, curso_id) VALUES(%s, %s, %s, %s, %s, %s)""",
            (vaga_link, vaga_title, vaga_nivel, join_vaga_desc, vaga_data, 1))
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def cleanup(txt):
    txt.replace(';', ' ').replace(',', ' ').replace('|', ' ')
    return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')


def main():
    parser = argparse.ArgumentParser(
        description='choose some browser chrome or chromium')
    parser.add_argument('-b',
                        action='store',
                        dest='browser',
                        help='write chrome or chromium')

    browser = parser.parse_args().browser

    if browser == 'chrome':
        binary_location = "/usr/bin/google-chrome-stable"
    elif browser == 'chromium':
        binary_location = "/usr/bin/chromium"
    else:
        print('choose a valid browser! chrome or chromium')



    #today



    row_list = [["Titulo", "link", "Descricao"]]

    for url in urls:
        getJobsFrom_VagasG(url, 0)

    with open('./db/reports/vagas_general_data.csv', 'a', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerows(row_list)

    #close chrome
    driver.quit()

    #close file
    file.close()

def getJobsFrom_VagasG():
    jobList = []
    urls = [
        "https://www.vagas.com.br/vagas-de-estagio?m%5B%5D=Empresa+e+Home+Office",
        "https://www.vagas.com.br/vagas-de-estagio?m%5B%5D=100%25+Home+Office"
    ]
    for url in urls:
        driver.get(url)

        #Find the load button and click
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

        #html parsing
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        #find all jobs
        vaga_odd = soup.findAll("li", {"class": "vaga odd"})
        vaga_even = soup.findAll("li", {"class": "vaga even"})
        vaga_total = vaga_even + vaga_odd
        print("DEBUG|Found vagas: ", len(vaga_total))

        for script in soup(["script", "style"]):
            script.extract()  # rip it out

        #loops over all vaga_total
        counter = 0
        for vagas in vaga_total:
            try:
                counter += 1
                print(f'''DEBUG| Extracting Vaga #{counter}''')
                ## Extract job title
                vaga_title = vagas.a["title"]
                # print(f'Title: {vaga_title}')

                ## Extract job link
                vaga_link = "https://www.vagas.com.br" + vagas.a["href"]

                ## Extract job description
                driver.get(vaga_link)
                sleep(2)
                html_desc = driver.page_source
                soup_vaga_desc = BeautifulSoup(html_desc, 'html.parser')

                ## Extract company name
                container_vaga_empresa = vagas.findAll("span",
                                                        {"class": "emprVaga"})
                vaga_empresa = container_vaga_empresa[0].text.strip()

                ## Extract job publication date
                container_data = vagas.findAll("span",
                                                {"class": "data-publicacao"})
                vaga_date = container_data[0].text

                ## Extract job relevance
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


def getJobDate(text_date):
    today = date.today()
    # job_date = today.strftime("%Y/%m/%d")
    delta = timedelta(0)
    if text_date == "Hoje":
        delta = timedelta(0)
    elif text_date == "Ontem":
        delta = timedelta(days=1)
    elif text_date == "Há 2 dias":
        delta = timedelta(days=2)
    elif text_date == "Há 3 dias":
        delta = timedelta(days=3)
    elif text_date == "Há 4 dias":
        delta = timedelta(days=4)
    elif text_date == "Há 5 dias":
        delta = timedelta(days=5)
    elif text_date == "Há 6 dias":
        delta = timedelta(days=6)
    elif text_date == "Há 7 dias":
        delta = timedelta(days=7)
    elif text_date == "Há 1 semana":
        delta = timedelta(weeks=1)
    elif text_date == "Há 2 semanas":
        delta = timedelta(weeks=2)
    elif text_date == "Há 3 semanas":
        delta = timedelta(weeks=3)
    elif text_date == "Há 1 mês":
        delta = timedelta(days=30)
    job_date = (today - delta)
    # print(f'getVagaDate({text_date} [d:{delta}]: {job_date})')
    return job_date


if __name__ == '__main__':
    main()