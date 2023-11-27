from typing import List, Any, Optional, Iterable
from rdflib import Graph, URIRef, RDF
from ..shared import WSDL, parse_description_iri, parse_interface_uri, parse_interface_operation_iri, parse_interface_message_reference_iri
from ..wsdl_components import\
        Description, Interface, InterfaceOperation,\
        InterfaceFaultReference, InterfaceMessageReference,\
        BindingFault, BindingOperation,\
        Service, Endpoint, InterfaceMessageReference, Binding,\
        MCM_OTHER, MCM_ANY, MCM_NONE, MCM_ELEMENT
from ..extensions.rdf_interfaces import RetrieveFailed, extras_endpoint, extras_interface_operation

class _rdfgraph_base:
    def __init__(self, rdfgraph: Graph, iri: URIRef):
        self.rdfgraph = rdfgraph
        self.iri = iri
        assert iri in rdfgraph.all_nodes()

    def __repr__(self):
        t = str(type(self))
        return "<%s:%s:%s>" % (t, self.iri, self.rdfgraph)

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        elif self.iri != other.iri:
            return False
        elif self.rdfgraph != other.rdfgraph:
            return False
        return True

class GraphDescription(Description, _rdfgraph_base):
    def __init__(self, rdfgraph: Graph, iri: URIRef):
        super().__init__(rdfgraph, iri)
        self._targetNamespace = parse_description_iri(iri)

    @property
    def parent(self):
        raise AttributeError()

    @property
    def bindings(self):
        raise NotImplementedError()

    @property
    def targetNamespace(self):
        return self._targetNamespace

    @property
    def interfaces(self):
        interface_iris = self.rdfgraph.objects(self.iri, WSDL.interface)
        return [GraphInterface(self.rdfgraph, iri) for iri in interfaces_iris]

    @property
    def services(self):
        iris = self.rdfgraph.objects(self.iri, WSDL.service)
        return [GraphService(self.rdfgraph, iri) for iri in iris]

    @property
    def type_definitions(self):
        raise NotImplementedError()

    @property
    def element_declarations(self):
        raise NotImplementedError()

class GraphInterface(Interface, _rdfgraph_base):
    def __init__(self, rdfgraph: Graph, iri: URIRef):
        super().__init__(rdfgraph, iri)
        self._targetNamespace, self._name = parse_interface_uri(iri)

    @property
    def parent(self) -> GraphDescription:
        iri = self.rdfgraph.value(predicate=WSDL.interface, object=self.iri)
        assert isinstance(iri, URIRef),q
        return GraphDescription(self.rdfgraph, iri)

    @property
    def targetNamespace(self):
        return self._targetNamespace

    @property
    def name(self):
        return self._name

    @property
    def interface_operations(self):
        iris = self.rdfgraph.objects(self.iri, WSDL.interfaceOperation)
        return [GraphInterfaceOperation(self.rdfgraph, iri) for iri in iris]

    @property
    def extended_interfaces(self):
        raise NotImplementedError()

    @property
    def interface_faults(self):
        raise NotImplementedError()

class GraphInterfaceMessageReference(InterfaceMessageReference,
                                     _rdfgraph_base):
    def __init__(self, rdfgraph: Graph, iri: URIRef):
        super().__init__(rdfgraph, iri)
        self._targetNamespace, _, _, self._name = parse_interface_message_reference_iri(iri)

    @property
    def direction(self) -> str:
        if (self.iri, RDF.type, WSDL.InputMessage) in self.rdfgraph:
            return "in"
        else:
            return "out"

    @property
    def targetNamespace(self):
        raise NotImplementedError()

    @property
    def message_label(self):
        raise NotImplementedError()
        return self._name

    @property
    def element_declaration(self):
        if self._element_declaration is None:
            raise AttributeError("Cant access element_declaration if not set.")
        else:
            return self._element_declaration

    @property
    def name(self):
        return self._name

    @property
    def parent(self):
        return self._parent

    @property
    def message_content_model(self):
        return MCM_OTHER

class GraphEndpoint(Endpoint, _rdfgraph_base):
    def __init__(self, rdfgraph: Graph, iri: URIRef):
        super().__init__(rdfgraph, iri)
        #self._targetNamespace, _, self._name = parse_endpoint_iri(iri)

    def __getattr__(self, key:str) -> Any:
        try:
            retrieving_methods = extras_endpoint[key]
        except KeyError as err:
            raise AttributeError("No extra implemented for Endpoint "
                                 "for key '%s'." % key)
        for m in retrieving_methods:
            try:
                return m(self.rdfgraph, self.iri)
            except RetrieveFailed:
                pass
        raise AttributeError("Not enough information found to retrieve for "
                             "Endpoint for key %s" % key)

    @property
    def name(self):
        return self._name

    def get(self, namespace: str, name: str, **kwargs: Any) -> Any:
        """No extra information given in this implementation."""
        raise KeyError()

    @property
    def parent(self) -> "GraphService":
        service_iri = self.rdfgraph.value(predicate=WSDL.endpoint, object=self.iri)
        return GraphService(self.rdfgraph, service_iri)

    @property
    def targetNamespace(self) -> str:
        raise NotImplementedError()

    @property
    def address(self) -> str:
        raise AttributeError()

    @property
    def binding(self) -> Binding:
        raise NotImplementedError()

class GraphService(Service, _rdfgraph_base):
    def __init__(self, rdfgraph: Graph, iri: URIRef):
        super().__init__(rdfgraph, iri)
        #self._targetNamespace, _, self._name = parse_service_iri(iri)
    @property
    def targetNamespace(self):
        raise NotImplementedError()
        return self._targetNamespace

    @property
    def interface(self):
        interface_iri = self.rdfgraph.value(self.iri, WSDL.implements)
        return GraphInterface(self.rdfgraph, interface_iri)

    @property
    def endpoints(self):
        for iri in self.rdfgraph.objects(self.iri, WSDL.endpoint):
            yield GraphEndpoint(self.rdfgraph, iri)

    @property
    def name(self):
        raise NotImplementedError()
        return self._name

    @property
    def parent(self):
        desc_iri = self.rdfgraph.value(predicate=WSDL.service, object=self.iri)
        return GraphDescription(rdfgraph, desc_iri)

class GraphInterfaceOperation(InterfaceOperation, _rdfgraph_base):
    def __init__(self, rdfgraph: Graph, iri: URIRef):
        super().__init__(rdfgraph, iri)
        self._targetNamespace, _, self._name = parse_interface_operation_iri(iri)

    def __getattr__(self, key:str) -> Any:
        try:
            retrieving_methods = extras_interface_operation[key]
        except KeyError as err:
            raise AttributeError("No extra implemented for Interface "
                                 "Operation for key '%s'." % key, extras_interface_operation)
        for m in retrieving_methods:
            try:
                return m(self.rdfgraph, self.iri)
            except RetrieveFailed:
                logger.debug("retrieving method '%s' failed" % m,
                             exc_info=True)
                pass
        raise AttributeError("Not enough information found to retrieve for "
                             "Interface Operation for key %s" % key)

    @property
    def interface_message_references(self) -> Iterable[InterfaceMessageReference]:
        for iri in self.rdfgraph.objects(self.iri, WSDL.interfaceMessageReference):
            yield GraphInterfaceMessageReference(self.rdfgraph, iri)

    def get(self, namespace: str, name: str, **kwargs: Any):
        raise KeyError()

    @property
    def interface_fault_references(self):
        raise NotImplementedError()

    @property
    def message_exchange_pattern(self):
        """Default to simple in-out"""
        raise NotImplementedError()
        return "http://www.w3.org/ns/wsdl/in-out"

    @property
    def name(self):
        return self._name

    @property
    def parent(self):
        iri = self.rdfgraph.value(predicate=WSDL.interfaceOperation,
                                  object=self.iri)
        return GraphInterface(self.rdfgraph, iri)

    @property
    def style(self):
        raise NotImplementedError()

    @property
    def targetNamespace(self):
        return self._targetNamespace
