FROM python:3.9

ENV HOME=/opt/app

# Turn off Django debug mode
ENV DEPLOY=1

WORKDIR $HOME

COPY requirements.txt $HOME

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

COPY . $HOME

EXPOSE 80

ENV PYTHONUNBUFFERED=true

CMD ["/bin/sh", "run.sh"]
