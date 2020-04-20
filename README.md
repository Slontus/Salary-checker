# Programming vacancies compare
This program provides average salary in russian rubles
for the most popular programming languages. It processes 
real vacancies from [HeadHunter](https://hh.ru/) and 
[SuperJob](https://www.superjob.ru) sites.

### How to Install
Python3 should be already installed. Then use pip (or pip3,
if there is a conflict with Python2) to install dependencies:
```
pip install -r requirements.txt
```
SuperJob site uses OAth authentication.
In order to obtain secret key you need to register your
application [here](https://api.superjob.ru/register). It
will ask you to provide site but you can indicate any
working one. After you receive your secret key please 
create **.env** file in the same directory with **main.py**
file and save you key in the following way:
```
SECRET_KEY = your_secret_key_here
```
### Project Goals
The code is written for educational purposes on online-course 
for web-developers [dvmn.org](https://dvmn.org).