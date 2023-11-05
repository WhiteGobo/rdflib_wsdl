import setuptools

long_description = """This module allows rdflib to load wsdl.

You can load wsdl files via `rdflib.Graph.parse` with the parser plugin `wsdl`
or `wsdl/xml`:
```
g = Graph().parse(PathToWSDL, format="wsdl")
```
"""

setuptools.setup(
    name='rdflib_wsdl',
    version='0.1',
    description='Parser for wsdl as plugin for rdflib',
    long_description=long_description,
    long_description_content_type="text/markdown",

    # url="https://example.com/rif-parser-rdflib",
    project_urls={
        "Homepage": "https://github.com/WhiteGobo/rdflib_rif",
    },
    
    author='Richard Focke Fechner',
    author_email='richardfechner@posteo.net',

    py_modules=['rdflib_wsdl'],
    #scripts = ['rif_parser.py',],

    packages=setuptools.find_packages(),
    install_requires=['rdflib'],
    
    # Classifiers allow your Package to be categorized based on functionality
    classifiers = [
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],

    # Entry points speficy, what is the functionability in rdflib
    # Also this sepicifies, how the plugin is reached
    entry_points = {
        'rdf.plugins.parser': [
            'wsdl = rdflib_wsdl:WSDLXMLParser',
            'wsdl/xml = rdflib_wsdl:WSDLXMLParser',
        ],
    },

    extras_require = {
        #'rifxml validation': ['lxml'],
        #'test':  ['lxml', 're', 'xml'],
    },
)
