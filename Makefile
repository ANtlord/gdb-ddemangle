all:
	dmd -c -fPIC -oflib.o lib.d
	dmd -shared -defaultlib=libphobos2.so -oflib.so lib.o -fPIC
