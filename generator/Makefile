
CC?=clang

OS = $(shell uname)

ifeq (Darwin, $(findstring Darwin, ${OS}))
CFLAGS = -O3 -Wall
LIB = libsugen.dylib
LDFLAGS = -dynamiclib -fPIC
else
CFLAGS = -O3 -Wall
LIB = libsugen.so
LDFLAGS = -shared -fPIC
endif


all: help


help:
	@echo ''
	@echo 'Here are the targets:'
	@echo ''
	@echo 'To make the generator               :  "make sugen"'
	@echo 'To make the dynamic                 :  "make lib"'
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
	${CC} ${CFLAGS} -DNO_SOFA sugen.c -o sugen

lib: libsugen.c
	${CC} ${CFLAGS} ${LDFLAGS} libsugen.c -o ${LIB}

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
	rm -f sugen ${LIB}
