FROM python:3.8.0

MAINTAINER Joshua Smeda

COPY . /TheHive_SLA_Monitor

WORKDIR /TheHive_SLA_Monitor

RUN pip install -r requirements.txt

EXPOSE 3000

CMD python ./main.py

