"""

XML taken from example 2-1 from `https://www.w3.org/TR/wsdl20-primer/#basics-greath-scenario`_.
RDF taken from `https://www.w3.org/TR/wsdl20-rdf/#example`_
"""
from os import getcwd
from os.path import join, split

from importlib.resources import files
from . import local
localfiles = files(local)

path_ttl = localfiles.joinpath("ex1.ttl")
path_wsdl = localfiles.joinpath("ex1.wsdl")
