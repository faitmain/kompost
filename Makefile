.PHONY: build generate

ifndef VTENV_OPTS
VTENV_OPTS = "--no-site-packages"
endif

build:
	virtualenv $(VTENV_OPTS) .
	bin/pip install Mako
	bin/pip install docutils


generate: 
	bin/python generate.py
