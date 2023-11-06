from rdflib import Graph, URIRef, BNode, RDF, RDFS, Literal, IdentifiedNode, XSD
from typing import Mapping, Iterable, TypeVar, TypeAlias, Callable, Optional
from urllib.parse import urlparse, urlunparse
from ..wsdl_components import Binding, BindingFaultReference, BindingMessageReference, BindingOperation, Description, ElementDeclaration, Endpoint, Interface, InterfaceFault, InterfaceFaultReference, InterfaceMessageReference, InterfaceOperation, Service, TypeDefinition, Extension, _WSDLComponent, MCM_ANY, MCM_NONE, MCM_OTHER, MCM_ELEMENT, BindingFault
from ..shared import _ns_wsdl, _ns_wsdlx, _ns_wsdlrdf, _ns_wsoap, _ns_whttp, _ns_wrpc, _ns_sawsdl, _ns_xs, WHTTP, WSDL, WSDLX, WSDL_RDF, WSOAP, SAWSDL, name2qname
from ..shared import MEP_inOnly, MEP_robustInOnly, MEP_inOut, MEP_inOptionalOut,MEP_outOnly, MEP_robustOutOnly, MEP_outIn, MEP_outOptionalIn
from .class_MapperWSDL2RDF import MESSAGECONTENTMODEL2URI, _create_id, _qname2id, _messageLabel2URI, _qname2rdfframes, WSDLMAPPER, extension_parser_data
from dataclasses import dataclass, field

@dataclass
class parser(extension_parser_data):
    binding: Optional[WSDLMAPPER[Binding]] = field(default=None)
    bindingOperation: Optional[WSDLMAPPER[BindingOperation]]\
             = field(default=None)
    bindingFault: Optional[WSDLMAPPER[BindingFault]]\
             = field(default=None)
    bindingMessageReference: Optional[WSDLMAPPER[BindingMessageReference]]\
             = field(default=None)
    bindingFaultReference: Optional[WSDLMAPPER[BindingFaultReference]]\
             = field(default=None)
    endpoint: Optional[WSDLMAPPER[Endpoint]] = field(default=None)
    interfaceOperation: Optional[WSDLMAPPER[InterfaceOperation]]\
             = field(default=None)


def _ext_soap_map_binding(g: Graph, binding: Binding) -> None:
    """`https://www.w3.org/TR/wsdl20-rdf/#table2-18`_"""
    elemid = _create_id(binding)
    soap_underlying_protocol = binding.get(_ns_wsoap, "protocol")
    if soap_underlying_protocol is None:
        return
    else:
        g.add((elemid, WSOAP.protocol, URIRef(soap_underlying_protocol)))
    try:
        mep_default = binding.get(_ns_wsoap, "soapMEP", as_qname=True)
    except KeyError:
        pass
    else:
        g.add((elemid, WSOAP.defaultSoapMEP, mep_default))
    try:
        soap_version = binding.get(_ns_wsoap, "")
    except KeyError:
        g.add((elemid, WSOAP.version, Literal("1.2")))
    else:
        g.add((elemid, WSOAP.version, Literal(soap_version)))
    _map_soap_module(g, elemid, binding)

def _ext_soap_map_bindingOperation(
        g: Graph, bindingOperation: BindingOperation,
        ) -> None:
    """`https://www.w3.org/TR/wsdl20-rdf/#table2-19`_"""
    elemid = _create_id(bindingOperation)
    try:
        action = bindingOperation.get(_ns_wsoap, "action")
    except KeyError:
        pass
    else:
        raise NotImplementedError()
        g.add((elemid, WSOAP.action, ))
    try:
        mep = bindingOperation.get(_ns_wsoap, "mep")
    except KeyError:
        pass
    else:
        g.add((elemid, WSOAP.soapMEP, URIRef(mep)))
    _map_soap_module(g, elemid, bindingOperation)

def _ext_soap_map_bindingFault(
        g: Graph, bindingFault: BindingFault,
        ) -> None:
    """`https://www.w3.org/TR/wsdl20-rdf/#table2-20`_"""
    elemid = _create_id(bindingFault)
    soap_fault_code = bindingFault.get(_ns_wsoap, "code", as_qname=True)
    if soap_fault_code is not None:
        code_ns, code_name = soap_fault_code
        q = BNode()
        for prop, obj in _qname2rdfframes(code_ns, code_name):
            g.add((q, prop, obj))
        g.add((elemid, WSOAP.faultCode, q))
    try:
        soap_fault_subcode = bindingFault.get(_ns_wsoap, "subcode", as_qname=True)
    except KeyError:
        pass
    else:
        raise NotImplementedError()
    _map_soap_module(g, elemid, bindingFault)
    _map_soap_headerBlock(g, elemid, bindingFault)

def _ext_soap_map_bindingMessageReference(
        g: Graph, bindingMessageReference: BindingMessageReference,
        ) -> None:
    """`https://www.w3.org/TR/wsdl20-rdf/#table2-21`_"""
    elemid = _create_id(bindingMessageReference)
    _map_soap_module(g, elemid, bindingMessageReference)
    _map_soap_headerBlock(g, elemid, bindingMessageReference)

def _ext_soap_map_bindingFaultReference(
        g: Graph, bindingFaultReference: BindingFaultReference,
        ) -> None:
    """`https://www.w3.org/TR/wsdl20-rdf/#table2-22`_"""
    reqSOAPMod = bindingFaultReference.get(_ns_wsoap, "requiresSOAPModule")
    offersSOAPMod = bindingFaultReference.get(_ns_wsoap, "offersSOAPModule")
    if reqSOAPMod is not None or offersSOAPMod is not None:
        raise NotImplementedError()
        _map_soap_module(g)

def _map_soap_module(g: Graph, elemid, elem) -> None:
    """`https://www.w3.org/TR/wsdl20-rdf/#table2-23`_"""
    try:
        reqSOAPMod = elem.get(_ns_wsoap, "requiresSOAPModule")
    except KeyError:
        reqSOAPMod = None
    try:
        offersSOAPMod = elem.get(_ns_wsoap, "offersSOAPModule")
    except KeyError:
        offersSOAPMod = None
    if reqSOAPMod is None and offersSOAPMod is None:
        return
    raise NotImplementedError()

def _map_soap_headerBlock(g: Graph, elemid, elem) -> None:
    """`https://www.w3.org/TR/wsdl20-rdf/#table2-24`_"""
    try:
        offersSOAPHeader = elem.get(_ns_wsoap, "offersHeader")
    except KeyError:
        offersSOAPHeader = None
    try:
        reqSOAPHeader = elem.get(_ns_wsoap, "requiresHeader")
    except KeyError:
        reqSOAPHeader = None
    if offersSOAPHeader is None and reqSOAPHeader is None:
        return
    raise NotImplementedError()

soapExtension = parser(
        binding = _ext_soap_map_binding,
        bindingOperation = _ext_soap_map_bindingOperation,
        bindingFault = _ext_soap_map_bindingFault,
        bindingMessageReference = _ext_soap_map_bindingMessageReference,
        bindingFaultReference = _ext_soap_map_bindingFaultReference,
        )

def _ext_http_binding(g: Graph, binding: Binding) -> None:
    """`https://www.w3.org/TR/wsdl20-rdf/#table2-25`_"""
    elemid = _create_id(binding)
    try:
        use_cookies = binding.get(_ns_whttp, "BindingUsingHTTPCookies")
    except KeyError:
        pass
    else:
        if use_cookies.upper() == "TRUE":
            g.add((elemid, RDF.type, WHTTP.BindingUsesHTTPCookies))
    try:
        coding = binding.get(_ns_whttp, "defaultContentEncoding")
    except KeyError:
        pass
    else:
        g.add((elemid, WHTTP.defaultContentEncoding, Literal(coding)))
    try:
        method = binding.get(_ns_whttp, "defaultMethod")
    except KeyError:
        pass
    else:
        g.add((elemid, WHTTP.defaultMethod, Literal(method)))
    try:
        separator = binding.get(_ns_whttp, "defaultQueryParameterSeparator")
    except KeyError:
        g.add((elemid, WHTTP.defaultQueryParameterSeparator, Literal("&")))
    else:
        g.add((elemid, WHTTP.defaultQueryParameterSeparator, Literal(separator)))

def _add_as_literal(g: Graph, elem, elemid, xml_namespace, xml_location, rdf_property,
                    **literal_kwargs):
    """Adds value from xml-thingies as rdf triple if possible.
    Just a little helper for shorter code.
    """
    try:
        value = elem.get(xml_namespace, xml_location)
    except KeyError:
        pass
    else:
        g.add((elemid, rdf_property, Literal(value, **literal_kwargs)))

def _ext_http_bindingOperation(g: Graph, bindingOperation: BindingOperation) -> None:
    """`https://www.w3.org/TR/wsdl20-rdf/#table2-26`_"""
    elemid = _create_id(bindingOperation)
    _add_as_literal(g, bindingOperation, elemid, _ns_whttp,
                    "location", WHTTP.location)
    _add_as_literal(g, bindingOperation, elemid, _ns_whttp,
                    "defaultContentEncoding", WHTTP.defaultContentEncoding)
    _add_as_literal(g, bindingOperation, elemid, _ns_whttp,
                    "inputSerialization", WHTTP.inputSerialization)
    _add_as_literal(g, bindingOperation, elemid, _ns_whttp,
                    "outputSerialization", WHTTP.outputSerialization)
    _add_as_literal(g, bindingOperation, elemid, _ns_whttp,
                    "faultSerialization", WHTTP.faultSerialization)
    try:
        ignore_uncited = bindingOperation.get(_ns_whttp,
                                              "locationIgnoreUncited")
    except KeyError:
        pass
    else:
        g.add((elemid, WHTTP.locationIgnoreUncited,
               Literal(ignore_uncited, datatype=XSD.boolean)))
    try:
        method = bindingOperation.get(_ns_whttp, "method")
    except KeyError:
        pass
    else:
        try:
            g.add((elemid, WHTTP.method, URIRef(method)))
        except Exception:
            raise Exception(g, method)
    _add_as_literal(g, bindingOperation, elemid, _ns_whttp,
                    "queryParameterSeparator", WHTTP.queryParameterSeparator)


def _ext_http_bindingFault(g: Graph, bindingFault: BindingFault) -> None:
    """`https://www.w3.org/TR/wsdl20-rdf/#table2-27`_"""
    elemid = _create_id(bindingFault)
    try:
        error_code = bindingFault.get(_ns_whttp, "errorCode")
    except KeyError:
        pass
    else:
        if error_code.upper() != "ANY":
            g.add((elemid, WHTTP.errorCode,
                   Literal(error_code, datatype=XSD.int)))
    _add_as_literal(g, bindingFault, elemid, _ns_whttp,
                    "contentEncoding", WHTTP.contentEncoding)
    _map_http_headerBlock(g, elemid, bindingFault)

def _ext_http_map_bindingMessageReference(g: Graph, bindingMessageReference: BindingMessageReference) -> None:
    """`https://www.w3.org/TR/wsdl20-rdf/#table2-28`_"""
    elemid = _create_id(bindingMessageReference)
    _add_as_literal(g, bindingFault, elemid, _ns_whttp,
                    "contentEncoding", WHTTP.contentEncoding)
    _map_http_headerBlock(g, elemid, bindingMessageReference)

def _ext_http_endpoint(g: Graph, endpoint: Endpoint) -> None:
    """`https://www.w3.org/TR/wsdl20-rdf/#table2-29`_"""
    elemid = _create_id(endpoint)
    try:
        auth_realm = endpoint.get(_ns_whttp, "authenticationRealm")
    except KeyError:
        pass
    else:
        g.add((elemid, WHTTP.authentificationRealm, Literal(auth_realm)))
    try:
        auth_scheme = endpoint.get(_ns_whttp, "authenticationScheme")
    except KeyError:
        pass
    else:
        g.add((elemid, WHTTP.authentificationScheme, Literal(auth_scheme)))

def _map_http_headerBlock(g: Graph, parentid: IdentifiedNode, parent) -> None:
    """`https://www.w3.org/TR/wsdl20-rdf/#table2-30`_"""
    try:
        offersHeader = parent.get(_ns_whttp, "offersHeader")
    except KeyError:
        offersHeader = None
    try:
        reqHeader = parent.get(_ns_whttp, "requiresHeader")
    except KeyError:
        reqHeader = None
    if offersHeader is None and reqHeader is None:
        return
    raise NotImplementedError()
    if required:
        g.add((parentid, WHTTP.requiresHeader, elemid))
    else:
        g.add((parentid, WHTTP.offersHeader, elemid))
    g.add((elemid, WSDL.typeDefinition, qnameid))

def _ext_sawsdl_interfaceOperation(g: Graph, interfaceOperation: InterfaceOperation) -> None:
    try:
        safe = interfaceOperation.get(_ns_wsdlx, "safe")
    except KeyError:
        pass
    else:
        if safe.upper() == "TRUE":
            elemid = _create_id(interfaceOperation)
            g.add((elemid, SAWSDL.modelReference, WSDLX.SafeInteraction))

httpExtension = parser(
        binding = _ext_http_binding,
        bindingOperation = _ext_http_bindingOperation,
        bindingFault = _ext_http_bindingFault,
        bindingMessageReference = _ext_http_map_bindingMessageReference,
        endpoint = _ext_http_endpoint,
        )

sawsdlExtension = parser(interfaceOperation = _ext_sawsdl_interfaceOperation)

default_extensions_binding = [
        _ext_soap_map_binding,
        _ext_http_binding,
        ]
default_extensions_bindingOperation = [
        _ext_soap_map_bindingOperation,
        _ext_http_bindingOperation,
        ]
default_extensions_bindingFault = [
        _ext_soap_map_bindingFault,
        _ext_http_bindingFault,
        ]
default_extensions_bindingMessageReference = [
        _ext_soap_map_bindingMessageReference,
        _ext_http_map_bindingMessageReference,
        ]
default_extensions_bindingFaultReference = [
        _ext_soap_map_bindingFaultReference,
        ]
default_extensions_endpoint = [
        _ext_http_endpoint,
        ]
default_extension_interfaceOperation = [
        _ext_sawsdl_interfaceOperation,
        ]
