from rdflib import Graph, URIRef
from ..shared import LogicTestInformation
from importlib.resources import files
from . import local
localfiles = files(local)

def mymethod(name: str, number: int) -> str:
    """Combines the name and the number"""
    return "%s%d"% (name, number)

graph = Graph().parse(
        localfiles.joinpath("full_description.ttl"),
        format='ttl')
#graph.parse(data=_basic_test_ttl_without_logic, format='ttl')
basegraph = Graph().parse(
        localfiles.joinpath("description_without_logic.ttl"),
        format='ttl')
ingraph = Graph().parse(
        localfiles.joinpath("expected_input_information.ttl"),
        format='ttl')
outgraph = Graph().parse(
        localfiles.joinpath("generated_output_information.ttl"),
        format='ttl')

_basic_test_input_vars = {
        URIRef("urn://test/information#mystr"): "mystr",
        URIRef("urn://test/information#myint"): "myint",
        }
_basic_test_output_vars = {
        URIRef("urn://test/information#myreturn"): "myreturn",
        }
interface_operation_iri = URIRef("urn://test/information#wsdl.interfaceOperation(myInterface/myio)")
inputdata = Graph().parse(data="""
@prefix A: <urn://test/information#> .
A:base A:strpointer "asdf".
A:base A:intpointer 3.
""", format="ttl")
outputdata = Graph().parse(data="""
@prefix A: <urn://test/information#> .
A:base A:strpointer "asdf".
A:base A:intpointer 3.
A:base A:amalgamation "asdf3".
""", format="ttl")
inputdata_rif = Graph().parse(
        localfiles.joinpath("inputdata_rif.ttl"),
        format="ttl",
        )
outputdata_rif = Graph().parse(
        localfiles.joinpath("outputdata_rif.ttl"),
        format="ttl",
        )
info = LogicTestInformation(
        graph, ingraph, outgraph,
        _basic_test_input_vars,
        _basic_test_output_vars,
        basegraph,
        interface_operation_iri,
        inputdata, outputdata,
        inputdata_rif, outputdata_rif,
        )
