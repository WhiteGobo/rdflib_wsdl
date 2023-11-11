from .wsdl_components import Description

class easyDescription(Description):
    def __init__(self, targetNamespace):
        self._bindings = []
        self._interfaces = []
        self._services = []
        self._targetNamespace = targetNamespace
        self._type_definitions = []
        self._element_declarations = []

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
