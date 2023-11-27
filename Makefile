PYTHON_TEST ?=python3 -m pytest
PYTEST_OPT ?=--log-level=INFO
DOCS_DIR = docs

build:
	python -m build

.PHONY: docs
docs:
	$(MAKE) -C $(DOCS_DIR) html

.PHONY: test
test:
	$(PYTHON_TEST) $(PYTEST_OPT)
	#python -m unittest


.PHONY: test_consistency_officialtestcases
test_consistency_officialtestcases:
	python -m tests.test_rif_officialtestcases

.PHONY: test_prdmarkup_rdflibparser
test_prdmarkup_rdflibparser:
	python -m tests.test_prdmarkup_rdflibparser
	#python -m tests.test_prdmarkup_rdflibparser

.PHONY: test_prdmarkup
test_prdmarkup:
	python -m tests.test_prdmarkup

.PHONY: test_validation
test_validation:
	python -m tests.test_xmlvalidation

.PHONY: test_rif2rdf
test_rif2rdf:
	python -m tests.test_parsing

