#iam's python pip makefile

all: help


help:
	@echo ''
	@echo 'Here are the targets:'
	@echo ''
	@echo 'To develop                :  "make develop"'
	@echo ''
	@echo 'To publish                :  "make publish"'
	@echo ''
	@echo 'To pylint (errors)        :  "make lint"'
	@echo 'To pylint (all)           :  "make lint_all"'

	@echo ''



#local editable install for developing
develop:
	pip install -e .


dist: clean
	python setup.py bdist_wheel

# If you need to push your project again,
# change the version number in sudokusensei/Version.py.
# otherwise the server will give you an error.

# requires an appropriate .pypirc file
publish: dist
	python -m twine upload --repository pypi dist/*

clean:
	rm -rf  *~ */*~ */*/*~ */__pycache__

spotless:  clean
	rm -rf dist build

PYLINT = $(shell which pylint)


check_lint:
ifeq ($(PYLINT),)
	$(error lint target requires pylint)
endif


lint: check_lint
# for detecting just errors:
	@ $(PYLINT) -E  sudokusensei/*.py *.py

lint_all: check_lint
# for detecting more than just errors:
	@ $(PYLINT) --disable=duplicate-code --rcfile=.pylintrc  sudokusensei/*.py *.py

.PHONY: lint check_lint rstify check_md2rst
