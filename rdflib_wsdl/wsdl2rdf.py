from rdflib import Graph, URIRef, BNode, RDF, RDFS, Literal, IdentifiedNode, XSD
from typing import Mapping, Iterable, TypeVar, TypeAlias, Callable
from urllib.parse import urlparse, urlunparse
from .wsdl_components import Binding, BindingFaultReference, BindingMessageReference, BindingOperation, Description, ElementDeclaration, Endpoint, Interface, InterfaceFault, InterfaceFaultReference, InterfaceMessageReference, InterfaceOperation, Service, TypeDefinition, Extension, _WSDLComponent, MCM_ANY, MCM_NONE, MCM_OTHER, MCM_ELEMENT, BindingFault
from .shared import _ns_wsdl, _ns_wsdlx, _ns_wsdlrdf, _ns_wsoap, _ns_whttp, _ns_wrpc, _ns_sawsdl, _ns_xs, WHTTP, WSDL, WSDLX, WSDL_RDF, WSOAP, SAWSDL, name2qname
from .shared import MEP_inOnly, MEP_robustInOnly, MEP_inOut, MEP_inOptionalOut,MEP_outOnly, MEP_robustOutOnly, MEP_outIn, MEP_outOptionalIn

MESSAGECONTENTMODEL2URI = {MCM_ANY: WSDL.AnyContent,
                           MCM_NONE: WSDL.NoContent,
                           MCM_OTHER: WSDL.OtherContent,
                           MCM_ELEMENT: WSDL.ElementContent,
                           }

def _qname2rdfframes(namespace: str, local_name: str) -> Iterable:
    """
    Described in `https://www.w3.org/TR/wsdl20-rdf/#interface`_ Table 2-2
    """
    yield RDF.type, WSDL.QName
    yield WSDL.localName, Literal(local_name)
    yield WSDL.namespace, URIRef(namespace)

#def generateRDF(basedescription: Description) -> Graph:
#    g = Graph()
#    _map_description(g, basedescription)
#    return g

def _create_id(element: _WSDLComponent) -> URIRef:
    """`https://www.w3.org/TR/wsdl20/#wsdl-iri-references`_"""
    fragment = element.fragment_identifier
    return _qname2id(element.targetNamespace, fragment)

def _qname2id(namespace: str, name: str) -> URIRef:
    """`https://www.w3.org/TR/wsdl20/#wsdl-iri-references`_"""
    q = urlparse(namespace)
    return URIRef(urlunparse(q._replace(fragment = name)))

def _messageLabel2URI(message_label: str, message_exchange_pattern: str,
                      ) -> URIRef:
    """`https://www.w3.org/TR/wsdl20-rdf/#meps`_"""
    if message_exchange_pattern == MEP_inOnly:
        return URIRef("http://www.w3.org/ns/wsdl/in-only#In")
    elif message_exchange_pattern == MEP_robustInOnly:
        return URIRef("http://www.w3.org/ns/wsdl/robust-in-only#In")
    elif message_exchange_pattern == MEP_inOut:
        if message_label.upper() == "IN":
            return URIRef("http://www.w3.org/ns/wsdl/in-out#In")
        else:
            return URIRef("http://www.w3.org/ns/wsdl/in-out#Out")
    elif message_exchange_pattern == MEP_inOptionalOut:
        if message_label.upper() == "IN":
            return URIRef("http://www.w3.org/ns/wsdl/in-opt-out#In")
        else:
            return URIRef("http://www.w3.org/ns/wsdl/in-opt-out#Out")
    elif message_exchange_pattern == MEP_outOnly:
        return URIRef("http://www.w3.org/ns/wsdl/out-only#Out")
    elif message_exchange_pattern == MEP_robustOutOnly:
        return URIRef("http://www.w3.org/ns/wsdl/robust-out-only#Out")
    elif message_exchange_pattern == MEP_outIn:
        if message_label.upper() == "IN":
            return URIRef("http://www.w3.org/ns/wsdl/out-in#In")
        else:
            return URIRef("http://www.w3.org/ns/wsdl/out-in#Out")
    elif message_exchange_pattern == MEP_outOptionalIn:
        if message_label.upper() == "IN":
            return URIRef("http://www.w3.org/ns/wsdl/out-opt-in#In")
        else:
            return URIRef("http://www.w3.org/ns/wsdl/out-opt-in#Out")
    raise NotImplementedError(message_label, message_exchange_pattern)

_C = TypeVar("_C")
WSDLMAPPER: TypeAlias = Callable[[Graph, _C], None]

class MapperWSDL2RDF:
    def __init__(self,
                 ext_binding: Iterable[WSDLMAPPER[Binding]] = [],
                 ext_bindingOperation: Iterable[WSDLMAPPER[BindingOperation]] = [],
                 ext_bindingFault: Iterable[WSDLMAPPER[BindingFault]] = [],
                 ext_bindingMessageReference: Iterable[WSDLMAPPER[BindingMessageReference]] = [],
                 ext_bindingFaultReference: Iterable[WSDLMAPPER[BindingFaultReference]] = [],
                 ext_endpoint: Iterable[WSDLMAPPER[Endpoint]] = [],
                 ext_interfaceOperation: Iterable[WSDLMAPPER[InterfaceOperation]] = []
                 ):
        """Register all extensions"""
        self.ext_binding = list(ext_binding)
        self.ext_bindingOperation = list(ext_bindingOperation)
        self.ext_bindingFault = list(ext_bindingFault)
        self.ext_bindingMessageReference = list(ext_bindingMessageReference)
        self.ext_bindingFaultReference = list(ext_bindingFaultReference)
        self.ext_endpoint = list(ext_endpoint)
        self.ext_interfaceOperation = list(ext_interfaceOperation)

    def __call__(self, basedescription: Description) -> Graph:
        g = Graph()
        self._map_description(g, basedescription)
        return g

    def _map_description(self, g: Graph, description: Description) -> None:
        """`https://www.w3.org/TR/wsdl20-rdf/#description`_"""
        elemid = _create_id(description)
        g.add((elemid, RDF.type, WSDL.Description))
        for interface in description.interfaces:
            self._map_interface(g, interface)
        for binding in description.bindings:
            self._map_binding(g, binding)
        for service in description.services:
            self._map_service(g, service)
        #ignore type_definitions, element_declarations

    def _map_interface(self, g: Graph, interface: Interface) -> None:
        elemid = _create_id(interface)
        parentid = _create_id(interface.parent)
        g.add((elemid, RDF.type, WSDL.Interface))
        g.add((parentid, WSDL.interface, elemid))
        g.add((elemid, RDFS.label, Literal(interface.name)))
        for other_interface in interface.extended_interfaces:
            otherid = _create_id(other_interface)
            g.add((elemid, WSDL.extends, otherid))
        for interface_operation in interface.interface_operations:
            self._map_interfaceOperation(g, interface_operation)
        for interface_fault in interface.interface_faults:
            self._map_interfaceFault(g, interface_fault)

    def _map_interfaceOperation(self, g: Graph,
                                interfaceOperation: InterfaceOperation) -> None:
        """`https://www.w3.org/TR/wsdl20-rdf/#table2-4`_"""
        elemid = _create_id(interfaceOperation)
        parentid = _create_id(interfaceOperation.parent)
        g.add((elemid, RDF.type, WSDL.InterfaceOperation))
        g.add((parentid, WSDL.interfaceOperation, elemid))
        g.add((elemid, RDFS.label, Literal(interfaceOperation.name)))
        for imr in interfaceOperation.interface_message_references:
            self._map_interfaceMessageReference(g, imr)
        for ifr in interfaceOperation.interface_fault_references:
            self._map_interfaceFaultReference(g, ifr)
        mep = interfaceOperation.message_exchange_pattern
        g.add((elemid, WSDL.messageExchangePattern, URIRef(mep)))
        for style in interfaceOperation.style:
            g.add((elemid, WSDL.operationStyle, URIRef(style)))
        for extmap in self.ext_interfaceOperation:
            extmap(g, interfaceOperation)

    def _map_interfaceMessageReference(
            self, g: Graph,
            interfaceMessageReference: InterfaceMessageReference,
            ) -> None:
        """`https://www.w3.org/TR/wsdl20-rdf/#table2-6`_"""
        elemid = _create_id(interfaceMessageReference)
        parentid = _create_id(interfaceMessageReference.parent)
        g.add((elemid, RDF.type, WSDL.InterfaceMessageReference))
        g.add((parentid, WSDL.interfaceMessageReference, elemid))
        elementDeclaration_id = BNode()
        g.add((elemid, WSDL.elementDeclaration, elementDeclaration_id))
        mcm = interfaceMessageReference.message_content_model
        if mcm == MCM_ELEMENT:
            elem_ns, elem_name = interfaceMessageReference.element_declaration
            for prop, obj in _qname2rdfframes(elem_ns, elem_name):
                g.add((elementDeclaration_id, prop, obj))
        g.add((elemid, WSDL.messageContentModel, MESSAGECONTENTMODEL2URI[mcm]))
        if interfaceMessageReference.direction == "in":
            g.add((elemid, RDF.type, WSDL.InputMessage))
        else:
            g.add((elemid, RDF.type, WSDL.OutputMessage))
        ml_id = _messageLabel2URI(
                interfaceMessageReference.message_label,
                interfaceMessageReference.parent.message_exchange_pattern)
        g.add((elemid, WSDL.messageLabel, ml_id))

    def _map_interfaceFaultReference(
            self, g: Graph,
            interfaceFaultReference: InterfaceFaultReference,
            ) -> None:
        """`https://www.w3.org/TR/wsdl20-rdf/#table2-7`_"""
        elemid = _create_id(interfaceFaultReference)
        parentid = _create_id(interfaceFaultReference.parent)
        g.add((elemid, RDF.type, WSDL.InterfaceFaultReference))
        g.add((parentid, WSDL.interfaceFaultReference, elemid))
        interFault = interfaceFaultReference.interface_fault
        g.add((elemid, WSDL.interfaceFault, _create_id(interFault)))
        if interfaceFaultReference.direction == "in":
            g.add((elemid, RDF.type, WSDL.InputMessage))
        else:
            g.add((elemid, RDF.type, WSDL.OutputMessage))
        ml_id = _messageLabel2URI(
                interfaceFaultReference.message_label,
                interfaceFaultReference.parent.message_exchange_pattern,
                )
        g.add((elemid, WSDL.messageLabel, ml_id))


    def _map_interfaceFault(
            self, g: Graph,
            interfaceFault: InterfaceFault,
            ) -> None:
        """`https://www.w3.org/TR/wsdl20-rdf/#table2-5`_"""
        elemid = _create_id(interfaceFault)
        parentid = _create_id(interfaceFault.parent)
        g.add((elemid, RDF.type, WSDL.InterfaceFault))
        g.add((parentid, WSDL.interfaceFault, elemid))
        g.add((elemid, RDFS.label, Literal(interfaceFault.name)))
        elementDeclaration_id = BNode()
        g.add((elemid, WSDL.elementDeclaration, elementDeclaration_id))
        for prop, obj in _qname2rdfframes(*interfaceFault.element_declaration):
            g.add((elementDeclaration_id, prop, obj))
        g.add((elemid, WSDL.messageContentModel,
               MESSAGECONTENTMODEL2URI[interfaceFault.message_content_model]))

    def _map_binding(self, g: Graph, binding: Binding) -> None:
        """`https://www.w3.org/TR/wsdl20-rdf/#table2-8`_"""
        elemid = _create_id(binding)
        parentid = _create_id(binding.parent)
        g.add((elemid, RDF.type, WSDL.Binding))
        g.add((parentid, WSDL.binding, elemid))
        g.add((elemid, RDFS.label, Literal(binding.name)))
        interfaceid = _create_id(binding.interface)
        g.add((elemid, WSDL.binds, interfaceid))
        g.add((elemid, RDF.type, URIRef(binding.type)))
        for bo in binding.binding_operations:
            self._map_bindingOperation(g, bo)
        for bf in binding.binding_faults:
            self._map_bindingFault(g, bf)
        for extmap in self.ext_binding:
            extmap(g, binding)

    def _map_bindingOperation(
            self, g: Graph,
            bindingOperation: BindingOperation) -> None:
        """`https://www.w3.org/TR/wsdl20-rdf/#table2-9`_"""
        elemid = _create_id(bindingOperation)
        parentid = _create_id(bindingOperation.parent)
        g.add((elemid, RDF.type, WSDL.BindingOperation))
        g.add((parentid, WSDL.bindingOperation, elemid))
        interid = _create_id(bindingOperation.interface_operation)
        g.add((elemid, WSDL.binds, interid))
        for bmr in bindingOperation.binding_message_references:
            self._map_bindingMessageReference(g, bmr)

        for bfr in bindingOperation.binding_fault_references:
            self._map_bindingFaultReference(g, bfr)
        for extmap in self.ext_bindingOperation:
            extmap(g, bindingOperation)

    def _map_bindingMessageReference(
            self, g: Graph,
            bindingMessageReference: BindingMessageReference) -> None:
        """`https://www.w3.org/TR/wsdl20-rdf/#table2-12`_"""
        elemid = _create_id(bindingMessagetReference)
        parentid = _create_id(bindingMessageReference.parent)
        g.add((elemid, RDF.type, WSDL.BindingMessageReference))
        g.add((parentid, WSDL.bindingMessageReference, elemid))

        imr_id = _create_id(bindingMessageReference.interface_message_reference)
        g.add((elemid, WSDL.binds, imr_id))
        for extmap in self.ext_bindingMessageReference:
            extmap(g, bindingMessageReference)

    def _map_bindingFaultReference(
            self, g: Graph,
            bindingFaultReference: BindingFaultReference) -> None:
        """`https://www.w3.org/TR/wsdl20-rdf/#table2-11`_"""
        elemid = _create_id(bindingFaultReference)
        parentid = _create_id(bindingFaultReference.parent)
        g.add((elemid, RDF.type, WSDL.BindingFaultReference))
        g.add((parentid, WSDL.bindingFaultReference, elemid))

        ifr_id = _create_id(bindingFaultReference.interface_fault_reference)
        g.add((elemid, WSDL.binds, ifr_id))
        for extmap in self.ext_bindingFaultReference:
            extmap(g, bindingFaultReference)

    def _map_bindingFault(self, g: Graph, bindingFault: BindingFault) -> None:
        """`https://www.w3.org/TR/wsdl20-rdf/#table2-10`_"""
        elemid = _create_id(bindingFault)
        parentid = _create_id(bindingFault.parent)
        g.add((elemid, RDF.type, WSDL.BindingFault))
        g.add((parentid, WSDL.bindingFault, elemid))
        interfaceFault_id = _create_id(bindingFault.interface_fault)
        g.add((elemid, WSDL.binds, interfaceFault_id))
        for extmap in self.ext_bindingFault:
            extmap(g, bindingFault)

    def _map_service(self, g: Graph, service: Service) -> None:
        """`https://www.w3.org/TR/wsdl20-rdf/#table2-13`_"""
        elemid = _create_id(service)
        parentid = _create_id(service.parent)
        g.add((elemid, RDF.type, WSDL.Service))
        g.add((parentid, WSDL.service, elemid))
        g.add((elemid, RDFS.label, Literal(service.name)))
        g.add((elemid, WSDL.implements, _create_id(service.interface)))
        for endpoint in service.endpoints:
            self._map_endpoint(g, endpoint)

    def _map_endpoint(self, g: Graph, endpoint: Endpoint) -> None:
        """`https://www.w3.org/TR/wsdl20-rdf/#table2-14`_"""
        elemid = _create_id(endpoint)
        parentid = _create_id(endpoint.parent)
        g.add((elemid, RDF.type, WSDL.Endpoint))
        g.add((parentid, WSDL.endpoint, elemid))
        g.add((elemid, RDFS.label, Literal(endpoint.name)))
        g.add((elemid, WSDL.usesBinding, _create_id(endpoint.binding)))
        g.add((elemid, WSDL.address, URIRef(endpoint.address)))
        for extmap in self.ext_endpoint:
            extmap(g, endpoint)


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

def _ext_http_bindingMessageReference(g: Graph, bindingMessageReference: BindingMessageReference) -> None:
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
        _ext_http_bindingMessageReference,
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
generateRDF = MapperWSDL2RDF(
        ext_binding = default_extensions_binding,
        ext_bindingOperation = default_extensions_bindingOperation,
        ext_bindingFault = default_extensions_bindingFault,
        ext_bindingMessageReference=default_extensions_bindingMessageReference,
        ext_bindingFaultReference = default_extensions_bindingFaultReference,
        ext_endpoint = default_extensions_endpoint,
        ext_interfaceOperation = default_extension_interfaceOperation,
        )
