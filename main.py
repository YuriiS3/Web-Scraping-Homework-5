import requests
import re
import hashlib
import json
from lxml import etree
import sqlite3
import csv
import xml.etree.ElementTree as ET

def get_content(url):
    name = hashlib.md5(url.encode('utf-8')).hexdigest()
    try:
        with open(name, 'r', newline='', encoding="utf-8") as f:
            content = f.read()
            return content
    except:
        response = requests.get(
            url,
            headers={
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 OPR/114.0.0.0 (Edition std-1)'
            }
        )
        with open(name, 'w', newline='', encoding="utf-8") as f:
            f.write(response.text)
        return response.text

def write_sql(data: list) -> None:
    filename = 'output.db'

    # 1. create table
    conn = sqlite3.connect(filename)
    cursor = conn.cursor()

    sql = """
        create table if not exists job_vacancies(
            id integer primary key,
            title text,
            url text
        )
    """
    cursor.execute(sql)

    sql = """
        delete from job_vacancies
    """
    cursor.execute(sql)

    # 2. insert data
    for item in data:
        cursor.execute("""
            insert into job_vacancies (id, title, url)
            values (?, ?, ?)
        """, (item[0], item[1], item[2]))

    conn.commit()
    conn.close()

def read_sql() -> None:
    filename = 'output.db'

    connection = sqlite3.connect(filename)
    cursor = connection.cursor()

    # 1. get names of people
    sql = """
        select id, title, url
        from job_vacancies
    """
    rows = cursor.execute(sql).fetchall()
    # print(rows)

    rows = cursor.execute(sql).fetchall()
    print(rows)

    connection.close()

def write_csv(data: list) -> None:
    filename = 'output.csv'

    with open(filename, mode='w', newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'title', 'url'])
        writer.writerows(data)

def write_xml(data: list) -> None:
    filename = 'output.xml'

    root = ET.Element('job_vacancies')
    for item in data:
        JV = ET.SubElement(root, 'Vacancies')
        ET.SubElement(JV, 'id').text = item[0]
        ET.SubElement(JV, 'title').text = str(item[1])
        ET.SubElement(JV, 'url').text = str(item[2])

    tree = ET.ElementTree(root)
    tree.write(filename, encoding='utf-8', xml_declaration=True)

if __name__ == '__main__':
    text = get_content('https://www.lejobadequat.com/emplois')
    pattern = r'<h3 class="jobCard_title m-0">(.+)\<\/h3>'
    job_match = re.findall(pattern, text)
    #print(job_match, type(job_match))

    tree = etree.HTML(text)
    xpath = '//article/a/@href'
    url_match = tree.xpath(xpath)
    #print(url_match, type(url_match))

    all_match = [{'id': i, 'title': e[0], 'url': e[1]} for i, e in enumerate(zip(job_match, url_match), start=1)]
    #print(all_match, type(all_match))

    all_match = json.dumps(all_match)
    obj = json.loads(all_match)
    json_formatted_str = json.dumps(obj, indent=4)

    with open('output.json', 'w', newline='', encoding="utf-8") as f:
        f.write(json_formatted_str)

    write_match = [[str(i), str(e[0]), str(e[1])] for i, e in enumerate(zip(job_match, url_match), start=1)]
    #print(write_match, type(write_match))

    write_sql(write_match)
    read_sql()
    write_csv(write_match)
    write_xml(write_match)
