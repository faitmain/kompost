.PHONY: build generate

ifndef VTENV_OPTS
VTENV_OPTS = "--no-site-packages"
endif

build:
	virtualenv $(VTENV_OPTS) .
	bin/pip install Mako
	bin/pip install docutils
	bin/pip install Pygments
	bin/pip install requests

generate: 
	bin/python generate.py
