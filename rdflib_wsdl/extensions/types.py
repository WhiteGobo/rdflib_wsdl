from xml.etree import ElementTree as ET
from typing import Dict, Tuple, Callable
from ..shared import _ns_xs
from rdflib import Graph

TYPES_EXTENSIONS: Dict[Tuple[str, str], Callable[[ET.ElementTree], Graph]] = {}

def convert_xsschema(element_tree: ET.ElementTree):
    """
    :TODO: Currently just a blueprint
    """
    g = Graph()
    #ET.dump(element_tree)
    # implement here transformation
    #g.parse(data=q, asdf)
    return g

TYPES_EXTENSIONS[(_ns_xs, "schema")] = convert_xsschema

