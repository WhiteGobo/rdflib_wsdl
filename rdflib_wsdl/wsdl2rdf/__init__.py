import sys
import typing as typ
if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points
from .class_MapperWSDL2RDF import MapperWSDL2RDF, ExtensionParserData
from .extensions import ParserData, sawsdlExtension, httpExtension, soapExtension

additional_parser: typ.Iterable[ExtensionParserData]\
        = entry_points(group='rdflib_wsdl.extensions.parser')
"""All available additional parsers specified by
entrypoint 'rdflib_wsdl.extensions.parser'. See parser for more information.
"""
if additional_parser:
    raise Exception(additional_parser)

from .python_extension import python_extension
all_parser = [sawsdlExtension, httpExtension, soapExtension, python_extension,
              *additional_parser]
"""All available parsers, so additional and builtin.
See `additional_parser` for more information.
"""

basicGenerateRDF = MapperWSDL2RDF.create_with_parser_data(
        additional_extensions = [sawsdlExtension, httpExtension, soapExtension]
        )
"""Basic wsdl to rdf transform with only builtin plugins enabled"""

generateRDF = MapperWSDL2RDF.create_with_parser_data(
        additional_extensions = all_parser,
        )
"""WSDL to RDF transform with all found :term:`plugins<WSDL plugin>` enabled.
"""
