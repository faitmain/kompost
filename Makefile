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
	bin/pip install Pillow
	bin/pip install rst2pdf

generate:
	bin/python generate.py
