import pytest
from pytest import param
from rdflib import Graph
from rdflib.compare import to_isomorphic, graph_diff
import logging
logger = logging.getLogger(__name__)
from . import ex1

ex1.format_to_file
@pytest.fixture(params=[
    param(ex1.format_to_file, id="helloWorld")
    ])
def compareFiles(request) -> dict[str, str]:
    """Returns a dictionary with a fileformat to a file. Each file contains
    the same information. The fileformat is compatible to rdflib.
    """
    return request.param


def test_compareDifferentFormats(register_wsdl_format, compareFiles):
    format2path = iter(compareFiles.items())
    fileformat, filepath = next(format2path)
    comparegraph = Graph().parse(filepath, format=fileformat)
    iso_comp = to_isomorphic(comparegraph)
    for fileformat, filepath in format2path:
        nextgraph = Graph().parse(filepath, format=fileformat)
        iso_next = to_isomorphic(nextgraph)
        inboth, incomp, innext = graph_diff(iso_comp, iso_next)
        try:
            assert not innext and not incomp, "Not the same information"
        except AssertionError:
            logger.info("Comparegraph holds info:\n%s" % iso_comp.serialize())
            logger.info("Next graph holds info:\n%s" % iso_next.serialize())
            logger.debug("info only in compgraph:\n%s" % incomp.serialize())
            logger.debug("info only in nextraph:\n%s" % innext.serialize())
            raise
