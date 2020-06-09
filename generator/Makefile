
CC?=clang

all: help


help:
	@echo ''
	@echo 'Here are the targets:'
	@echo ''
	@echo 'To make the generator               :  "make sugen"'
	@echo ''
	@echo 'To (try and) make an easy puzzle    :  "make easy"'
	@echo 'To (try and) make a medium puzzle   :  "make medium"'
	@echo 'To (try and) make a hard puzzle     :  "make hard"'
	@echo 'To (try and) make an evil puzzle    :  "make evil"'
	@echo 'To (try and) make an extreme puzzle :  "make extreme"'
	@echo ''
	@echo 'To clean up                         :  "make clean"'
	@echo ''

sugen: sugen.c
	${CC} -O3 -Wall sugen.c -o sugen

#these numbers are total guesses, but at least force the generator to try ...
easy: sugen
	./sugen -u -t 100 generate

medium: sugen
	./sugen -u -t 200 generate

hard: sugen
	./sugen -u -t 300 generate

evil: sugen
	./sugen -u -t 500 generate

extreme:
	./sugen -u -t 800 generate



clean:
	rm sugen
