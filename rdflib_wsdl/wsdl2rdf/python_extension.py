from .extensions import ParserData
from ..shared import PYTHONWSDL, _ns_python_wsdl
from rdflib import Graph, RDF
from ..wsdl_components import Endpoint
from .class_MapperWSDL2RDF import _create_id

def _ext_python_map_endpoint(g: Graph, endpoint: Endpoint):
    try:
        import_path = endpoint.get(_ns_python_wsdl, "module")
    except KeyError:
        return
    import_name = endpoint.get(_ns_python_wsdl, "method")
    elemid = _create_id(endpoint)
    g.add((elemid, RDF.type, PYTHONWSDL.method))
    g.add((elemid, PYTHONWSDL.name, Literal(import_name)))
    g.add((elemid, PYTHONWSDL.path, Literal(import_path)))

python_extension = ParserData(endpoint=_ext_python_map_endpoint)
