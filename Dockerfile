FROM python:3.8.0

MAINTAINER Joshua Smeda

COPY . /TheHive_SLA_Monitor

WORKDIR /TheHive_SLA_Monitor

RUN pip install -r requirements.txt

EXPOSE 3000

# forward request and error logs to docker log collector
RUN ln -sf /dev/stdout debug.log \
	&& ln -sf /dev/stderr debug.log

CMD python ./main.py

