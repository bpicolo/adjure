FROM python:3.5.1

ADD . /src
WORKDIR /src

RUN pip install -r requirements.txt

CMD make run-in-docker
