.PHONY: run
run: venv
	./venv/bin/uwsgi --yaml uwsgi-production.yaml --pyargv "-c config.yaml"

.PHONY: run-dev
run-dev: venv
	./venv/bin/uwsgi --yaml uwsgi-dev.yaml --pyargv "-c config.yaml"

venv:
	virtualenv -ppython3.4 venv
	./venv/bin/pip install -r requirements.txt

.PHONY: test
test:
	tox

.PHONY: clean
clean:
	rm -rf venv

