import sys
if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points
from .class_MapperWSDL2RDF import MapperWSDL2RDF, extension_parser_data
from .extensions import parser, default_extensions_binding,default_extensions_bindingOperation, default_extensions_bindingFault, default_extensions_bindingMessageReference, default_extensions_bindingFaultReference, default_extensions_endpoint, default_extension_interfaceOperation
from .extensions import parser, sawsdlExtension, httpExtension, soapExtension

additional_parser: extension_parser_data = entry_points(group='rdflib_wsdl.extensions.parser')
"""All available additional parsers specified by
entrypoint 'rdflib_wsdl.extensions.parser'. See parser for more information.
"""
all_parser = [sawsdlExtension, httpExtension, soapExtension,
              *additional_parser]

basicGenerateRDF = MapperWSDL2RDF.create_with_parser_data(
        additional_extensions = [sawsdlExtension, httpExtension, soapExtension]
        )
"""Basic wsdl to rdf transform with only builtin plugins enabled"""

generateRDF = MapperWSDL2RDF.create_with_parser_data(
        additional_extensions = all_parser,
        )
"""WSDL to RDF transform with all found :term:`plugins<WSDL plugin>` enabled.
"""
