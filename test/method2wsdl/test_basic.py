import logging
from typing import Tuple, Any, Callable
logger = logging.getLogger(__name__)
from pytest import fixture
from rdflib_wsdl.generate_helper import python_interface, python_endpoint
from rdflib_wsdl.generate_helper.python import _python_endpoint
from rdflib_wsdl import generateRDF
from rdflib_wsdl.basic_implementations import easyDescription
from rdflib import Graph
from rdflib.compare import to_isomorphic, graph_diff

def mymethod(name: str, number: int) -> str:
    """Combines the name and the number"""
    return "%s%d"% (name, number)

_basicmethod2ttl_interface = "urn://test_basicmethod2ttl#wsdl.interface(test.method2wsdl.test_basic)"
_basicmethod2ttl_ttl = """
@prefix ns1: <http://www.w3.org/ns/wsdl-rdf#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix pwsdl: <https://github.com/WhiteGobo/rdflib_wsdl/pythonmethods#> .

<urn://test_basicmethod2ttl#wsdl.description()> a ns1:Description ;
    ns1:interface <urn://test_basicmethod2ttl#wsdl.interface(test.method2wsdl.test_basic)> ;
    ns1:service <urn://test_basicmethod2ttl#wsdl.service(mymethod)> .

<urn://test_basicmethod2ttl#wsdl.interfaceMessageReference(test.method2wsdl.test_basic/test.method2wsdl.test_basic/input)> a ns1:InputMessage,
        ns1:InterfaceMessageReference ;
    ns1:messageContentModel ns1:OtherContent ;
    ns1:messageLabel <http://www.w3.org/ns/wsdl/in-out#Out> .

<urn://test_basicmethod2ttl#wsdl.interfaceMessageReference(test.method2wsdl.test_basic/test.method2wsdl.test_basic/output)> a ns1:InterfaceMessageReference,
        ns1:OutputMessage ;
    ns1:messageContentModel ns1:OtherContent ;
    ns1:messageLabel <http://www.w3.org/ns/wsdl/in-out#Out> .

<urn://test_basicmethod2ttl#wsdl.interfaceOperation(test.method2wsdl.test_basic/test.method2wsdl.test_basic)> a ns1:InterfaceOperation ;
    rdfs:label "test.method2wsdl.test_basic" ;
    ns1:interfaceMessageReference <urn://test_basicmethod2ttl#wsdl.interfaceMessageReference(test.method2wsdl.test_basic/test.method2wsdl.test_basic/input)>,
        <urn://test_basicmethod2ttl#wsdl.interfaceMessageReference(test.method2wsdl.test_basic/test.method2wsdl.test_basic/output)> ;
    ns1:messageExchangePattern <http://www.w3.org/ns/wsdl/in-out> .

<urn://test_basicmethod2ttl#wsdl.service(mymethod)> a ns1:Service ;
    rdfs:label "mymethod" ;
    ns1:endpoint <urn://test_basicmethod2ttl#wsdl.endpoint(mymethod/mymethod)> ;
    ns1:implements <urn://test_basicmethod2ttl#wsdl.interface(test.method2wsdl.test_basic)> .

<urn://test_basicmethod2ttl#wsdl.endpoint(mymethod/mymethod)>
    a ns1:Endpoint, pwsdl:method;
    rdfs:label "mymethod" ;
    ns1:usesBinding <urn://test_basicmethod2ttl#wsdl.binding(mymethod)> ;
    pwsdl:path "test.method2wsdl.test_basic";
    pwsdl:name "mymethod".

<urn://test_basicmethod2ttl#wsdl.interface(test.method2wsdl.test_basic)> a ns1:Interface ;
    rdfs:label "test.method2wsdl.test_basic" ;
    ns1:interfaceOperation <urn://test_basicmethod2ttl#wsdl.interfaceOperation(test.method2wsdl.test_basic/test.method2wsdl.test_basic)> .
"""

from collections import namedtuple
MethodTestInformation = namedtuple(
        "ServiceInformation",
        ['rdfgraph', 'ttl', 'method', 'test_input','test_output',
         'interface_name', "targetNamespace"],
        )
"""Collection of all information needed to handle one method"""

@fixture
def method_test_information() -> MethodTestInformation:
    """Returns all information needed to test a method"""
    myinput = ("asdf", 3)
    myoutput = mymethod(*myinput)
    g = Graph().parse(data=_basicmethod2ttl_ttl, format="ttl")
    return MethodTestInformation(
            g, _basicmethod2ttl_ttl, mymethod,
            myinput, myoutput,
            _basicmethod2ttl_interface,
            "urn://test_basicmethod2ttl",
            )
    
@fixture
def description(method_test_information):
    method = method_test_information.method
    targetNamespace = method_test_information.targetNamespace
    interface = python_interface.from_method(method, targetNamespace=targetNamespace)
    interface_operation = next(iter(interface.interface_operations))
    description = interface.parent
    endpoint = python_endpoint.from_method(method, interface_operation)
    #g = generateRDF(description)
    return description

@fixture
def rdfgraph_from_description(description):
    return generateRDF(description)

@fixture
def data_test_input_output(method_test_information):
    """Returns an method input tuple and the expected output for the method."""
    myinput = method_test_information.test_input
    myoutput = method_test_information.test_output
    return myinput, myoutput

@fixture
def method(description):
    for service in description.services:
        for endpoint in service.endpoints:
            logger.debug("directly loading method from given endpoint")
            try:
                yield endpoint.method
            except AttributeError:
                raise

def test_checkServiceOutput(data_test_input_output, method):
    """Tests if a service works and produces the correct output"""
    myinput, myoutput = data_test_input_output
    result = method(*myinput)
    try:
        assert result == myoutput,\
                "Method of endpoint didnt produce correct output. "\
                "See debug for more information."
    except AssertionError:
        logger.debug("Used input: %s" % myinput)
        logger.debug("Method produced output: %s\n\nExpected output: %s"
                     % (result, myoutput))
        raise

def test_checkPythonDescriptionData(method_test_information, description,
                                    rdfgraph_from_description):
    """Checks if created data and expected data is the same"""
    interface_data = method_test_information.ttl
    method = method_test_information.method
    g = rdfgraph_from_description
    iso_g = to_isomorphic(g)
    iso_comp = to_isomorphic(Graph().parse(data=_basicmethod2ttl_ttl,
                                           format="ttl"))
    inboth, ing, incomp = graph_diff(iso_g, iso_comp)
    try:
        assert not ing and not incomp, "Not the same information"
    except AssertionError:
        logger.info("Expected Graph:\n%s" % iso_comp.serialize())
        logger.info("Generated graph holds info:\n%s" % iso_g.serialize())
        logger.debug("info only in expected graph:\n%s" % incomp.serialize())
        logger.debug("info only in generated graph:\n%s" % ing.serialize())
        raise
