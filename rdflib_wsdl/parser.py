from urllib.parse import urldefrag, urljoin
import xml.sax
from xml.sax import handler, make_parser, xmlreader, SAXParseException
from xml.sax.handler import ErrorHandler
from xml.sax.saxutils import escape, quoteattr
from .xmlhandler_mainbody import WSDLXMLHandler
    
import rdflib.parser
from rdflib.exceptions import Error, ParserError
from rdflib.namespace import RDF, is_ncname
from rdflib.plugins.parsers.RDFVOC import RDFVOC
from rdflib.term import BNode, Literal, URIRef
import rdflib

from . import xmlhandler

class WSDLXML_PluginException(rdflib.plugin.PluginException):
    pass

class _parsercreator(xml.sax.handler.ContentHandler):
    @classmethod
    def create_parser(cls, target, store) -> xmlreader.XMLReader:
        parser = xml.sax.make_parser()
        parser.setFeature(xml.sax.handler.feature_namespaces, 0)
        #parser.setFeature(xml.sax.handler.feature_namespace_prefixes, 1)
        self = cls(store)
        self.setDocumentLocator(target)
        # rdfxml.setDocumentLocator(_Locator(self.url, self.parser))
        parser.setContentHandler(self)
        parser.setErrorHandler(xml.sax.handler.ErrorHandler())
        return parser

class WSDLXMLHandler(_parsercreator, WSDLXMLHandler):
    """Mainclass for creation of parsers for :term:`rif/xml`.
    """

class WSDLXMLParser(rdflib.parser.Parser):
    _parser: xmlreader.XMLReader

    def parse(self, source, sink, preserve_bnode_ids=None):
        """
        :raises XMLRif_PluginException:
        """
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
