import pytest
import rdflib.plugin
import rdflib.parser

@pytest.fixture
def register_wsdl_format() -> None:
    rdflib.plugin.register("wsdl", rdflib.parser.Parser,
                           "rdflib_wsdl", "WSDLXMLParser")
