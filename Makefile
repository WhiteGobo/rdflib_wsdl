PYTHON_TEST ?=python3 -m pytest
PYTEST_OPT ?=--log-level=INFO
DOCS_DIR = docs

build:
	python -m build

.PHONY: docs
docs:
	$(MAKE) -C $(DOCS_DIR) html

.PHONY: opendoc
opendoc:
	xdg-open $(DOCS_DIR)/_build/html/index.html

.PHONY: test
test:
	$(PYTHON_TEST) $(PYTEST_OPT)
	#python -m unittest
