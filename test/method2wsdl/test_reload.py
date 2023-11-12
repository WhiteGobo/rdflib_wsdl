"""Testing if a python method can be loaded from a wsdl description.
Uses test_checkServiceOutput.
"""
from pytest import fixture
from typing import Tuple
from rdflib import Graph
from rdflib_wsdl.generate_helper.python import _python_endpoint
from rdflib_wsdl.generate_helper import load_python_endpoints
from .test_basic import method_test_information, test_checkServiceOutput, data_test_input_output

@fixture
def method(method_test_information):
    endpoints = list(load_python_endpoints(method_test_information.rdfgraph))
    if len(endpoints) == 0:
        raise Exception("coudlnt load any python endpoints.")

    for endpoint in endpoints:
        yield endpoint.method
