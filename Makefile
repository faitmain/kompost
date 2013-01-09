.PHONY: build generate

ifndef VTENV_OPTS
VTENV_OPTS = "--no-site-packages"
endif

build:
	virtualenv $(VTENV_OPTS) .
	bin/python setup.py develop

generate:
	bin/faitmain
