"""
Generell information about extensibility in `https://www.w3.org/TR/wsdl/#language-extensibility`_
:TODO: http extensions are missing, see `https://www.w3.org/TR/wsdl20-rdf/#httpbinding`_
"""
from rdflib.term import Node, IdentifiedNode, Literal, URIRef
from rdflib import Graph, BNode
from typing import Callable, Tuple, Optional
from collections.abc import Mapping, Iterable, MutableMapping
BINDING_EXTENSIONS:\
        MutableMapping[str, Callable[[IdentifiedNode, Mapping[str, str]],
                                     Graph]] = {}
"""All extension for :term:`wsdl binding`."""
BINDING_FAULT_EXTENSIONS:\
        MutableMapping[str, Callable[[IdentifiedNode, Mapping[str, str]],
                                     Graph]] = {}
"""All extensions for :term:`wsdl binding fault`"""
BINDING_OPERATION_EXTENSIONS:\
        MutableMapping[str, Callable[[IdentifiedNode, Mapping[str, str]],
                                     Graph]] = {}
"""All extensions for :term:`wsdl binding operation`"""
MESSAGE_REFERENCE_EXTENSIONS:\
        MutableMapping[str, Callable[[IdentifiedNode, Mapping[str, str]],
                                     Graph]] = {}
"""All extensions for :term:`wsdl message reference`"""
MESSAGE_FAULT_EXTENSIONS:\
        MutableMapping[str, Callable[[IdentifiedNode, Mapping[str, str]],
                                     Graph]] = {}
"""All extensions for :term:`wsdl message fault`"""
ENDPOINT_EXTENSIONS:\
        MutableMapping[str, Callable[[IdentifiedNode, Mapping[str, str]],
                                     Graph]] = {}
"""All extensions for :term:`wsdl endpoint`"""

from ..shared import _ns_wsoap, name2qname, WSOAP

def extension_WSDL_SOAP_Binding(
        bindingNode: IdentifiedNode,
        soapData: Mapping[str, str],
        namespaces: Mapping[str, str],
        defaultNamespace: str,
        ) -> Graph:
    """
    Specified in `https://www.w3.org/TR/wsdl20-rdf/#soapbinding`_
    More information see `https://www.w3.org/TR/2007/REC-wsdl20-adjuncts-20070626/#soap-binding`_
    """
    g = Graph()
    version = soapData.get("version", "1.2")
    protocol = soapData["protocol"]
    try:
        mep = soapData["soapMEP"]
    except KeyError:
        pass
    else:
        raise NotImplementedError()
    g.add((bindingNode, WSOAP.version, Literal(version)))
    g.add((bindingNode, WSOAP.protocol, URIRef(protocol)))
    return g
BINDING_EXTENSIONS[_ns_wsoap] = extension_WSDL_SOAP_Binding

def extension_WSDL_SOAP_BindingOperation(
        bindingNode: IdentifiedNode,
        soapData: Mapping[str, str],
        namespaces: Mapping[str, str],
        defaultNamespace: str,
        ) -> Graph:
    """
    Specified in `https://www.w3.org/TR/wsdl20-rdf/#soapbinding`_
    More information see `https://www.w3.org/TR/2007/REC-wsdl20-adjuncts-20070626/#soap-binding`_
    """
    g = Graph()
    mep = soapData["mep"]
    g.add((bindingNode, WSOAP.soapMEP, URIRef(mep)))
    return g
BINDING_OPERATION_EXTENSIONS[_ns_wsoap] = extension_WSDL_SOAP_BindingOperation

def extension_WSDL_SOAP_BindingFault(
        bindingNode: IdentifiedNode,
        soapData: Mapping[str, str],
        namespaces: Mapping[str, str],
        defaultNamespace: str,
        ) -> Graph:
    """
    Specified in `https://www.w3.org/TR/wsdl20-rdf/#soapbinding`_
    More information see `https://www.w3.org/TR/2007/REC-wsdl20-adjuncts-20070626/#soap-binding`_
    """
    g = Graph()
    try:
        code = soapData["code"]
    except KeyError:
        pass
    else:
        elem = BNode()
        g.add((bindingNode, WSOAP.faultCode, elem))
        for pred, obj in qname2rdfframes(code, namespaces,
                                         defaultNamespace):
            g.add((elem, pred, obj))
    try:
        subcode = soapData["subcode"]
    except KeyError:
        pass
    else:
        raise NotImplementedError()
    return g
BINDING_FAULT_EXTENSIONS[_ns_wsoap] = extension_WSDL_SOAP_BindingFault

def extension_WSDL_SOAP_MessageReference(
        bindingNode: IdentifiedNode,
        soapData: Mapping[str, str],
        namespaces: Mapping[str, str],
        defaultNamespace: str,
        ) -> Graph:
    """
    Specified in `https://www.w3.org/TR/wsdl20-rdf/#soapbinding`_
    More information see `https://www.w3.org/TR/2007/REC-wsdl20-adjuncts-20070626/#soap-binding`_
    """
    raise NotImplementedError()
    g = Graph()
    return g
MESSAGE_REFERENCE_EXTENSIONS[_ns_wsoap] = extension_WSDL_SOAP_MessageReference

def extension_WSDL_SOAP_MessageFault(
        bindingNode: IdentifiedNode,
        soapData: Mapping[str, str],
        namespaces: Mapping[str, str],
        defaultNamespace: str,
        ) -> Graph:
    """
    Specified in `https://www.w3.org/TR/wsdl20-rdf/#soapbinding`_
    More information see `https://www.w3.org/TR/2007/REC-wsdl20-adjuncts-20070626/#soap-binding`_
    """
    raise NotImplementedError()
    g = Graph()
    return g
MESSAGE_FAULT_EXTENSIONS[_ns_wsoap] = extension_WSDL_SOAP_MessageFault
