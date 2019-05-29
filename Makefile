install: requirements
		pipenv install --three

test: requirements
		pipenv run tox -r

run: install
		@pipenv run python setup.py install
		pipenv run vmshepherd -c config/settings.example.yaml

develop:
		@pipenv run python setup.py develop
		pipenv run vmshepherd -c config/settings.example.yaml

requirements:
		@which pip3 &>/dev/null || (echo 'ERROR: Install python3 and pip3 (sudo apt-get install python3-pip)' && exit 1)
		@which pipenv || pip3 install --user pipenv -i https://pypi.python.org/pypi

clean:
		rm -rf `find . -name __pycache__`
		rm -f `find . -type f -name '*.py[co]' `
		rm -rf dist build htmlcov .tox
		rm install

.PHONY: install test show-docs run clean requirements
