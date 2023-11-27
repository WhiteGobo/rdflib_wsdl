Parsing and Serializer
======================

:term:`Parsing` and :term:`Serializing` is done via rdflib core mechanics 
rdflib.Graph.serialize and rdflib.Graph.parse. The praser and serialiazer 
are registered under ``'wsdl'`` .

Serializer is not yet implemented.

.. code-block:: python

        from rdflib import Graph
        g = Graph().parse(data_path, format='wsdl')
        #print(g.serialize(format='wsdl'))

