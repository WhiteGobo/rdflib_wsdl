from rdflib import Graph, IdentifiedNode
from typing import Mapping, Callable, Dict, Iterable, Any

class RetrieveFailed(Exception):
    """Raised if rdfgraph doesnt provide enough information or wrong
    information, so that the extension cant be used.
    """

EXTRAS = Dict[str, Iterable[Callable[[Graph, IdentifiedNode], Any]]]

extras_endpoint: EXTRAS = {}
extras_interface_operation: EXTRAS = {}

