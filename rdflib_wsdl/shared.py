from rdflib import Namespace, RDF, Literal, URIRef
from collections.abc import Mapping, Iterable
from typing import Tuple, Optional

_ns_wsdl = "http://www.w3.org/ns/wsdl"
"""Standard namespace of wsdl"""
_ns_wsdlx = "http://www.w3.org/ns/wsdl-extensions"
_ns_wsdlrdf = "http://www.w3.org/ns/wsdl-rdf#"
_ns_wsoap = "http://www.w3.org/ns/wsdl/soap"
_ns_whttp = "http://www.w3.org/ns/wsdl/http#"
_ns_wrpc = "http://www.w3.org/ns/wsdl/rpc#"
_ns_sawsdl = "http://www.w3.org/ns/sawsdl#"
_ns_xs = "http://www.w3.org/2001/XMLSchema"
"""Standard namespace of xs"""
WHTTP = Namespace("http://www.w3.org/ns/wsdl/http#")
WSDL = Namespace("http://www.w3.org/ns/wsdl-rdf#")
WSDLX = Namespace("http://www.w3.org/ns/wsdl-extensions#")
WSDL_RDF = Namespace(_ns_wsdlrdf)
WSOAP = Namespace("http://www.w3.org/ns/wsdl/soap#")
SAWSDL = Namespace(_ns_sawsdl)

MEP_inOnly = "http://www.w3.org/ns/wsdl/in-only"
MEP_robustInOnly = "http://www.w3.org/ns/wsdl/robust-in-only"
MEP_inOut = "http://www.w3.org/ns/wsdl/in-out"
MEP_inOptionalOut = "http://www.w3.org/ns/wsdl/in-opt-out"
MEP_outOnly = "http://www.w3.org/ns/wsdl/out-only"
MEP_robustOutOnly = "http://www.w3.org/ns/wsdl/robust-out-only"
MEP_outIn = "http://www.w3.org/ns/wsdl/out-in"
MEP_outOptionalIn = "http://www.w3.org/ns/wsdl/out-opt-in"

def name2qname(name: str,
               defaultNS: str,
               otherNS: Mapping[str, str],
               ) -> Tuple[str, str]:
    qname = name.split(":")
    if len(qname) == 1:
        return (defaultNS, name)
    elif len(qname) == 2:
        return (otherNS[qname[0]], qname[1])
    else:
        raise Exception("Broken element name %s" % name)

def extract_namespaces(attrs: Mapping[str, str],
              defaultNS: Optional[str] = None,
              ) -> Tuple[Mapping[str, str], str]:
    """
    """
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
