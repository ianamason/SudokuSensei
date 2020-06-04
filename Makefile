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
	@echo 'To turn README.rst 2 html :  "make zippity"'
	@echo 'To pylint (errors)        :  "make lint"'
	@echo 'To pylint (all)           :  "make lint_all"'
	@echo 'To update the README.rst  :  "make rstify"'

	@echo ''



#local editable install for developing
develop:
	pip install -e .


dist: clean
	python setup.py bdist_wheel

# If you need to push your project again,
# change the version number in sudoku/Version.py.
# otherwise the server will give you an error.

# requires an appropriate .pypirc file
publish: dist
	python -m twine upload --repository pypi dist/*


PANDOC = $(shell which pandoc)

check_pandoc:
ifeq ($(PANDOC),)
	$(error lint target requires pandoc)
endif


zippity: check_pandoc
	rm -rf doczip*; mkdir doczip;
	cat README.rst | pandoc -f rst > doczip/index.html
	zip -r -j doczip.zip doczip

MD2RST = $(shell which mdToRst)

check_md2rst:
ifeq ($(MD2RST),)
	$(error rstify target requires mdToRst)
endif

rstify: check_md2rst
	mdToRst README.md > README.rst


clean:
	rm -rf  *.pyc *~ */*~ __pycache__

PYLINT = $(shell which pylint)


check_lint:
ifeq ($(PYLINT),)
	$(error lint target requires pylint)
endif


lint: check_lint
# for detecting just errors:
	@ $(PYLINT) -E  sudoku/*.py *.py

lint_all: check_lint
# for detecting more than just errors:
	@ $(PYLINT) --rcfile=.pylintrc  sudoku/*.py *.py

.PHONY: lint check_lint rstify check_md2rst
