import abc
from ..wsdl_components import Description, Interface, InterfaceMessageReference, InterfaceOperation, MCM_OTHER, Service, Endpoint, Binding
from typing import Callable, Any, List, Iterable, Optional, Tuple
from inspect import signature, Parameter, getmodule
from ..basic_implementations import easyDescription
from dataclasses import dataclass, field
from .generell import easyDescription, easyInterface, easyService,\
        easyEndpoint, easyInterfaceOperation, easyBinding,\
        easyInterfaceMessageReference_in, easyInterfaceMessageReference_out

class python_interfaceOperation(easyInterfaceOperation):
    @classmethod
    def from_method(
            cls,
            method: Callable,
            interface: easyInterface,
            name: Optional[str] = None,
            expected_errortypes: Iterable[type[Exception]] = [],
            ):
        if name is None:
            module = getmodule(method)
            name = module.__name__
        self = cls(interface, name)
        if expected_errortypes:
            raise NotImplementedError()
        #generate inputtype(with annotations) qname must be given to reference
        #generate outputtype(with annotations) qname must be given to reference
        easyInterfaceMessageReference_in(self, "input")
        easyInterfaceMessageReference_out(self, "output")
        return self


class python_interface(easyInterface):
    DEFAULT_INTERFACE_OPERATION = python_interfaceOperation

    @classmethod
    def from_method(
            cls,
            method: Callable,
            description: Optional[easyDescription] = None,
            name: Optional[str] = None,
            targetNamespace: Optional[str] = None,
            expected_errortypes: Iterable[type[Exception]] = [],
            ):
        if targetNamespace is None:
            raise NotImplementedError()
        if description is None:
            description = easyDescription(targetNamespace)
        if name is None:
            module = getmodule(method)
            name = module.__name__
        if expected_errortypes:
            #generate InterfaceFault from expected_errortypes
            raise NotImplementedError()
        self = cls(description, name,
                   targetNamespace=targetNamespace)
        interfaceOperation = python_interfaceOperation.from_method(method, self)
        return self

class python_binding(easyBinding):
    @classmethod
    def from_method(cls, method: Callable, description: easyDescription,
                    ):
        return cls(description, method.__name__)


class _python_endpoint(Endpoint):
    """Not full implementation of a endpoint for pythons method.
    """
    _name: str
    def get_method(self):
        #return self.method
        module = importlib.import_module(self.module_name)
        return getattr(module, self.method_name)

    @property
    @abc.abstractmethod
    def method(self) -> Callable: ...
        #module = importlib.import_module(self.module_name)
        #return getattr(module, self.method_name)

    @property
    @abc.abstractmethod
    def module_name(self) -> str: ...

    @property
    @abc.abstractmethod
    def method_name(self) -> str: ...

    @property
    def name(self):
        return self._name

    def get(self, namespace: str, name: str, **kwargs: Any) -> Any:
        """No extra information given in this implementation."""
        raise KeyError()

    @property
    def targetNamespace(self) -> str:
        return self.parent.targetNamespace

    @property
    def address(self) -> str:
        """endpoints for python methods dont have a valid address, because it
        represents always a locally loaded python method.
        """
        raise AttributeError()


class python_endpoint(_python_endpoint):
    """Implementation of an endpoint for a method with a method as central
    information.
    """
    DEFAULT_SERVICE_FACTORY = easyService
    method: Callable
    """This method is used to generate a parent service."""
    def __init__(self, parent: easyService, binding: Binding,
                 method: Callable, name: Optional[str] = None):
        """
        :TODO: Make binding required
        """
        if name is None:
            self._name = method.__name__
        else:
            self._name = method.__name__
        self._binding = binding
        self._parent = parent
        parent._endpoints.append(self)
        self.method = method

    @classmethod
    def from_method(
            cls,
            method: Callable,
            interfaceOperation: easyInterfaceOperation,
            ):
        """Creates information about an endpoint, which binds the given method
        as an operation, that implements given interface operation.
        :param method: a valid operation for given interface operation
        :param interfaceOperation: Information about the operation. Includes
            generalized input types, information about the message exchange
            and can contain other information.
        :TODO: There is no check if the method is valid for given
            interface operation.
        """
        interface = interfaceOperation.parent
        description = interfaceOperation.parent.parent
        binding = python_binding.from_method(method, description)
        name = method.__name__
        module = getmodule(method)
        service = cls.DEFAULT_SERVICE_FACTORY(description, name, interface)
        return cls(service, binding, method=method)

    def _get_method(self) -> Callable:
        return self._method

    def _set_method(self, method) -> Callable:
        self._method = method
    method = property(fget= _get_method, fset=_set_method)

    @property
    def method_name(self) -> str:
        return self.method.__name__

    @property
    def module_name(self) -> str:
        return getmodule(self.method).__name__

    @property
    def parent(self) -> easyService:
        return self._parent

    @property
    def binding(self) -> Binding:
        return self._binding