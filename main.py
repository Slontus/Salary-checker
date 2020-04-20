import requests
from dotenv import load_dotenv
import os
from itertools import count
from terminaltables import SingleTable


load_dotenv()
HH_URL = "https://api.hh.ru/vacancies"
SJ_URL = "https://api.superjob.ru/2.0/vacancies/"
LANGUAGES = ['Typescript', 'Swift', 'Scala', 'Objective-C', 'Go', 'C', 'C#', 'C++', 'PHP', 'Ruby',
             'Python', 'Java', 'JavaScript']
CATALOG = 48
SJ_TOWN = 4
HH_AREA = 1
TABLE_HEADER = ('Programming language', 'Vacancies found', 'Vacancies processed', 'Average salary')


def predict_rub_salary_sj(obj):
    if obj['currency'] != 'rub':
        return None
    return predict_salary(obj['payment_from'], obj['payment_to'])


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


def dict_to_table(dictionary, title):
    table_data = [TABLE_HEADER]
    for lang, val in dictionary.items():
        table_row = (lang, val['vacancies_found'], val['vacancies_processed'], val['average_salary'])
        table_data.append(table_row)
    table_instance = SingleTable(table_data, title)
    print(table_instance.table)
    print()


def fetch_sj_data():
    languages_sj_dict = {}
    header = {"X-Api-App-Id": secret_key}
    for _language in LANGUAGES:
        language_statistic = {}
        language_results = []
        for _page in count(0):
            _payload = {'town': SJ_TOWN, 'catalogues': CATALOG, 'page': _page, 'keyword': _language}
            response = requests.get(SJ_URL, headers=header, params=_payload)
            response.raise_for_status()
            page_data = response.json().get('objects')
            if page_data:
                language_results.extend(page_data)
            else:
                break
        if language_results:
            language_statistic['vacancies_found'] = len(language_results)
            processed_salaries = list(filter(lambda x: x is not None, map(predict_rub_salary_sj, language_results)))
            language_statistic['vacancies_processed'] = len(processed_salaries)
            if processed_salaries:
                language_statistic['average_salary'] = int(sum(processed_salaries)/len(processed_salaries))
            else:
                language_statistic['average_salary'] = 0
            languages_sj_dict[_language] = language_statistic
    return languages_sj_dict


def fetch_hh_data():
    languages_hh_dict = {}
    for _language in LANGUAGES:
        language_statistic = {}
        _payload = {"text": f"программист {_language}", "period": 30, "area": HH_AREA}
        response = requests.get(HH_URL, params=_payload)
        response.raise_for_status()
        if response.json()['found'] >= 100:
            language_statistic["vacancies_found"] = response.json()['found']
            lang_result = []
            for page in range(response.json()['pages']):
                _payload["page"] = page
                response = requests.get(HH_URL, params=_payload)
                response.raise_for_status()
                lang_result.extend(response.json()['items'])
            salaries_list = [item['salary'] for item in lang_result if item['salary'] is not None]
            processed_salaries = list(filter(lambda x: x is not None, map(predict_rub_salary_hh, salaries_list)))
            language_statistic["vacancies_processed"] = len(processed_salaries)
            language_statistic["average_salary"] = int(sum(processed_salaries)/len(processed_salaries))
            languages_hh_dict[_language] = language_statistic
    return languages_hh_dict


if __name__ == '__main__':
    load_dotenv()
    secret_key = os.getenv('SECRET_KEY')
    dict_to_table(fetch_hh_data(), 'HeadHunter Moscow')
    dict_to_table(fetch_sj_data(), 'SuperJobs Moscow')

