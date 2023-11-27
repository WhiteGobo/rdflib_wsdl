"""
:TODO: replace NS with RIF on deeper level
"""
from typing import Iterable, Mapping, List, Any, Optional, Union, Tuple
from rdflib import Graph, URIRef, BNode, Literal, RDF, IdentifiedNode, Variable
from rdflib.collection import Collection
from .generell import easyDescription, easyInterfaceOperation, easyInterface, _easyIMR
try:
    from rdflib_rif.rif_namespace import RIF
except ModuleNotFoundError:
    from rdflib import Namespace
    RIF = Namespace("http://www.w3.org/2007/rif#")
from ..shared import RDFLOGICWSDL as NS
from ..shared import _ns_rdflogic_wsdl as _ns
from ..shared import WSDL, parse_message_reference_iri, parse_interface_operation_iri
from collections import defaultdict
from xml.etree import ElementTree as ET
import logging
logger = logging.getLogger(__name__)
from ..wsdl_components import Description, InterfaceMessageReference
from ..extensions import rdf_interfaces
from ..extensions.rdf_interfaces import RetrieveFailed

_table3 = {
        ("Document," "directive"): (NS.directives, 2),
        ("Group", "sentence"): (NS.sentences, 2),
        ("Forall", "declare"): (NS.vars, 2),
        ("Exists", "declare"): (NS.vars, 2),
        ("And", "formula"): (NS.formulas, 2),
        ("Or", "formula"): (NS.formulas, 2),
        ("Frame", "slot"): (NS.slots, 3),
        ("Atom", "slot"): (NS.namedargs, 4),
        ("Expr", "slot"): (NS.namedargs, 4),
        }
"""
`https://www.w3.org/TR/2013/NOTE-rif-in-rdf-20130205/#General_Mapping`_
"""
def _get_property_and_mode(parent_name, child_name, ordered=False, **kwargs):
    if ordered:
        rdfproperty = getattr(NSR, child_name)
        mode = 0
    else:
        try:
            rdfproperty, mode = _table3[parent_name, child_name]
        except KeyError:
            rdfproperty = getattr(NS, child_name)
            mode = 1
    return rdfproperty, mode

def _translate_element(element: ET.Element, g: Graph) -> IdentifiedNode:
    """expects all elements without namespace.
    Compare to `https://www.w3.org/TR/2013/NOTE-rif-in-rdf-20130205/#Mapping_from_RIF_XML_to_RDF_Graphs`_
    """
    iri_elem = element.find("id")
    iri = BNode() if iri_elem is None else _translate_element(iri_elem, g)
    prop2array = {}
    if element.tag in (_et_Var, _et_Const):
        raise NotImplementedError()
    else:
        for sub_elem in element:
            if sub_elem.tag == "id":
                continue
            prop, mode = _get_property_and_mode(element.tag, sub_elem.tag,
                                                **sub_elem.attrib)
            if mode == 0:
                child = BNode()
                g.add((iri, prop, child))
                childarray = Collection(g, child)
                for subsub in sub_elem:
                    childarray.append(_translate_element(subsub, g))
            elif mode == 1:
                sub_iri = _translate_element(sub_elem, g)
                g.add((iri, prop, sub_iri))
            elif mode == 2:
                prop2array.setdefault(prop, []).append(sub_elem)
            elif mode == 3:
                child = BNode()
                prop2array.setdefault(prop, []).append(child)
                g.add((child, RDF.type, NS.Slot))
                key, value = iter(sub_elem)
                g.add((child, NS.slotkey, _translate_element(key, g)))
                g.add((child, NS.slotvalue, _translate_element(value, g)))
            elif mode == 4:
                child = BNode()
                prop2array.setdefault(prop, []).append(child)
                g.add((child, RDF.type, NS.NamedArg))
                name, value = iter(sub_elem)
                g.add((child, NS.argname, _translate_element(name, g)))
                g.add((child, NS.argvalue, _translate_element(value, g)))
            else:
                raise Exception()
    for prop, sub_elems in prop2array:
        child = BNode()
        g.add((iri, prop, child))
        childarray = Collection(g, child)
        for subsub in sub_elems:
            childarray.append(_translate_element(subsub, g))

class LogicDescription(easyDescription):
    _logic_formulas: List["LogicFormula"]
    def __init__(self, targetNamespace):
        super().__init__(targetNamespace)
        self._logic_formulas = []

    def get(self, namespace: str, name: str, **kwargs: Any) -> Any:
        if namespace == _ns:
            if name == "logic formulas":
                return self._logic_formulas
        super().get(namespace, name, **kwargs)

class LogicInterfaceOperation(easyInterfaceOperation):
    @classmethod
    def from_rdfgraph(cls, graph: Graph, iri: URIRef,
                      interface: Optional[easyInterface] = None,
                      create_message_references: bool = True):
        #ignore namespace and parents name
        _, _, name = parse_interface_operation_iri(iri)
        if interface is None:
            interface_iri = graph.value(predicate=WSDL.interfaceOperation,
                                        object=iri)
            interface = easyInterface.from_rdfgraph(graph, interface_iri)
        self = cls(interface, name)
        if create_message_references:
            list_imr_elem = graph.objects(iri, WSDL.interfaceMessageReference)
            list_imr = []
            for imr_iri in list_imr_elem:
                tmp_imr = LogicMessageReference.from_rdfgraph(
                        graph, imr_iri,
                        interface_operation = self,
                        )
        return self
        

class LogicMessageReference(_easyIMR):
    def direction(self):
        return self._message_label

    @classmethod
    def from_rdfgraph(
            cls, graph: Graph, iri: URIRef,
            interface_operation: Optional[easyInterfaceOperation] = None,
            ):
        _, _, _, message_label = parse_message_reference_iri(iri)
        name_split = iri.split("/")
        message_label = name_split[-1][:-1]
        if interface_operation is None:
            raise NotImplementedError()
        return cls(interface_operation, message_label)

class LogicInterface(easyInterface): ...

def _term_NS2RDF(wsdl_graph, const_or_var) -> Literal | URIRef | BNode | Variable:
    try:
        iri_as_literal, = wsdl_graph.objects(const_or_var, NS.constIRI)
    except ValueError:
        pass
    else:
        return URIRef(iri_as_literal)
    try:
        varname, = wsdl_graph.objects(const_or_var, NS.varname)
    except ValueError:
        pass
    else:
        return Variable(varname)
    raise NotImplementedError(dict(wsdl_graph.predicate_objects(const_or_var)))

class LogicFormula:
    """A rdf graph representation for elements of a message.
    Eg. you can represent the information needed to correctly invoke
    an interface and represent the resulting information.
    Its to be noted that information is noted in a open world
    assumption, so missing information doesnt mean the missing information
    is false or in other words, already existing information wont be
    overwritten.
    """
    def __init__(self, graph: Graph, iri: URIRef):
        self._graph = graph
        self._iri = iri

    def create_rdfgraph(self) -> Tuple[Graph, Mapping[Variable, IdentifiedNode]]:
        formulas_iri, = self._graph.objects(self._iri, NS.formulas)
        formulas = Collection(self._graph, formulas_iri)
        g = Graph()
        var2node = {}
        for formula_iri in formulas:
            subj_reif = self._graph.value(formula_iri, NS.object)
            subj = _term_NS2RDF(self._graph, subj_reif)
            slots_iri = self._graph.value(formula_iri, NS.slot)
            for slot in Collection(self._graph, slots_iri):
                slotkey_reif = self._graph.value(slot, NS.slotkey)
                slotvalue_reif = self._graph.value(slot, NS.slotvalue)
                slotkey = _term_NS2RDF(self._graph, slotkey_reif)
                slotvalue = _term_NS2RDF(self._graph, slotvalue_reif)
                g.add((var2node.setdefault(x, BNode())
                      if isinstance(x, Variable)
                      else x
                      for x in (subj, slotkey, slotvalue)))
        return g, var2node

    @property
    def iri(self) -> URIRef:
        return self._iri

    def __iter__(self):
        return iter(self._graph)

    def axiom_bind_to(self, imr: InterfaceMessageReference):
        return imr.iri, NS.elementsDescribedBy, self.iri

    def axiom_implement_in_description(self, description: Description):
        return description.iri, NS.logicFormula, self.iri

    @classmethod
    def create_from_rdfgraph(cls, rdfgraph: Graph,
                             node2vars: Mapping[IdentifiedNode, str],
                             targetNamespace: str, name: str):
        """Uses the reification of RIF to generate information about the
        given graph.
        """
        g = Graph()
        obj2slots = {}
        term2node = {}
        for ax in rdfgraph:
            obj, slotkey, slotvalue = ax
            obj2slots.setdefault(obj, []).append((slotkey, slotvalue))
            for x in ax:
                if x in term2node:
                    continue
                node = BNode()
                term2node[x] = node
                if x in node2vars:
                    g.add((node, RDF.type, NS.Var))
                    g.add((node, NS.varname, Literal(node2vars[x])))
                elif isinstance(x, URIRef):
                    g.add((node, RDF.type, NS.Const))
                    g.add((node, NS.constIRI, Literal(str(x))))
                elif isinstance(x, BNode):
                    g.add((node, RDF.type, NS.Const))
                    g.add((node, NS.constname, Literal(str(x))))
                elif isinstance(x, Literal):
                    g.add((node, RDF.type, NS.Const))
                    g.add((node, NS.value, x))
                else:
                    raise Exception("unhandled nodetype of %s" % x)

        basenode = URIRef("%s#logicwsdl.logicformula(%s)"
                          % (targetNamespace, name))
        tmp_node = BNode()
        g.add((basenode, NS.formulas, tmp_node))
        framearray = Collection(g, tmp_node)
        for obj, slots in obj2slots.items():
            obj_node = term2node[obj]
            framenode = BNode()
            framearray.append(framenode)
            _s = BNode()
            g.add((framenode, RDF.type, NS.Frame))
            g.add((framenode, NS.object, obj_node))
            g.add((framenode, NS.slot, _s))
            slots_coll = Collection(g, _s)
            for key, value in slots:
                key_node, value_node = (term2node[t] for t in (key, value))
                slotnode = BNode()
                slots_coll.append(slotnode)
                g.add((slotnode, NS.slotkey, key_node))
                g.add((slotnode, NS.slotvalue, value_node))
        return cls(g, basenode)


    @classmethod
    def from_elementTree(cls, tree: ET.ElementTree):
        for elem in tree.findall("{%s}*" % _ns):
            _, name = elem.tag.split("}")
            elem.tag = name
        graph = Graph()
        basenode = _translate_element(tree, graph)
        return cls(graph, basenode)


class Frame:
    """All information is represented in simple asdf as frames.
    So if you have a simple information graph represented in rdf, every
    axiom `(s, p, o)` is represented as a frame `s[p->o]`. This representation
    conforms to `formulas in RIF<https://www.w3.org/TR/2013/REC-rif-core-20130205/#Formulas_of_RIF-Core_2>`_.
    """

class Constant:
    """All terms within a LogicFormula which are constant."""

class External:
    """All terms that are to be derived by an interpreter. This
    wont be implemented yet.
    """

class Var:
    """Variables cant represent the elements of a message or can be anonymous
    terms within an information graph. Variables are to be considered equal
    to elemnts of a message if the name of the element is equal to be variable
    name. Its suggested, that every element of an inputmessage is present
    within the logic formula.
    """

def create_inputfinder(wsdlgraph: Graph,
                       interface_operation_iri: IdentifiedNode):
    raise NotImplementedError("No method to generate sparql query with rdflib")
    imr_iris = list(wsdlgraph.objects(interface_operation_iri,
                                      WSDL.interfaceMessageReference))
    try:
        input_iri, = (x for x in imr_iris
                      if (x, RDF.type, WSDL.InputMessage) in wsdlgraph)
    except ValueError as err:
        raise Exception("Expected exactly one inputmessage.") from err
    logic_formula_iri = wsdlgraph.value(input_iri,
                                        NS.elementsDescribedBy)
    logic_formula = LogicFormula(wsdlgraph, logic_formula_iri)
    input_graph, var2node = logic_formula.create_rdfgraph()
    logger.critical(input_graph.serialize())
    g = Graph()
    for x in logic_formula:
        g.add(x)
    logger.critical(g.serialize())
    raise Exception()
rdf_interfaces.extras_interface_operation.setdefault("find_usable_inputs", []).append(create_inputfinder)

def get_input_logic_formula(wsdlgraph: Graph,
                            interface_operation_iri: IdentifiedNode):
    imr_iris = list(wsdlgraph.objects(interface_operation_iri,
                                      WSDL.interfaceMessageReference))
    try:
        input_iri, = (x for x in imr_iris
                      if (x, RDF.type, WSDL.InputMessage) in wsdlgraph)
    except ValueError as err:
        raise Exception("Expected exactly one inputmessage.") from err
    logic_formula_iri = wsdlgraph.value(input_iri,
                                        NS.elementsDescribedBy)
    return LogicFormula(wsdlgraph, logic_formula_iri)
rdf_interfaces.extras_interface_operation.setdefault(
        "get_input_logic_formula", []).append(get_input_logic_formula)

def get_output_logic_formula(wsdlgraph: Graph,
                            interface_operation_iri: IdentifiedNode):
    imr_iris = list(wsdlgraph.objects(interface_operation_iri,
                                      WSDL.interfaceMessageReference))
    try:
        output_iri, = (x for x in imr_iris
                      if (x, RDF.type, WSDL.OutputMessage) in wsdlgraph)
    except ValueError as err:
        raise Exception("Expected exactly one outputmessage.") from err
    logic_formula_iri = wsdlgraph.value(output_iri,
                                        NS.elementsDescribedBy)
    return LogicFormula(wsdlgraph, logic_formula_iri)
rdf_interfaces.extras_interface_operation.setdefault(
        "get_output_logic_formula", []).append(get_output_logic_formula)
