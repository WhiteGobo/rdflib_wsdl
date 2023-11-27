from typing import Tuple
import networkx as netx
from collections import namedtuple
from rdflib import Graph, URIRef, RDF
from rdflib.compare import to_isomorphic, graph_diff, to_canonical_graph
from rdflib_wsdl.shared import WSDL
import pytest
from pytest import fixture, param, skip
from rdflib_wsdl.generate_helper.rdflogic import LogicFormula, LogicInterfaceOperation
from rdflib_wsdl.generate_helper.generell_rdfbase import GraphInterface, GraphInterfaceOperation
from rdflib_wsdl.generate_helper.generell import easyInterface
from rdflib_wsdl import generateRDF
import logging
logger = logging.getLogger(__name__)

from .shared import LogicTestInformation
from rdflib_wsdl.tools import load_usable_endpoints_for

from . import baseexample

@fixture(params=[
    param(baseexample.info),
    ])
def logic_test_information(request) -> LogicTestInformation:
    return request.param

@fixture
def shared_information_graph(logic_test_information):
    g = Graph()
    for ax in logic_test_information.basegraph:
        g.add(ax)
    return g

@fixture
def compare_wsdl_graph(logic_test_information):
    return logic_test_information.graph

@fixture
def description_namespace(logic_test_information):
    description_iri, = logic_test_information.graph.subjects(RDF.type, WSDL.Description)
    targetNamespace, _ = description_iri.split("#wsdl.description")
    return targetNamespace

@fixture
def interface_operation(logic_test_information, shared_information_graph):
    interface_operation_iri = logic_test_information.interface_operation_iri
    interface_operation = GraphInterfaceOperation(
            shared_information_graph,
            interface_operation_iri,
            )
    return interface_operation

@fixture
def input_outputgraph(logic_test_information):
    return logic_test_information.inputgraph,\
            logic_test_information.outputgraph,\
            logic_test_information.inputnode2var,\
            logic_test_information.outputnode2var

@fixture
def created_wsdl_graph(
        interface_operation: LogicInterfaceOperation,
        input_outputgraph,
        shared_information_graph: Graph,
        ) -> Tuple[LogicFormula, LogicFormula]:
    g = shared_information_graph
    interface = interface_operation.parent
    description = interface.parent
    imrs = {imr.direction: imr
            for imr in interface_operation.interface_message_references}
    input_message_reference = imrs["in"]
    output_message_reference = imrs["out"]
    in_info, out_info, in_node2var, out_node2var = input_outputgraph
    targetNamespace = description.targetNamespace
    in_g = LogicFormula.create_from_rdfgraph(in_info, in_node2var, targetNamespace, "In")
    out_g = LogicFormula.create_from_rdfgraph(out_info, out_node2var, targetNamespace, "Out")
    for ax in in_g:
        g.add(ax)
    for ax in out_g:
        g.add(ax)
    g.add(in_g.axiom_implement_in_description(description))
    g.add(out_g.axiom_implement_in_description(description))
    g.add(in_g.axiom_bind_to(input_message_reference))
    g.add(out_g.axiom_bind_to(output_message_reference))
    logger.critical(in_g._graph.serialize())
    logger.critical(out_g._graph.serialize())
    return g

@fixture
def compare_wsdl_graph(logic_test_information):
    return logic_test_information.graph

def _sort_arrays(g: Graph,
                 ) -> Graph:
    g = to_canonical_graph(g)
    def sortkey(n):
        return str(n)
    mylists = {x: [x]
               for x in g.subjects(predicate=RDF.rest, object=RDF.nil)}
    listnodes = list(mylists.keys())
    firstnodes = set(listnodes)
    for n in listnodes:
        nextnode = g.value(predicate=RDF.rest, object=n)
        if nextnode is not None:
            mylists[nextnode] = [nextnode] + mylists[n]
            listnodes.append(nextnode)
            firstnodes.remove(n)
            firstnodes.add(nextnode)

    listnode2first = {}
    new_g = Graph()
    for o, p, s in g:
        if p != RDF.first:
            new_g.add((o, p, s))
        else:
            listnode2first[o] = s

    for n in firstnodes:
        l = mylists[n]
        firsts_list = [listnode2first[x] for x in l]
        firsts_list.sort(key=sortkey)
        for x, y in zip(l, firsts_list):
            new_g.add((x, RDF.first, y))
    return new_g


def test_check_created_graph(
        compare_wsdl_graph,
        created_wsdl_graph,
        ):
    """Transforms all lists, because they can be different
    """
    iso_g = to_isomorphic(_sort_arrays(created_wsdl_graph))
    iso_comp = to_isomorphic(_sort_arrays(compare_wsdl_graph))
    inboth, ing, incomp = graph_diff(iso_g, iso_comp)
    try:
        assert not ing and not incomp, "Not the same information"
    except AssertionError:
        logger.info("Expected Graph:\n%s" % iso_comp.serialize())
        logger.info("Generated graph holds info:\n%s" % iso_g.serialize())
        logger.debug("info only in expected graph:\n%s" % incomp.serialize())
        logger.debug("info only in generated graph:\n%s" % ing.serialize())
        raise

@fixture
def input_output_data(logic_test_information):
    return logic_test_information.test_input_data, logic_test_information.test_output_data

@fixture
def input_output_data_rif(logic_test_information):
    return logic_test_information.input_data_rif, logic_test_information.output_data_rif

def test_get_rif_input_output(
        compare_wsdl_graph,
        input_outputgraph,
        interface_operation,
        input_output_data,
        created_wsdl_graph,
        input_output_data_rif,
        ):
    skip("It seems, that graph_diff doesnt work correctly.")
    logger.debug(interface_operation.rdfgraph.serialize())
    inputdata, outputdata = input_output_data
    #endpoint = next(load_usable_endpoints_for(interface_operation))

    in_logic_formula = interface_operation.get_input_logic_formula
    out_logic_formula = interface_operation.get_output_logic_formula
    rif_input, rif_output = input_output_data_rif
    iso_rif_input = to_isomorphic(rif_input)
    iso_rif_output = to_isomorphic(rif_output)
    created_rif_input = to_isomorphic(in_logic_formula._graph)
    created_rif_output = to_isomorphic(out_logic_formula._graph)
    logger.critical(in_logic_formula._graph)
    _, _, incomp = graph_diff(created_rif_output, iso_rif_output)
    try:
        assert not incomp, "rif output information not fully implemented"
    except AssertionError:
        logger.error("missing info:\n%s" % incomp.serialize())
        logger.debug(iso_rif_output.serialize())
        logger.debug(created_rif_output.serialize())
        raise
    _, _, incomp = graph_diff(created_rif_input, iso_rif_input)
    try:
        assert not incomp, "rif input information not fully implemented"
    except AssertionError:
        logger.error("missing info:\n%s" % incomp.serialize())
        logger.debug(iso_rif_input.serialize())
        logger.debug(created_rif_input.serialize())
        raise

def test_input_outputgraph(
        compare_wsdl_graph,
        input_outputgraph,
        interface_operation,
        input_output_data,
        created_wsdl_graph,
        ):
    skip("Not method to generate sparql from rdflib")
    logger.debug(interface_operation.rdfgraph.serialize())
    inputdata, outputdata = input_output_data
    endpoint = next(load_usable_endpoints_for(interface_operation))

    in_g, out_g, inputnode2var, outputnode2var = input_outputgraph
    logger.critical(in_g.serialize())
    logger.critical(out_g.serialize())
    try:
        endpoint.method
    except AttributeError:
        pytest.skip("couldnt load method, so cant check if logic works "
                    "with method.")

    var2input = interface_operation.find_usable_inputs(inputdata)
    out_g = to_isomorphic(outputdata)
    raise Exception(q, outputdata)
    raise Exception(inputnode2var, outputnode2var)
