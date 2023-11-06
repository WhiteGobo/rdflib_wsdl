wsdl parser for rdflib
======================

"Web Services Description Language Version 2.0 (WSDL 2.0) provides a model and an XML format for describing Web services." [w3c-specification](https://www.w3.org/TR/wsdl/#intro)

This module should provide a simple parser plugin for rdflib.
You can parse wsdl per:

```
	rdflib.Graph().parse("path/to/wsdl.wsdl", format="wsdl")
```


extensions
----------

As WSDL is extensible this package supports extensions for parsers (serializer not yet implemented).
The supported entry points are:
```
    'rdflib_wsdl.extensions.parser'
```
For further documentation to implement extensions and check all available 
extensions see `rdflib_wsdl.extensions.parser`
