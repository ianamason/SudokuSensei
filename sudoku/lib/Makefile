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


all: lib

lib: libsugen.c
	${CC} ${CFLAGS} ${LDFLAGS} sugen.c -o ${LIB}

clean:
	rm -f ${LIB}
