all: build

build:
	@echo Bootstrap script
	pip install -U setuptools
	python bootstrap.py
	bin/buildout
endif

test:
	bin/test
