#iam's makefile; maybe migrate some targets to the main Makefile when done.

all: help


help:
	@echo ''
	@echo 'Here are the targets:'
	@echo ''
	@echo 'To develop                :    "make develop"'
	@echo ''
	@echo 'To pylint (errors)        :    "make lint"'
	@echo 'To pylint (all)           :    "make lint_all"'
	@echo 'To update the README.rst  :    "make rstify"'

	@echo ''



#local editable install for developing
develop:
	pip install -e .

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
