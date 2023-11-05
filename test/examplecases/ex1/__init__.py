"""

XML taken from example 2-1 from `https://www.w3.org/TR/wsdl20-primer/#basics-greath-scenario`_.
RDF taken from `https://www.w3.org/TR/wsdl20-rdf/#example`_
"""
from os import getcwd
from os.path import join, split

path, init_file = split(__file__)
_tmp = "ex1%s"
format_to_file = {
        "ttl": join(path, _tmp % ".ttl"),
        "wsdl": join(path, _tmp % ".wsdl"),
        }
