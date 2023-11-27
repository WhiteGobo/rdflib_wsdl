import abc
from typing import Optional, Tuple, Any
from collections.abc import Iterable
from .shared import _ns_xs

MCM_ANY = "any"
"""A possible :term:`message content model`"""
MCM_NONE = "none"
"""A possible :term:`message content model`"""
MCM_OTHER = "other"
"""A possible :term:`message content model`"""
MCM_ELEMENT = "element"
"""A possible :term:`message content model`"""

class _WSDLComponent(abc.ABC):
    """A comprehensive list of all components and their properties canbe found
    `https://www.w3.org/TR/wsdl/#componentsummary`_
    """
    #@property
    #@abc.abstractmethod
    #def iri(self) -> URIRef: ...

    @property
    @abc.abstractmethod
    def parent(self) -> Optional["_WSDLComponent"]: ...

    @property
    @abc.abstractmethod
    def fragment_identifier(self) -> str:
        """See also :term:`XPointer Framework scheme`"""

    @property
    @abc.abstractmethod
    def targetNamespace(self) -> str:
        """According to `https://www.w3.org/TR/wsdl20/#wsdl-iri-references`_
        names of components have an IRI part. This is not the case according
        to the xml description. So i we implement targetNamespace additionally.
        """
                         

class Binding(_WSDLComponent):
    @property
    @abc.abstractmethod
    def parent(self) -> "Description": ...

    @abc.abstractmethod
    def get(self, namespace: str, name: str, **kwargs: Any) -> Any:
        """This is needed to get access to data of extensions"""
        raise KeyError(namespace, name)

    @property
    @abc.abstractmethod
    def binding_faults(self) -> Iterable["BindingFault"]: ...

    @property
    @abc.abstractmethod
    def binding_operations(self) -> Iterable["BindingOperation"]: ...

    @property
    @abc.abstractmethod
    def interface(self) -> "Interface": ...

    @property
    @abc.abstractmethod
    def name(self) -> str: ...

    @property
    @abc.abstractmethod
    def type(self) -> str:
        """Defined by uri"""

    @property
    def fragment_identifier(self) -> str:
        return "wsdl.binding(%s)" % self.name

class BindingFault(_WSDLComponent):
    @abc.abstractmethod
    def get(self, namespace, name, **kwargs: Any) -> Any:
        """This is needed to get access to data of extensions"""
        raise KeyError(namespace, name)

    @property
    @abc.abstractmethod
    def interface_fault(self) -> "InterfaceFault":
        """Is only referenced in xml per attribute ref"""

    @property
    @abc.abstractmethod
    def parent(self) -> "Binding": ...

    @property
    def fragment_identifier(self) -> str:
        return "wsdl.bindingFault(%s/%s)" % (self.parent.name, self.interface_fault.name)

class BindingFaultReference(_WSDLComponent):
    """extensible via attributes
    :TODO: Im not quite sure what the attribute wsdl.messageLabel does. Maybe
        it has to be the same as a possible messagelabel to the refererenced
        interface fault.
    """
    @abc.abstractmethod
    def get(self, namespace, name, **kwargs: Any) -> Any:
        """This is needed to get access to data of extensions"""
        raise KeyError(namespace, name)

    @property
    @abc.abstractmethod
    def interface_fault_reference(self) -> "InterfaceFaultReference":
        """uses ref item. References the bound interface fault
        namepsace of ref must be the same as namespace of
        this element. So only fragment is relevant.
        """

    @property
    @abc.abstractmethod
    def message(self) -> str:
        """same as messageLabel property"""

    @property
    @abc.abstractmethod
    def parent(self) -> "BindingOperation": ...

    @property
    def binding(self) -> "Binding":
        return self.parent.parent

    @property
    @abc.abstractmethod
    def documentation(self) -> str:
        """plain text documentation of element"""

    @property
    def fragment_identifier(self) -> str:
        """Im not quite sure what message is. There is a messagelabel for
        the xml representation but its optional.
        Specified in `https://www.w3.org/TR/wsdl/#wsdl.bindingFaultReference`_
        """
        return "wsdl.bindingFaultReference(%s/%s/%s/%s)" % (
                self.binding.name, 
                self.parent.interface_operation.name,
                self.interface_fault_reference.message_label,
                self.interface_fault_reference.interface_fault.name,
                )

class BindingMessageReference(_WSDLComponent):
    @abc.abstractmethod
    def get(self, namespace, name, **kwargs: Any) -> Any:
        """This is needed to get access to data of extensions"""
        raise KeyError(namespace, name)

    @property
    @abc.abstractmethod
    def interface_message_reference(self) -> "InterfaceMessageReference": ...

    @property
    @abc.abstractmethod
    def parent(self) -> "BindingOperation": ...

    @property
    def binding(self) -> "Binding":
        return self.parent.parent

    @property
    def message_label(self) -> str:
        """Same as the xml attribute message label but xmlattr is optional"""
        return self.interface_message_reference.message_label

    @property
    def fragment_identifier(self) -> str:
        """
        Specified `https://www.w3.org/TR/wsdl/#wsdl.bindingMessageReference`_
        """
        return "wsdl.bindingMessageReference(%s/%s/%s)" % (
                self.binding.name,
                self.parent.name,
                self.interface_message_reference.message_label,
                )

class BindingOperation(_WSDLComponent):
    @abc.abstractmethod
    def get(self, namespace, name, **kwargs: Any) -> Any:
        """This is needed to get access to data of extensions"""
        raise KeyError(namespace, name)

    @property
    @abc.abstractmethod
    def binding_fault_references(self) -> Iterable["BindingFaultReference"]:
        ...

    @property
    @abc.abstractmethod
    def binding_message_references(
            self) -> Iterable["BindingMessageReference"]: ...

    @property
    @abc.abstractmethod
    def interface_operation(self) -> "InterfaceOperation": ...

    @property
    @abc.abstractmethod
    def parent(self) -> "Binding": ...

    @property
    def fragment_identifier(self) -> str:
        return "wsdl.bindingOperation(%s/%s)" % (self.parent.name,
                                                 self.interface_operation.name)

class Description(_WSDLComponent):
    parent = None

    def get_interfaceOperation(self, ref_ns, ref_name) -> "InterfaceOperation":
        """
        :TODO: comparing of ref_ns is missing because targetnamespace
            not implemented
        :raises: KeyError
        """
        for interface in self.interfaces:
            for operation in interface.interface_operations:
                if operation.name == ref_name:
                    return operation
        raise KeyError()

    def get_interfaceFault(self, ref_ns, ref_name) -> "InterfaceFault":
        """
        :TODO: comparing of ref_ns is missing because targetnamespace
            not implemented
        :raises: KeyError
        """
        for interface in self.interfaces:
            for fault in interface.interface_faults:
                if fault.name == ref_name:
                    return fault
        raise KeyError()

    @property
    @abc.abstractmethod
    def bindings(self) -> Iterable[Binding]: ...

    @property
    @abc.abstractmethod
    def element_declarations(self) -> Iterable["ElementDeclaration"]: ...

    @property
    @abc.abstractmethod
    def interfaces(self) -> Iterable["Interface"]: ...

    @property
    @abc.abstractmethod
    def services(self) -> Iterable["Service"]: ...

    @property
    @abc.abstractmethod
    def type_definitions(self) -> Iterable["TypeDefinition"]: ...

    @property
    def fragment_identifier(self) -> str:
        return "wsdl.description()"

class ElementDeclaration(_WSDLComponent):
    @property
    @abc.abstractmethod
    def name(self) -> str: ...

    @property
    @abc.abstractmethod
    def system(self): ...

    @property
    def fragment_identifier(self) -> str:
        if self.system.namespace == _ns_xs:
            return "wsdl.elementDeclaration(%s)" % self.name
        else:
            return "wsdl.elementDeclaration(%s,%s)" % (self.name,
                                                       self.system.namespace)

class Endpoint(_WSDLComponent):
    @abc.abstractmethod
    def get(self, namespace: str, name: str, **kwargs: Any) -> Any:
        raise KeyError(namespace, name)

    @property
    @abc.abstractmethod
    def address(self) -> str: ...

    @property
    @abc.abstractmethod
    def binding(self) -> "Binding": ...

    @property
    @abc.abstractmethod
    def name(self) -> str: ...

    @property
    @abc.abstractmethod
    def parent(self) -> "Service": ...

    @property
    def fragment_identifier(self) -> str:
        return "wsdl.endpoint(%s/%s)"% (self.parent.name, self.name)

class Interface(_WSDLComponent):
    @property
    @abc.abstractmethod
    def parent(self) -> "Description": ...

    @property
    @abc.abstractmethod
    def extended_interfaces(self) -> Iterable["Interface"]: ...

    @property
    @abc.abstractmethod
    def interface_faults(self) -> Iterable["InterfaceFault"]: ...

    @property
    @abc.abstractmethod
    def interface_operations(self) -> Iterable["InterfaceOperation"]: ...

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """
        :TODO: This should return a QName not a NCName.
        """

    @property
    def fragment_identifier(self) -> str:
        return "wsdl.interface(%s)" % self.name

class InterfaceFault(_WSDLComponent):
    @property
    def element_declaration(self) -> Tuple[str, str]:
        """
        :TODO: find a way to find the corresponding interface fault reference
        :raises StopIteration:
        """
        #description = self.parentnode.parentnode
        #all_decl = description.element_declaration
        #try:
        #    return next(x for x in all_decl if True)
        #except StopIteration:
        #    raise

    @property
    @abc.abstractmethod
    def message_content_model(self) -> str:
        """
        See `https://www.w3.org/TR/wsdl/#InterfaceFault`_
        :returns: one of (MCM_ANY, MCM_NONE, MCM_OTHER, MCM_ELEMENT)
        """

    @property
    @abc.abstractmethod
    def name(self) -> str: ...

    @property
    @abc.abstractmethod
    def parent(self) -> "Interface": ...

    @property
    def fragment_identifier(self) -> str:
        return "wsdl.interfaceFault(%s/%s)" % (self.parent.name, self.name)

class InterfaceFaultReference(_WSDLComponent):
    @property
    @abc.abstractmethod
    def direction(self) -> str:
        """Must be the xs:token 'in' or 'out'"""

    @property
    @abc.abstractmethod
    def interface_fault(self) -> InterfaceFault:
        """
        :TODO: I might change this to return optional an InterfaceFault
            eventually.
        """

    @property
    @abc.abstractmethod
    def message_label(self) -> str: ...

    @property
    @abc.abstractmethod
    def parent(self) -> "InterfaceOperation": ...

    @property
    def interface(self) -> "Interface":
        return self.parent.parent

    @property
    def fragment_identifier(self) -> str:
        return "wsdl.interfaceFaultReference(%s/%s/%s/%s)" % (
                self.interface.name,
                self.parent.name,
                self.message_label,
                self.name,
                )

class InterfaceMessageReference(_WSDLComponent):
    @property
    @abc.abstractmethod
    def direction(self): ...

    @property
    @abc.abstractmethod
    def element_declaration(self) -> Tuple[str, str]:
        """Returns the :term:`qualified name` of the declaration of 
        this element.
        """

    @property
    @abc.abstractmethod
    def message_content_model(self) -> str:
        """
        See `https://www.w3.org/TR/wsdl/#InterfaceFault`_
        """
        raise NotImplementedError()
        return MCM_ANY
        return MCM_NONE
        return MCM_OTHER
        return MCM_ELEMENT

    @property
    @abc.abstractmethod
    def message_label(self) -> str: ...

    @property
    @abc.abstractmethod
    def parent(self) -> "InterfaceOperation": ...

    @property
    def interface(self) -> "Interface":
        return self.parent.parent

    @property
    def fragment_identifier(self) -> str:
        return "wsdl.interfaceMessageReference(%s/%s/%s)" % (
                self.interface.name,
                self.parent.name,
                self.message_label,
                )

class InterfaceOperation(_WSDLComponent):
    @abc.abstractmethod
    def get(self, namespace: str, name: str, **kwargs: Any) -> Any:
        raise KeyError(namespace, name)

    @property
    @abc.abstractmethod
    def interface_fault_references(self) -> Iterable["InterfaceFaultReference"]: ...

    @property
    @abc.abstractmethod
    def interface_message_references(self) -> Iterable["InterfaceMessageReference"]: ...

    @property
    @abc.abstractmethod
    def message_exchange_pattern(self) -> str:
        """Returns an xs.uri"""

    @property
    @abc.abstractmethod
    def name(self) -> str: ...

    @property
    @abc.abstractmethod
    def parent(self) -> "Interface": ...

    @property
    @abc.abstractmethod
    def style(self): ...

    @property
    def fragment_identifier(self) -> str:
        return "wsdl.interfaceOperation(%s/%s)" % (
                self.parent.name,
                self.name,
                )

class Service(_WSDLComponent):
    @property
    def parent(self) -> "Description": ...

    @property
    @abc.abstractmethod
    def endpoints(self) -> Iterable["Endpoint"]: ...

    @property
    @abc.abstractmethod
    def interface(self) -> "Interface": ...

    @property
    @abc.abstractmethod
    def name(self) -> str: ...

    @property
    def fragment_identifier(self) -> str:
        return "wsdl.service(%s)" % self.name

class TypeDefinition(_WSDLComponent):
    @property
    def name(self) -> str: ...
    @property
    @abc.abstractmethod
    def system(self) -> "Extension":
        """
        :TODO: Im not sure if Extension is the correct returntype
        """

    @property
    def fragment_identifier(self) -> str:
        """`https://www.w3.org/TR/wsdl/#wsdl.typeDefinition`_
        :TODO: Im not sure if this is correct
        """
        if self.system.namespace == _ns_xs:
            return "wsdl.typeDef(%s)" % self.name
        else:
            return "wsdl.typeDef(%s,%s)" % (self.name, self.system.namespace)

class Extension(_WSDLComponent):
    @property
    @abc.abstractmethod
    def namespace(self) -> str:
        """
        :return: the URI that identifies the extension
        """
    
    @property
    @abc.abstractmethod
    def identifier(self) -> str: ...

    @property
    def fragment_identifier(self) -> str:
        """See `https://www.w3.org/TR/wsdl/#wsdl.extension`_"""
        return "wsdl.extension(%s,%s)" % (self.namespace,self.identifier)
