from .wsdl_components import InterfaceOperation, Endpoint
from typing import Iterable

def load_usable_endpoints_for(
        interface_operation: InterfaceOperation,
        ) -> Iterable[Endpoint]:
    interface = interface_operation.parent
    description = interface.parent
    for service in description.services:
        if service.interface == interface:
            for endpoint in service.endpoints:
                yield endpoint

