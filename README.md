# asyNc-backend

本仓库为2022-2023秋季学期软件工程课程新闻搜索系统项目子模块

项目父模块为[asyNc-web]([asyNc / asyNc-web · GitLab (secoder.net)](https://gitlab.secoder.net/asyNc/asyNc-web))

### setting up env:
```
pip install django
pip install djangorestframework
pip install django-filter
pip install django-cors-headers
pip install django-sslserver
pip install psycopg2-binary
pip install pyJWT
pip install elasticsearch==7.13.1
pip install elasticsearch-dsl==7.4.0

```
### run
```
python asyNc/manage.py runserver
```
### run sslserver
```
python asyNc/manage.py runsslserver
```