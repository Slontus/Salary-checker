import requests
from dotenv import load_dotenv
import os
from itertools import count
from terminaltables import SingleTable
from statistics import mean


HH_URL = "https://api.hh.ru/vacancies"
SJ_URL = "https://api.superjob.ru/2.0/vacancies/"
LANGUAGES = ['Typescript', 'Swift', 'Scala', 'Objective-C', 'Go', 'C', 'C#', 'C++', 'PHP', 'Ruby',
             'Python', 'Java', 'JavaScript']
CATALOG = 48
SJ_TOWN = 4
HH_AREA = 1
TABLE_HEADER = ('Programming language', 'Vacancies found', 'Vacancies processed', 'Average salary')


def predict_rub_salary_sj(vacancy):
    if vacancy['currency'] != 'rub':
        return None
    return predict_salary(vacancy['payment_from'], vacancy['payment_to'])


def predict_rub_salary_hh(salary):
    if salary['currency'] != 'RUR':
        return None
    return predict_salary(salary['from'], salary['to'])


def predict_salary(salary_from, salary_to):
    if salary_from and salary_to:
        return (salary_from + salary_to)/2
    elif not salary_from and salary_to:
        return salary_to * 0.8
    elif salary_from and not salary_to:
        return salary_from * 1.2
    else:
        return None


def convert_vacancies_statistic_to_table(vacancies_statistic, table_title):
    table = [TABLE_HEADER]
    for lang, statistic in vacancies_statistic.items():
        table_row = (lang, statistic['vacancies_found'], statistic['vacancies_processed'], statistic['average_salary'])
        table.append(table_row)
    table_instance = SingleTable(table, table_title)
    return table_instance.table


def fetch_sj_vacancies_statistic(_secret_key):
    vacancies_statistic = {}
    header = {"X-Api-App-Id": _secret_key}
    for _language in LANGUAGES:
        lang_statistic = {}
        vacancies = []
        for _page in count(0):
            _payload = {'town': SJ_TOWN, 'catalogues': CATALOG, 'page': _page, 'keyword': _language}
            response = requests.get(SJ_URL, headers=header, params=_payload)
            response.raise_for_status()
            page_vacancies = response.json().get('objects')
            if page_vacancies:
                vacancies.extend(page_vacancies)
            else:
                break
        if vacancies:
            lang_statistic['vacancies_found'] = len(vacancies)
            processed_salaries = [salary for salary in map(predict_rub_salary_sj, vacancies) if salary]
            lang_statistic['vacancies_processed'] = len(processed_salaries)
            if processed_salaries:
                lang_statistic['average_salary'] = int(mean(processed_salaries))
            else:
                lang_statistic['average_salary'] = 0
            vacancies_statistic[_language] = lang_statistic
    return vacancies_statistic


def fetch_hh_vacancies_statistic():
    vacancies_statistic = {}
    for _language in LANGUAGES:
        lang_statistic = {}
        _payload = {"text": f"программист {_language}", "period": 30, "area": HH_AREA}
        response = requests.get(HH_URL, params=_payload)
        response.raise_for_status()
        response_page = response.json()
        if response_page['found'] >= 100:
            lang_statistic["vacancies_found"] = response_page['found']
            vacancies = []
            for page in range(response_page['pages']):
                _payload["page"] = page
                response = requests.get(HH_URL, params=_payload)
                response.raise_for_status()
                vacancies.extend(response.json()['items'])
            salaries = [vacancy['salary'] for vacancy in vacancies if vacancy['salary']]
            processed_salaries = [salary for salary in map(predict_rub_salary_hh, salaries) if salary]
            lang_statistic["vacancies_processed"] = len(processed_salaries)
            lang_statistic["average_salary"] = int(mean(processed_salaries))
            vacancies_statistic[_language] = lang_statistic
    return vacancies_statistic


if __name__ == '__main__':
    load_dotenv()
    secret_key = os.getenv('SECRET_KEY')
    print(convert_vacancies_statistic_to_table(fetch_hh_vacancies_statistic(), 'HeadHunter Moscow'), end="\n")
    print(convert_vacancies_statistic_to_table(fetch_sj_vacancies_statistic(secret_key), 'SuperJob Moscow'))
