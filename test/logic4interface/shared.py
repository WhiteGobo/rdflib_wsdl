from collections import namedtuple

LogicTestInformation = namedtuple(
        "LogicTestInformation",
        ['graph', 'inputgraph', 'outputgraph', 'inputnode2var', 'outputnode2var', 'basegraph', 'interface_operation_iri', 'test_input_data', 'test_output_data', 'input_data_rif', 'output_data_rif'],
        )
"""Collection of all information for testing the logic implementation within
an interface.
"""
