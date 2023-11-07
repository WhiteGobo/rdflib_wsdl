from rdflib import Graph, URIRef, BNode, RDF, RDFS, Literal,\
        IdentifiedNode, XSD
from typing import Mapping, Iterable, TypeVar, TypeAlias, Callable, Optional
from urllib.parse import urlparse, urlunparse
from ..wsdl_components import Binding, BindingFaultReference,\
        BindingMessageReference, BindingOperation, Description,\
        ElementDeclaration, Endpoint, Interface, InterfaceFault,\
        InterfaceFaultReference, InterfaceMessageReference,\
        InterfaceOperation, Service, TypeDefinition, Extension,\
        _WSDLComponent, MCM_ANY, MCM_NONE, MCM_OTHER, MCM_ELEMENT, BindingFault
from ..shared import _ns_wsdl, _ns_wsdlx, _ns_wsdlrdf, _ns_wsoap, _ns_whttp,\
        _ns_wrpc, _ns_sawsdl, _ns_xs, WHTTP, WSDL, WSDLX, WSDL_RDF, WSOAP,\
        SAWSDL, name2qname,\
        MEP_inOnly, MEP_robustInOnly, MEP_inOut, MEP_inOptionalOut,\
        MEP_outOnly, MEP_robustOutOnly, MEP_outIn, MEP_outOptionalIn

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

class extension_parser_data:
    binding: Optional[WSDLMAPPER[Binding]]
    bindingOperation: Optional[WSDLMAPPER[BindingOperation]]
    bindingFault: Optional[WSDLMAPPER[BindingFault]]
    bindingMessageReference: Optional[WSDLMAPPER[BindingMessageReference]]
    bindingFaultReference: Optional[WSDLMAPPER[BindingFaultReference]]
    endpoint: Optional[WSDLMAPPER[Endpoint]]
    interfaceOperation: Optional[WSDLMAPPER[InterfaceOperation]]
    service: Optional[WSDLMAPPER[Service]]
    description: Optional[WSDLMAPPER[Description]]
    interfaceMessageReference: Optional[WSDLMAPPER[InterfaceMessageReference]]
    interfaceFaultReference: Optional[WSDLMAPPER[InterfaceFaultReference]]
    interface: Optional[WSDLMAPPER[Interface]]
    interfaceFault: Optional[WSDLMAPPER[InterfaceFault]]


class MapperWSDL2RDF:
    @classmethod
    def create_with_parser_data(
            cls,
            ext_binding: Iterable[WSDLMAPPER[Binding]] = [],
            ext_bindingOperation: Iterable[WSDLMAPPER[BindingOperation]] = [],
            ext_bindingFault: Iterable[WSDLMAPPER[BindingFault]] = [],
            ext_bindingMessageReference:\
                    Iterable[WSDLMAPPER[BindingMessageReference]] = [],
            ext_bindingFaultReference:\
                    Iterable[WSDLMAPPER[BindingFaultReference]] = [],
            ext_endpoint: Iterable[WSDLMAPPER[Endpoint]] = [],
            ext_interfaceOperation:\
                    Iterable[WSDLMAPPER[InterfaceOperation]] = [],
            ext_interfaceMessageReference:\
                    Iterable[WSDLMAPPER[InterfaceMessageReference]] = [],
            ext_interfaceFaultReference:\
                    Iterable[WSDLMAPPER[InterfaceFaultReference]] = [],
            ext_service: Iterable[WSDLMAPPER[Service]] = [],
            ext_description:\
                    Iterable[WSDLMAPPER[Description]] = [],
            ext_interfaceFault:\
                    Iterable[WSDLMAPPER[InterfaceFault]] = [],
            additional_extensions: Iterable[extension_parser_data] = [],
            ) -> "MapperWSDL2RDF":
        """Creates a mapper with packed extensions. Use this for easy
        compliance with available :term:`plugins<parser plugin>`.
        """
        ext_description = list(ext_description)
        ext_interfaceMessageReference = list(ext_interfaceMessageReference)
        ext_interfaceFaultReference = list(ext_interfaceFaultReference)
        ext_interfaceFault = list(ext_interfaceFault)
        ext_service = list(ext_service)
        ext_binding = list(ext_binding)
        ext_bindingOperation = list(ext_bindingOperation)
        ext_bindingFault = list(ext_bindingFault)
        ext_bindingMessageReference = list(ext_bindingMessageReference)
        ext_bindingFaultReference = list(ext_bindingFaultReference)
        ext_endpoint = list(ext_endpoint)
        ext_interfaceOperation = list(ext_interfaceOperation)
        for add in additional_extensions:
            if add.description is not None:
                ext_description.append(add.description)
            if add.interfaceMessageReference is not None:
                ext_interfaceMessageReference.append(add.interfaceMessageReference)
            if add.interfaceFaultReference is not None:
                ext_interfaceFaultReference.append(add.interfaceFaultReference)
            if add.interfaceFault is not None:
                ext_interfaceFault.append(add.interfaceFault)
            if add.service is not None:
                ext_service.append(add.service)
            if add.binding is not None:
                ext_binding.append(add.binding)
            if add.bindingOperation is not None:
                ext_bindingOperation.append(add.bindingOperation)
            if add.bindingFault is not None:
                ext_bindingFault.append(add.bindingFault)
            if add.bindingMessageReference is not None:
                ext_bindingMessageReference.append(
                        add.bindingMessageReference)
            if add.bindingFaultReference is not None:
                ext_bindingFaultReference.append(add.bindingFaultReference)
            if add.endpoint is not None:
                ext_endpoint.append(add.endpoint)
            if add.interfaceOperation is not None:
                ext_interfaceOperation.append(add.interfaceOperation)
        return cls(
                ext_binding = ext_binding,
                ext_bindingOperation = ext_bindingOperation,
                ext_bindingFault = ext_bindingFault,
                ext_bindingMessageReference = ext_bindingMessageReference,
                ext_bindingFaultReference = ext_bindingFaultReference,
                ext_endpoint = ext_endpoint,
                ext_interfaceOperation = ext_interfaceOperation,
                ext_service=ext_service,
                ext_interfaceFaultReference = ext_interfaceFaultReference,
                ext_interfaceMessageReference = ext_interfaceMessageReference,
                ext_description = ext_description,
                ext_interfaceFault = ext_interfaceFault,
                )


    def __init__(
            self,
            ext_binding: Iterable[WSDLMAPPER[Binding]] = [],
            ext_bindingOperation: Iterable[WSDLMAPPER[BindingOperation]] = [],
            ext_bindingFault: Iterable[WSDLMAPPER[BindingFault]] = [],
            ext_bindingMessageReference:\
                    Iterable[WSDLMAPPER[BindingMessageReference]] = [],
            ext_bindingFaultReference:\
                    Iterable[WSDLMAPPER[BindingFaultReference]] = [],
            ext_endpoint: Iterable[WSDLMAPPER[Endpoint]] = [],
            ext_interfaceOperation:\
                    Iterable[WSDLMAPPER[InterfaceOperation]] = [],
            ext_interfaceMessageReference:\
                    Iterable[WSDLMAPPER[InterfaceMessageReference]] = [],
            ext_interfaceFaultReference:\
                    Iterable[WSDLMAPPER[InterfaceFaultReference]] = [],
            ext_service: Iterable[WSDLMAPPER[Service]] = [],
            ext_description:\
                    Iterable[WSDLMAPPER[Description]] = [],
            ext_interfaceFault:\
                    Iterable[WSDLMAPPER[InterfaceFault]] = [],
            ):
        """Register all extensions"""
        self.ext_description = list(ext_description)
        self.ext_interfaceMessageReference = list(ext_interfaceMessageReference)
        self.ext_interfaceFaultReference = list(ext_interfaceFaultReference)
        self.ext_interfaceFault = list(ext_interfaceFault)
        self.ext_service = list(ext_service)
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
        for extmap in self.ext_description:
            extmap(g, description)
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
        for extmap in self.ext_interfaceFault:
            extmap(g, interface_fault)

    def _map_interfaceOperation(self, g: Graph,
                                interfaceOperation: InterfaceOperation,
                                ) -> None:
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
        mcm = interfaceMessageReference.message_content_model
        if mcm == MCM_ELEMENT:
            elementDeclaration_id = BNode()
            g.add((elemid, WSDL.elementDeclaration, elementDeclaration_id))
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
        for extmap in self.ext_interfaceMessageReference:
            extmap(g, interfaceMessageReference)

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
        for extmap in self.ext_interfaceFaultReference:
            extmap(g, interfaceFaultReference)


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
        for extmap in self.ext_interfaceFault:
            extmap(g, interfaceFault)

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
        elemid = _create_id(bindingMessageReference)
        parentid = _create_id(bindingMessageReference.parent)
        g.add((elemid, RDF.type, WSDL.BindingMessageReference))
        g.add((parentid, WSDL.bindingMessageReference, elemid))
        imr = bindingMessageReference.interface_message_reference
        imr_id = _create_id(imr)
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
        for extmap in self.ext_service:
            extmap(g, service)

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
