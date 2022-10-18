# asyNc-backend

本仓库为2022-2023秋季学期软件工程课程新闻搜索系统项目子模块

项目父模块为[asyNc-web]([asyNc / asyNc-web · GitLab (secoder.net)](https://gitlab.secoder.net/asyNc/asyNc-web))

# Quick Start
### environment:
```
Ubuntu 22.04.1 LTS
Python 3.9
```
### setting up env:
```
pip install django==4.1.1
pip install djangorestframework==3.14.0
pip install django-filter==22.1
pip install django-cors-headers==3.13.0
pip install django-sslserver==0.22
pip install psycopg2-binary==2.9.4
pip install pyJWT==2.5.0
pip install elasticsearch==7.13.1
pip install elasticsearch-dsl==7.4.0
```
### install PostgreSQL
```
sudo apt install postgresql
```
### config PostgreSQL for testing
```
sudo su postgres
psql
CREATE USER django WITH PASSWORD 'SUPER_SECRET_PASSWORD';
CREATE DATABASE django OWNER django;
GRANT ALL PRIVILEGES ON DATABASE django TO django;
```
### if you need to start postgresql service manually:
```
service postgresql start
```
### migrate
```
python manage.py migrate
```
### run
```
python asyNc/manage.py runserver
```
### run sslserver
```
python asyNc/manage.py runsslserver
```
# Testing
## About pytest 
### installation
> pip install pytest-django==4.5.2
## About pylint
### installation
> sudo apt-get install pylint
### configuration
> configure file at .pylintrc
### future work
> should be replaced by pylint-django afterwards
## About pycodestyle
### installation
> sudo apt install pycodestyle
### configuration
> configure file at .pycodestyle
