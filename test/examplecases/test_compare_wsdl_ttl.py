import pytest
from pytest import param, skip
from rdflib import Graph
from rdflib.compare import to_isomorphic, graph_diff
import logging
logger = logging.getLogger(__name__)
from . import ex1
from collections import namedtuple
DescriptionInfo = namedtuple("DescriptionInfo",
                             ["path_ttl", "path_wsdl", "graph"],
                             )

@pytest.fixture(params=[
    param(ex1, id="greath.example.com/2004/wsdl/resSvc"),
    ])
def description_info(request, register_wsdl_format) -> dict[str, str]:
    """Returns a dictionary with a fileformat to a file. Each file contains
    the same information. The fileformat is compatible to rdflib.
    """
    q = request.param
    g = Graph().parse(q.path_ttl, format="ttl")
    return DescriptionInfo(q.path_ttl, q.path_wsdl, g)


def test_compareDifferentFormats(register_wsdl_format, description_info):
    compare_graph = description_info.graph
    if compare_graph is None:
        skip("No default graph given")
    format2path = [ (key, info) for key, info in [
                   ("ttl", description_info.path_ttl),
                   ("wsdl", description_info.path_wsdl),
                   ] if info is not None ]
    #format2path = iter(compareFiles.items())
    iso_comp = to_isomorphic(compare_graph)
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
