from rdflib import Graph, RDF, Namespace
from typing import List

PYTHONWSDL\
        = Namespace("https://github.com/WhiteGobo/rdflib_wsdl/pythonmethods#")

def load_python_endpoints(graph: Graph) -> List:
    endpoints = []

    for x in graph.subjects(RDF.type, PYTHONWSDL.method):
        raise Exception(x)

    return endpoints
