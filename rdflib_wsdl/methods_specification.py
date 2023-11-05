"""This document implements all mapping methods specified in 
`https://www.w3.org/TR/wsdl20-rdf/`_
"""
from xml.etree import ElementTree as ET
from rdflib import Graph, URIRef

def xmlschema2rdf(etreeNode: ET.ElementTree) -> Graph:
    pass

def wsdlCoreElements2rdf() -> Graph:
    raise NotImplementedError()

def MapDescription(qname: str) -> Graph:
    """As described in `https://www.w3.org/TR/wsdl20-rdf/#description`_
    only return the information that given 'description' is a description.
    All information about properties are mapped by them.
    """
    

def wsdlQNameResolution(targetNamespace: str, wsdl_property: str) -> URIRef:
    """Generates
    Specified in `https://www.w3.org/TR/wsdl20/#qnameres`_
    The specified :term:`WSDL Core Properties` are 'interface', 'binding'
    and 'service' and originate in 'Description' as 
    the :term:`top-level WSDL Component`
    Despite originating from the :term:`top-level WSDL Component` too,
    'types' and 'elements' are currently not mapped.

    :param target_namespace: :term:`Namespace name` as determined
        in the parent 'Description'
    :param wsdl_property: This is one of the specified properties 'interface'
        'binding' or 'service'. all non mapped properties will result in 
        a KeyError
    :raises: KeyError
    """
    mapped_propertyname = {'interface': 'Interface',
                           'binding': 'Binding',
                           'service': 'Service'}[wsdl_property]
    return "%s.%s(%s)" % (target_namespace, wsdl_property, "")
