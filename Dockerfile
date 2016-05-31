FROM python3.5.1

ADD . /src
WORKDIR /src

CMD make run
