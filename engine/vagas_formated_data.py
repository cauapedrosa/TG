import instance.driver
import psycopg2
from instance.config import config
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options  import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import urllib.parse
from time import sleep
from datetime import date, timedelta
import datetime
import os
from unicodedata import normalize
import csv
from configparser import ConfigParser
import argparse
import traceback
#from vagas_general_data import insert_vaga_geral


def listToString(s):      
    # initialize an empty string 
    str1 = " "  
    
    # traverse in the string   
    for ele in s:
        ele = ele.replace('\n', ' ').replace('\xa0',' ').replace(',',' | ').replace(';', ' | ')
        str1 = str1 + ' ' + ele + ' '
      
    # return string   
    return str1  


def remover_acentos(txt):
    return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')


def insert_vaga_geral(vaga_link, vaga_title, vaga_nivel, join_vaga_desc, vaga_data, curso_id):
    conn = None
    try:
        params =  config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("""INSERT INTO vaga_geral(geral_url, geral_titulo, geral_cargo, geral_desc, geral_data, curso_id) VALUES(%s, %s, %s, %s, %s, %s)""",
                    (vaga_link, vaga_title, vaga_nivel, join_vaga_desc, vaga_data, curso_id))
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        print(f'DEBUG| Vaga {vaga_title} | CursoID {curso_id} | Sucessfully inserted into vaga_geral')
        if conn is not None:
            conn.close()

#                 insert_vaga_formatada(text_subject, vaga_title, vaga_link,  join_vaga_desc)

def insert_vaga_formatada(text_subject, vaga_title, vaga_link, join_vaga_desc):
    conn = None
    try:
        params =  config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # print("DEBUG: Inserting vaga_formatada: ", text_subject, vaga_title)
        cur.execute("""INSERT INTO vaga_formatada(formatada_url, formatada_titulo, formatada_desc, curso_id) VALUES(%s, %s, %s, %s);""",
                    (vaga_link, vaga_title, join_vaga_desc, text_subject))
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def getCourseList():
    conn = None
    try:
        params =  config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("""SELECT * FROM curso;""")
        courseList = cur.fetchall()        
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return courseList

def getCourse(n):
    conn = None
    try:
        params =  config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("""SELECT * FROM curso WHERE curso_id = %s;""", (n,))
        course = cur.fetchone()        
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return course

def cleanupDesc(txt):
    txt = txt.replace(';',' ').replace(',',' ').replace('|',' ').replace(':',' ').replace('-', ' ').replace('  ', ' ').strip(" :")
    return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')

def cleanupTitle(txt):
    txt = txt.replace(';',' ').replace(',',' ').replace('|',' ').replace(':',' ').replace('-', ' ').replace('  ', ' ').strip(" :")
    return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')

def main():
    parser = argparse.ArgumentParser(description='choose some browser chrome or chromium')
    parser.add_argument('-b', action='store', dest='browser', help='write chrome or chromium')
    browser = parser.parse_args().browser

    if browser == 'chrome':
        binary_location = "/usr/bin/google-chrome-stable" 
    elif browser == 'chromium':
        binary_location = "/usr/bin/chromium"
    else:
        print('choose a valid browser! chrome or chromium')

    #specify chrome locations
    ser = Service(instance.driver.driver_location)

    #add options
    opt = webdriver.ChromeOptions()
    # options.add_argument('')
    opt.binary_location = instance.driver.binary_location

    driver = webdriver.Chrome(service=ser, options=opt)

    #today
    today = date.today()

    #Open webdriver at site vagas.com
    urls = []
    url_base = "https://www.vagas.com.br/vagas-de-{term}?h%5B%5D=22&h%5B%5D=28&h%5B%5D=30"
    subjects = getCourseList()
    for course in getCourseList():
        if course[0] == 1:
            # urls.append("https://www.vagas.com.br/vagas-de-an%C3%A1lise-e-desenvolvimento-de-sistemas?h[]=22&h[]=28&h[]=30")
            print("Adding vagas to list")
        else:
            str = urllib.parse.quote_plus(course[1])
            url = url_base.format(term=str)
            print(f'Adding Course:{course[1]} | Link: |{url}|')
            urls.append(url)

    #
    row_list = [["Link" , "Titulo", "Desc", "Curso"]]

    url_counter=0
    for url in urls:
        url_counter+=1
        # skip first X courses
        if url_counter < 5:
            print(f'Skipping {url_counter}')
            continue
        #
        try:
            print(f'DEBUG|driver.get({url}):')
            driver.get(url)
            sleep(3)
            subject = getCourse(urls.index(url)+2)
            print("DEBUG|Subject: " + subject[1])
        except Exception as exception:
            traceback.print_exc()
            break;

        #Find the load button and click up to 10 times
        vaga_counter=0
        while True:
            try:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                print('Loading page...')
                sleep(2)
                # button = driver.find_element_by_xpath('//*[@id="maisVagas"]')
                buttons = driver.find_elements(By.XPATH, '//*[@id="maisVagas"]')
                # print(f'DEBUG| len of buttons: {len(buttons)}')
                buttons[0].click()
                vaga_counter += 1
                if(vaga_counter>=10):
                    print(f'Found {vaga_counter} buttons. Enough jobs!')
                    break
                else:
                    print(f'Waiting for more jobs... [{vaga_counter}]')
                sleep(2)
            except Exception as exception:
                # traceback.print_exc()
                print('No more jobs!')
                break;
            
        #html parsing
        try:
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
        except Exception as exception:
            print(f'EXCEPTION @ {subject[1]} |{exception}|')
            traceback.print_exc()
            continue;


        #find all jobs
        vaga_odd = soup.findAll("li", {"class":"vaga odd"})
        vaga_even = soup.findAll("li", {"class":"vaga even"})
        vaga_total = vaga_even + vaga_odd
        print( "DEBUG|Found vagas: ", len(vaga_total))

        for script in soup(["script", "style"]):
            script.extract()    # rip it out

        #loops over all vaga_total
        vaga_counter=0
        for vagas in vaga_total:
            vaga_counter+=1
            #extract job title
            vaga_title = vagas.a["title"]

            #extract job link
            vaga_link = "https://www.vagas.com.br" + vagas.a["href"]

            #extract job description 
            # print("DEBUG|Extracting description from: " + vaga_link)
            driver.get(vaga_link)
            sleep(2)
            html_desc = driver.page_source
            soup_vaga_desc = BeautifulSoup(html_desc, 'html.parser')

            #extract job relevance
            container_vaga_nivel = vagas.findAll("span", {"class": "nivelVaga"})
            vaga_nivel = container_vaga_nivel[0].text.strip()

            #extract job publication date    
            container_data = vagas.findAll("span", {"class": "data-publicacao"})
            vaga_data = container_data[0].text
            # print(vaga_data)

            format_str = '%d/%m/%Y'

            if vaga_data == "Hoje" :
                vaga_data = today.strftime("%Y/%m/%d")
            elif vaga_data == "Ontem" :
                vaga_data = today.strftime("%Y/%m/%d")
            elif vaga_data == "Há 2 dias" :
                vaga_data = today.strftime("%Y/%m/%d")
            elif vaga_data == "Há 3 dias" :
                vaga_data = today.strftime("%Y/%m/%d")
            elif vaga_data == "Há 4 dias" :
                vaga_data = today.strftime("%Y/%m/%d")
            elif vaga_data == "Há 5 dias" :
                vaga_data = today.strftime("%Y/%m/%d")
            elif vaga_data == "Há 6 dias" :
                vaga_data = today.strftime("%Y/%m/%d")
            elif vaga_data == "Há 7 dias" :
                vaga_data = today.strftime("%Y/%m/%d")
            else:
                vaga_data = datetime.datetime.strptime(vaga_data, format_str)
                vaga_data = vaga_data.strftime("%Y/%m/%d")

            # print(vaga_data)

            try:
                container_vaga_desc = soup_vaga_desc.find("div","job-tab-content job-description__text texto")
                vaga_desc_texto = container_vaga_desc.get_text()
                vaga_desc_texto = vaga_desc_texto.replace(",", "-").replace(";","-").replace("Descrição"," ")
                vaga_desc_words = vaga_desc_texto.split(' ')
            
            except Exception as exception:
                join_vaga_desc  = "confidencial"
                traceback.print_exc()
                continue
            
            try:
                subject_id = subject[0]
                text_subject = subject[1]
                vaga_title = cleanupDesc(vaga_title)
                vaga_link = vaga_link
                vaga_desc_texto = cleanupDesc(vaga_desc_texto)
                # print(f'DEBUG| PRE REPLACE| {vaga_desc_texto}')
                # vaga_desc_texto = vaga_desc_texto.replace("        :  "," ",1)
                # print(f'DEBUG| POS REPLACE| {vaga_desc_texto}')
                vaga_desc_words = vaga_desc_texto.split(' ')
                join_vaga_desc = listToString(vaga_desc_words)
                join_vaga_desc = cleanupDesc(join_vaga_desc)
                print(f'Vaga #{vaga_counter} de {len(vaga_total)} em {text_subject}')
                print(f'## Title| {vaga_title}')
                print(f'## Data | {vaga_data}')
                print(f'## Descr|{join_vaga_desc[0:70]}[...]')
                # print(f'## Desc:{vaga_desc_texto}')
                #Insert BD
                insert_vaga_formatada(subject_id, vaga_title, vaga_link,  join_vaga_desc)
                #CSV file
                actual_list = [vaga_link, vaga_title, join_vaga_desc, subject_id]   
                row_list.append(actual_list)
            except Exception as exception:
                traceback.print_exc()
                continue
    
    with open('./db/reports/vagas_formated_data.csv', 'a', newline='') as file:
        print("Writing to CSV...")
        writer = csv.writer(file, delimiter=';')
        writer.writerows(row_list)
        print("CSV file written!")


    #close chrome
    driver.quit()

    #close file
    file.close()

if __name__ == '__main__':
    main()