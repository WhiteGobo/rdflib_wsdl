from typing import Optional, Tuple, Any
from collections.abc import Mapping
import xml.sax
import xml.sax.handler
from xml.sax.xmlreader import XMLReader
from .xmlparser_states import _start, _state, name2qname, wsdl_description
from io import IOBase
from xml.sax.xmlreader import AttributesImpl

from .wsdl2rdf import MapperWSDL2RDF, additional_parser

class WSDLXMLHandler(xml.sax.handler.ContentHandler):
    """Transforms given wsdl/xml into rdf. Adds all triples to given sink.
    """
    startingstate: type[_state] = _start
    locator: Optional[IOBase]
    rdf_generator: MapperWSDL2RDF

    @classmethod
    def create_parser(cls, target, store,
                      rdf_generator: MapperWSDL2RDF=None) -> XMLReader:
        """Create a parser with this as content handler. Automaticly sets
        all expected features. Parsing adds all generated rdf triples
        to given store.

        :param rdf_generator: If not given automaticly creates a mapper from
        """
        if rdf_generator is None:
            rdf_generator = MapperWSDL2RDF.create_with_parser_data(
                    additional_extensions = additional_parser,
                    )
        parser = xml.sax.make_parser()
        parser.setFeature(xml.sax.handler.feature_namespaces, 0)
        #parser.setFeature(xml.sax.handler.feature_namespace_prefixes, 1)
        self = cls(store, rdf_generator)
        self.setDocumentLocator(target)
        # rdfxml.setDocumentLocator(_Locator(self.url, self.parser))
        parser.setContentHandler(self)
        parser.setErrorHandler(xml.sax.handler.ErrorHandler())
        return parser


    def __init__(self, store, rdf_generator):
        self.rdf_generator = rdf_generator
        self.store = store
        self.preserve_bnode_ids = False
        self.reset()
        self.states = []

    def _get_currentState(self):
        return self.states[-1]

    def _set_currentState(self, newstate):
        if newstate not in self.states:
            self.states.append(newstate)
        elif self.states[-2] == newstate:
            self.states.pop()
        else:
            raise Exception("Cant set state only to an old state, if that "
                            "state is the previous state.")

    currentState = property(fset=_set_currentState, fget=_get_currentState)

    def reset(self):
        pass

    def setDocumentLocator(self, locator: IOBase):
        self.locator = locator

    def startDocument(self):
        self.currentState = self.startingstate()
        
    def parse(self, *args: Any):
        raise Exception()

    #def feed(self, buffer):
    #    raise Exception(buffer)
    #    super().feed()

    def endDocument(self) -> None:
        assert isinstance(self.currentState, _start)
        assert self.currentState.first_state is not None

        for ax in self.rdf_generator(self.currentState.first_state):
            self.store.add(ax)
        #endinfograph = self.currentState.finalize()
        #for ax in endinfograph:
        #    self.store.add(ax)

    def startElement(self, name: str, attrs: AttributesImpl) -> None:
        attrs_ = dict(attrs)
        other_attrs, namespaces, defaultNS = extract_namespaces(attrs_)
        namespaces = {**self.currentState.namespaces, **namespaces}
        if defaultNS == None:
            defaultNS = self.currentState.default_namespace
        assert defaultNS is not None
        qname = name2qname(name, defaultNS, namespaces)
        self.currentState = self.currentState.transition(qname, attrs_,
                                                         namespaces, defaultNS)

    def endElement(self, name):
        if isinstance(self.currentState, _start):
            raise Exception("Got one xml endelement too much.")
        else:
            self.currentState.close()
            self.states.pop()

    def startElementNS(self, name, qname, attrs):
        """Cant implement this with feature Namespaces enabled because
        i need access to namespaces within binding.
        """
        raise NotImplementedError()

    def endElementNS(self, name, qname):
        raise NotImplementedError()

    def characters(self, content):
        self.currentState.add_characters(content)

    def ignorableWhitespace(self, content):
        pass

def extract_namespaces(attrs: Mapping[str, str],
              defaultNS: Optional[str] = None,
              ) -> Tuple[Mapping[str, str], Mapping[str, str], Optional[str]]:
    other_attrs = {}
    namespaces = {}
    for key, x in attrs.items():
        if key.startswith("xmlns:"):
            namespaces[key[6:]] = x
        elif key.startswith("xmlns"):
            defaultNS = x
        else:
            other_attrs[key] = x
    return other_attrs, namespaces, defaultNS
