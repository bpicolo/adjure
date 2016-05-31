FROM python:3.5.1

# Don't rebuild unless requirements are changed
ADD requirements.txt /src/requirements.txt
RUN pip install -r /src/requirements.txt

ADD . /src
WORKDIR /src

CMD make run-in-docker
