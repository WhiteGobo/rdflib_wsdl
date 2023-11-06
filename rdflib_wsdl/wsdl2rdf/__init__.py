from .class_MapperWSDL2RDF import MapperWSDL2RDF
from .extensions import *

basicGenerateRDF = MapperWSDL2RDF(
        ext_binding = default_extensions_binding,
        ext_bindingOperation = default_extensions_bindingOperation,
        ext_bindingFault = default_extensions_bindingFault,
        ext_bindingMessageReference=default_extensions_bindingMessageReference,
        ext_bindingFaultReference = default_extensions_bindingFaultReference,
        ext_endpoint = default_extensions_endpoint,
        ext_interfaceOperation = default_extension_interfaceOperation,
        )
"""Basic wsdl to rdf transform with only builtin plugins enabled"""

generateRDF = basicGenerateRDF
"""WSDL to RDF transform with all found :term:`plugins<WSDL plugin>` enabled."""
