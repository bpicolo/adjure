FROM python:3.5.1

# Some docker practices say not to use virtualenvs in docker, because it's
# already self contained. I disagree, as having e.g. different uWSGI configurations
# inside vs outside docker containers is a much bigger sin
RUN pip install virtualenv

# Don't rebuild unless requirements are changed
ADD Makefile /src/Makefile
ADD requirements.txt /src/requirements.txt
WORKDIR /src
RUN make venv

ADD . /src
CMD make run-production
