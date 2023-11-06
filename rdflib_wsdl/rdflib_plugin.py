from urllib.parse import urldefrag, urljoin
import xml.sax
from xml.sax import handler, make_parser, xmlreader, SAXParseException
from xml.sax.handler import ErrorHandler
from xml.sax.saxutils import escape, quoteattr
from .xmlparser import WSDLXMLHandler
    
import rdflib.parser
from rdflib.exceptions import Error, ParserError
from rdflib.namespace import RDF, is_ncname
from rdflib.plugins.parsers.RDFVOC import RDFVOC
from rdflib.term import BNode, Literal, URIRef
import rdflib

from .wsdl_components import Description
from .wsdl2rdf import generateRDF

class WSDLXML_PluginException(rdflib.plugin.PluginException):
    """Expected errortype of rdflib.Graph.parse."""

class WSDLXMLParser(rdflib.parser.Parser):
    _parser: WSDLXMLHandler

    def parse(self, source, sink, preserve_bnode_ids=None):
        """
        :raises WSDLXML_PluginException:
        """
        description: Description
        self._parser = WSDLXMLHandler.create_parser(source, sink)
        content_handler = self._parser.getContentHandler()
        if preserve_bnode_ids is not None:
            content_handler.preserve_bnode_ids = preserve_bnode_ids
        # # We're only using it once now
        # content_handler.reset()
        # self._parser.reset()
        try:
            self._parser.parse(source)
        except SAXParseException as err:
            raise WSDLXML_PluginException() from err
