wsdl parser for rdflib
======================

"Web Services Description Language Version 2.0 (WSDL 2.0) provides a model and an XML format for describing Web services." [w3c-specification](https://www.w3.org/TR/wsdl/#intro)

This module should provide a simple parser plugin for rdflib.
You can parse wsdl per:

```
	rdflib.Graph().parse("path/to/wsdl.wsdl", format="wsdl")
```
