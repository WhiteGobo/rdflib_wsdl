"""
WSDL2RDF
========

WSDL parsing can be extended via :py:module:`rdflib_wsdl.wsdl2rdf`. Please see its documentation for a howto.


Plugin support for parser of :term:`WSDL`. This module uses the
:term:`entry point` ``'rdflib_wsdl.extensions.parser'``.

If you are using setuptools, you can implement a :py:class:`rdflib_wsdl.wsdl2rdf.class_MapperWSDL2RDF.ExtensionParserData` as an entry point
as described in
`https://setuptools.pypa.io/en/latest/userguide/entry_point.html#entry-points-for-plugins`_
"""
import sys
import typing as typ
if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points
from .class_MapperWSDL2RDF import MapperWSDL2RDF, ExtensionParserData
from .extensions import ParserData, sawsdlExtension, httpExtension, soapExtension

additional_parser: typ.Iterable[ExtensionParserData]\
        = [x.load() for x in entry_points(group='rdflib_wsdl.extensions.parser')]
"""All available additional parsers specified by
entrypoint 'rdflib_wsdl.extensions.parser'. See parser for more information.
Can be extended instead of relying on entrypoints:

```
my_parser_plugin = ParserData(...)
rdflib_wsdl.wsdl2rdf.additional_parser.append(my_parser_plugin)
```

A :term:`rdflib_wsdl plugin`.
"""

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
