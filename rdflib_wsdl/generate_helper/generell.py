from typing import Callable, Any, List, Iterable, Optional, Tuple
from rdflib import Graph, URIRef
from ..shared import WSDL, parse_description_iri, parse_interface_uri
from ..wsdl_components import\
        Description, Interface, InterfaceOperation,\
        InterfaceFaultReference, InterfaceMessageReference,\
        BindingFault, BindingOperation,\
        Service, Endpoint, InterfaceMessageReference, Binding,\
        MCM_OTHER, MCM_ANY, MCM_NONE, MCM_ELEMENT

__all__=[
        "easyDescription",
        "easyInterface",
        "easyService",
        "easyEndpoint",
        "easyInterfaceOperation",
        "easyInterfaceMessageReference_in",
        "easyInterfaceMessageReference_out",
        ]

class easyDescription(Description):
    """Easy implementation of description. Can be used within methods for
    easy generation of a Description or can be inherited.
    """
    def __init__(self, targetNamespace):
        self._bindings = []
        self._interfaces = []
        self._services = []
        self._targetNamespace = targetNamespace
        self._type_definitions = []
        self._element_declarations = []

    @classmethod
    def from_rdfgraph(cls, graph: Graph, iri: URIRef):
        targetNamespace = parse_description_iri(iri)
        return cls(targetNamespace)

    @property
    def parent(self):
        raise AttributeError()

    @property
    def bindings(self):
        return self._bindings

    @property
    def targetNamespace(self):
        return self._targetNamespace

    @property
    def interfaces(self):
        return self._interfaces

    @property
    def services(self):
        return self._services

    @property
    def type_definitions(self):
        return self._type_definitions

    @property
    def element_declarations(self):
        return self._element_declarations

class easyBinding(Binding):
    def __init__(self, parent: easyDescription, name):
        self._parent = parent
        self._name = name
        self._binding_faults = []
        self._binding_operations = []

    def get(self, namespace: str, name: str, **kwargs: Any) -> Any:
        """No extra information given in this implementation."""
        raise KeyError()

    @property
    def name(self) -> str:
        return self._name

    @property
    def parent(self) -> Interface:
        return self._parent

    @property
    def binding_faults(self) -> Iterable[BindingFault]:
        return self._binding_faults

    @property
    def binding_operations(self) -> Iterable[BindingOperation]:
        return self._bindings_operations

    @property
    def interface(self) -> Interface:
        raise NotImplementedError()
        return self.parent.interfaces

    @property
    def targetNamespace(self) -> str:
        return self.parent.targetNamespace

    @property
    def type(self) -> str:
        """Defined by uri"""
        raise NotImplementedError()

class easyInterface(Interface):
    """Easy implementation of interface. Can be used within methods for
    easy generation of a Interface or can be inherited.
    """
    interface_operations = None
    def __init__(self, parent: easyDescription, name: str,
                 interface_operations: Iterable[InterfaceOperation] = [],
                 targetNamespace: Optional[str] = None,
                 ):
        self._name = name
        self._faults = []
        self.interface_operations = list(interface_operations)
        self._parent = parent
        self._targetNamespace = targetNamespace
        self._extended_interfaces = []
        parent.interfaces.append(self)

    @classmethod
    def from_rdfgraph(cls, graph: Graph, iri: URIRef,
                      description: Optional["easyDescription"] = None):
        if description is None:
            description_iri = graph.value(predicate=WSDL.interface, object=iri)
            description = easyDescription.from_rdfgraph(graph, description_iri)
        _, name = parse_interface_uri(iri)
        return cls(description, name)

    @property
    def parent(self) -> easyDescription:
        return self._parent

    @property
    def targetNamespace(self):
        if self._targetNamespace is None:
            return self.parent.targetNamespace
        else:
            return self._targetNamespace

    @property
    def name(self):
        return self._name

    @property
    def extended_interfaces(self):
        return self._extended_interfaces

    @property
    def interface_faults(self):
        return self._faults

class easyService(Service):
    """Easy implementation of service. Can be used within methods for
    easy generation of a Service or can be inherited.
    """
    def __init__(self, parent: easyDescription, name: str,
                 interface: easyInterface):
        self._parent = parent
        self._name = name
        self._endpoints = []
        parent._services.append(self)
        self._interface = interface

    @property
    def targetNamespace(self):
        return self._parent.targetNamespace

    @property
    def interface(self):
        return self._interface

    @property
    def endpoints(self):
        return self._endpoints

    @property
    def name(self):
        return self._name

    @property
    def parent(self):
        return self._parent


class easyEndpoint(Endpoint):
    """Easy implementation of Endpoint. Can be used within methods for
    easy generation of a Endpoint or can be inherited.
    """
    def __init__(self, parent: easyService, name: str, binding: Binding,
                 address: Optional[str] = None):
        """
        :TODO: Make binding required
        """
        self._binding = binding
        self._name = name
        self._parent = parent
        parent._endpoints.append(self)
        self._address = address

    @property
    def name(self):
        return self._name

    def get(self, namespace: str, name: str, **kwargs: Any) -> Any:
        """No extra information given in this implementation."""
        raise KeyError()

    @property
    def parent(self) -> easyService:
        return self._parent

    @property
    def targetNamespace(self) -> str:
        return self.parent.targetNamespace

    @property
    def address(self) -> str:
        raise AttributeError()

    @property
    def binding(self) -> Binding:
        return self._binding


class easyInterfaceOperation(InterfaceOperation):
    """Easy implementation of Interface Operation. Can be used within methods
    for easy generation of a Interface Operation or can be inherited.
    """
    def __init__(self, parent: easyInterface, name: str):
        self._parent = parent
        parent.interface_operations.append(self)
        self._interface_message_references = []
        self._name = name

    @property
    def interface_message_references(self) -> List[InterfaceMessageReference]:
        return self._interface_message_references

    def get(self, namespace: str, name: str, **kwargs: Any):
        raise KeyError()

    @property
    def interface_fault_references(self):
        return []

    @property
    def message_exchange_pattern(self):
        """Default to simple in-out"""
        return "http://www.w3.org/ns/wsdl/in-out"

    @property
    def name(self):
        return self._name

    @property
    def parent(self):
        return self._parent

    @property
    def style(self):
        return []

    @property
    def targetNamespace(self):
        return self.parent.targetNamespace

class _easyIMR(InterfaceMessageReference):
    def __init__(self, parent: "easyInterfaceOperation",
                 name: str,
                 element_declaration: Optional[Tuple[str, str]] = None,
                 ):
        self._parent = parent
        self._name = name
        parent.interface_message_references.append(self)
        self._element_declaration = element_declaration

    @property
    def targetNamespace(self):
        return self.parent.targetNamespace

    @property
    def message_label(self):
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

class easyInterfaceMessageReference_in(_easyIMR):
    """Easy implementation of Interface Message Reference. Can be used
    within methods for easy generation of a Interface Message Reference 
    or can be inherited.
    The direction is 'in'.
    """
    @property
    def direction(self):
        """Returns 'in'"""
        return "in"


class easyInterfaceMessageReference_out(_easyIMR):
    """Easy implementation of Interface Message Reference. Can be used
    within methods for easy generation of a Interface Message Reference 
    or can be inherited.
    The direction is 'out'.
    """
    @property
    def direction(self):
        """Returns 'out'"""
        return "out"


