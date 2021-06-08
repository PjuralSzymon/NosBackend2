# Pull a pre-built alpine docker image with nginx and python3 installed
#FROM python:3.6.3
#ENV LISTEN_PORT=8000
#EXPOSE 8000
#COPY /app /app
#COPY requirements.txt /
#RUN pip install -r /requirements.txt
#CMD python app/main.py runserver

FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.7
#
ENV LISTEN_PORT=8000
EXPOSE 8000
#
COPY /app /app
#
# Uncomment to install additional requirements from a requirements.txt file
COPY requirements.txt /
RUN apk --update add python py-pip openssl ca-certificates py-openssl wget
RUN apk --update add --virtual build-dependencies libffi-dev openssl-dev python-dev py-pip build-base \
  && pip install --upgrade pip \
  && pip install -r /requirements.txt \
  && apk del build-dependencies

#RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
#RUN python3 -m ensurepip
#RUN pip3 install --no-cache --upgrade pip setuptools
#RUN pip install --no-cache-dir -U pip
#RUN pip install --no-cache-dir -r /requirements.txt