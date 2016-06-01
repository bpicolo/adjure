.PHONY: run
run: venv
	docker-compose up adjure

.PHONY: run-production
run-production:
	./venv/bin/uwsgi uwsgi-production.ini --pyargv "--config config.yaml"

.PHONY: run-dev
run-dev: venv
	./venv/bin/uwsgi uwsgi-dev.ini --pyargv "--config config.yaml"

venv:
	virtualenv -ppython3.5 venv
	./venv/bin/pip install -r requirements.txt

.PHONY: test
test:
	tox

.PHONY: clean
clean:
	rm -rf venv

