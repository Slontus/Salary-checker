import requests
from dotenv import load_dotenv
import os
from itertools import count
from terminaltables import SingleTable


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


def predict_rub_salary_hh(salary_dict):
    if salary_dict['currency'] != 'RUR':
        return None
    return predict_salary(salary_dict['from'], salary_dict['to'])


def predict_salary(salary_from, salary_to):
    if salary_from and salary_to:
        return (salary_from + salary_to)/2
    elif not salary_from and salary_to:
        return salary_to * 0.8
    elif salary_from and not salary_to:
        return salary_from * 1.2
    else:
        return None


def create_table_from_salary_dict(language_statistic_dict, table_title):
    table_data = [TABLE_HEADER]
    for lang, statistic in language_statistic_dict.items():
        table_row = (lang, statistic['vacancies_found'], statistic['vacancies_processed'], statistic['average_salary'])
        table_data.append(table_row)
    table_instance = SingleTable(table_data, table_title)
    print(table_instance.table)
    print()


def fetch_sj_salary_data():
    languages_sj_salary_dict = {}
    header = {"X-Api-App-Id": secret_key}
    for _language in LANGUAGES:
        lang_salary_statistic = {}
        lang_vacancies = []
        for _page in count(0):
            _payload = {'town': SJ_TOWN, 'catalogues': CATALOG, 'page': _page, 'keyword': _language}
            response = requests.get(SJ_URL, headers=header, params=_payload)
            response.raise_for_status()
            page_data = response.json().get('objects')
            if page_data:
                lang_vacancies.extend(page_data)
            else:
                break
        if lang_vacancies:
            lang_salary_statistic['vacancies_found'] = len(lang_vacancies)
            processed_salaries = list(filter(lambda x: x is not None, map(predict_rub_salary_sj, lang_vacancies)))
            lang_salary_statistic['vacancies_processed'] = len(processed_salaries)
            if processed_salaries:
                lang_salary_statistic['average_salary'] = int(sum(processed_salaries)/len(processed_salaries))
            else:
                lang_salary_statistic['average_salary'] = 0
            languages_sj_salary_dict[_language] = lang_salary_statistic
    return languages_sj_salary_dict


def fetch_hh_salary_data():
    languages_hh_salary_dict = {}
    for _language in LANGUAGES:
        lang_salary_statistic = {}
        _payload = {"text": f"программист {_language}", "period": 30, "area": HH_AREA}
        response = requests.get(HH_URL, params=_payload)
        response.raise_for_status()
        if response.json()['found'] >= 100:
            lang_salary_statistic["vacancies_found"] = response.json()['found']
            lang_vacancies = []
            for page in range(response.json()['pages']):
                _payload["page"] = page
                response = requests.get(HH_URL, params=_payload)
                response.raise_for_status()
                lang_vacancies.extend(response.json()['items'])
            salaries_list = [vacancy['salary'] for vacancy in lang_vacancies if vacancy['salary'] is not None]
            processed_salaries = list(filter(lambda x: x is not None, map(predict_rub_salary_hh, salaries_list)))
            lang_salary_statistic["vacancies_processed"] = len(processed_salaries)
            lang_salary_statistic["average_salary"] = int(sum(processed_salaries)/len(processed_salaries))
            languages_hh_salary_dict[_language] = lang_salary_statistic
    return languages_hh_salary_dict


if __name__ == '__main__':
    load_dotenv()
    secret_key = os.getenv('SECRET_KEY')
    create_table_from_salary_dict(fetch_hh_salary_data(), 'HeadHunter Moscow')
    create_table_from_salary_dict(fetch_sj_salary_data(), 'SuperJob Moscow')

