from rdflib import Graph, RDF, Namespace, IdentifiedNode, URIRef
from typing import List, Optional, Iterable
from ..shared import PYTHONWSDL, parse_endpoint_uri, WSDL, parse_binding_uri, parse_service_uri, parse_interface_uri
from ..generate_helper.generell import easyDescription, easyService, easyBinding, easyInterface
from ..generate_helper.python import _python_endpoint_importer

def load_binding(
        graph: Graph, binding_uri: URIRef,
        ) -> easyBinding:
    targetNamespace, name = parse_binding_uri(binding_uri)
    description = easyDescription(targetNamespace)
    return easyBinding(description, name)

def load_service(graph: Graph, description: easyDescription,
                 service_uri: URIRef):
    targetNamespace, name = parse_service_uri(service_uri)
    interface_uri = graph.value(service_uri, WSDL.implements)
    interface = load_interface(graph, description, interface_uri)
    return easyService(description, name, interface)

def load_interface(graph: Graph, description: easyDescription,
                   interface_uri: URIRef):
    targetNamespace, name = parse_interface_uri(interface_uri)
    return easyInterface(description, name)

def load_python_endpoints(
        graph: Graph,
        endpoint_uris: Optional[Iterable[URIRef]] = None,
        ) -> Iterable:
    if endpoint_uris is None:
        endpoint_uris = list(graph.subjects(RDF.type, PYTHONWSDL.method))

    for elem in endpoint_uris:
        assert isinstance(elem, URIRef)
        targetNamespace, service_name, name = parse_endpoint_uri(elem)
        binding_elem = graph.value(elem, WSDL.usesBinding)
        service_elem = graph.value(predicate=WSDL.endpoint, object=elem)
        assert isinstance(binding_elem, URIRef)
        binding = load_binding(graph, binding_elem)
        description = binding.parent
        service = load_service(graph, description, service_elem)

        import_path = graph.value(subject=elem, predicate=PYTHONWSDL.path)
        import_name = graph.value(subject=elem, predicate=PYTHONWSDL.name)
        if import_path is None or import_name is None:
            raise Exception("Cant import method if without a path or a name."
                            "\npath: %s\nname:%s" % (import_path, import_name))
        yield _python_endpoint_importer(service, binding,
                                        str(import_path),
                                        str(import_name),
                                        name)
