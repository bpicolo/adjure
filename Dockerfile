FROM ubuntu:trusty

RUN apt-get update && apt-get -y install python3-pip \
                    python3-dev \
                    python3.4 \
                    make

ADD . /src
WORKDIR /src

CMD make run
