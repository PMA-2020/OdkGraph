"""A module for generating a graph structure from an XlsForm.

Module attributes:
    OdkGraph: Class for representing the graph structure
    cli: A routine for running a command-line interface
"""
import argparse
from typing import Iterable, List

import networkx as nx
import xlrd

from .xlsformrow import XlsFormRow


class OdkGraph:
    """Class to represent the graph structure of an XlsForm.

    Class attributes:
        DIRECTED_TO_DEPENDENCY: True if and only if an edge points to
            a dependency

    Instance attributes:
        ordered_nodes: A list of XlsFormRows
        node_lookup: A dictionary of ODK name key to XlsFormRow value
        network: The networkx.DiGraph object for this XlsForm
    """

    DIRECTED_TO_DEPENDENCY = False

    def __init__(self, path: str):
        """Initialize an OdkGraph object.

        This __init__ reads in an XlsForm file and parses out the graph
        nodes. A node is represented as an XlsFormRow. Edges for the
        graph come from the dependencies between XlsFormRows.

        Args:
            path: The path to the XlsForm file
        """
        self.ordered_nodes = self.parse_ordered_nodes(path)
        self.node_lookup = {node.row_name: node for node in self.ordered_nodes}
        for node in self.ordered_nodes:
            unsorted_dependencies = [self.node_lookup[name] for name in
                                     node.dependency_counter]
            dependencies = sorted(unsorted_dependencies, key=lambda x: x.rowx)
            node.dependencies = dependencies
        self.network = self.generate_network()

    @staticmethod
    def parse_ordered_nodes(path: str) -> List[XlsFormRow]:
        """Parse nodes (rows) from an XlsForm.

        Args:
            path: The path to the XlsForm file

        Returns:
            A list of XlsFormRows, in the same order as the XlsForm.
        """
        ordered_nodes = []
        ancestors = []
        workbook = xlrd.open_workbook(path)
        survey = workbook.sheet_by_name('survey')
        header = survey.row_values(0)
        for i, row in enumerate(survey.get_rows()):
            if i == 0:
                continue
            row_values = (cell.value for cell in row)
            value_strings = (str(value).strip() for value in row_values)
            this_row_dict = {k: v for k, v in zip(header, value_strings)}
            row_type = this_row_dict.get('type')
            row_name = this_row_dict.get('name')
            if row_type in ('end group', 'end repeat'):
                ancestors.pop()
                continue
            if row_type and row_name:
                xlsformrow = XlsFormRow(i, row_type, row_name, this_row_dict,
                                        list(ancestors))
                ordered_nodes.append(xlsformrow)
            if row_type in ('begin group', 'begin repeat'):
                ancestors.append(row_name)
        return ordered_nodes

    def generate_network(self) -> nx.DiGraph:
        """Create a `networkx.DiGraph` object from this object.

        Each node is added to a directed graph. Then the edges are
        added.

        Returns:
            The `networkx.DiGraph` object representing this object
        """
        graph = nx.DiGraph()
        for node in self.ordered_nodes:
            graph.add_node(node)
            # Possibly useful instead
            # graph.add_node(node, **node.row_dict)
        for node in self.ordered_nodes:
            iterator = node.dependency_pair_iter(self.DIRECTED_TO_DEPENDENCY)
            graph.add_edges_from(iterator)
        return graph

    def all_dependencies_from_nodes(self, nodes: Iterable[XlsFormRow]) \
            -> List[XlsFormRow]:
        """Get the sorted list of all dependencies for input nodes.

        This routine gets all the dependencies for each node in the
        input iterable. The result is de-duped, sorted, and the input
        nodes are removed from that result.

        Args:
            nodes: An iterable of XlsFormRow objects.

        Returns:
            A list of nodes sorted by the row number.
        """
        node_set = set(nodes)
        dependencies = set()
        for node in node_set:
            ancestors = nx.algorithms.dag.ancestors(self.network, node)
            dependencies |= ancestors
        diff = dependencies - node_set
        sorted_nodes = sorted(list(diff), key=lambda x: x.rowx)
        return sorted_nodes

    def successors(self, node: XlsFormRow) -> List[XlsFormRow]:
        """Get the direct dependencies of input node."""
        result = list(self.network.successors(node))
        return result

    def predecessors(self, node: XlsFormRow) -> List[XlsFormRow]:
        """Get the nodes that depend on input node."""
        result = list(self.network.predecessors(node))
        return result

    def order(self):
        """Return the number of nodes in the graph."""
        result = self.network.order()
        return result

    def size(self, weight: str = None):
        """Return the number of edges or total of all edge weights."""
        result = self.network.size(weight)
        return result

    def simple_cycles(self) -> list:
        """Return a list of cycles in the directed graph."""
        result = list(nx.simple_cycles(self.network))
        return result

    def is_directed_acyclic_graph(self) -> bool:
        """Determine if this is a directed acyclic graph."""
        result = nx.algorithms.is_directed_acyclic_graph(self.network)
        return result

    def isolates(self) -> List[XlsFormRow]:
        """Return a list of isolate nodes."""
        result = list(nx.isolates(self.network))
        return result

    def terminal_nodes(self) -> List[XlsFormRow]:
        """Return a list of terminal nodes.

        A terminal node is a node with at least one in-edge and zero
        out-edges.
        """
        gen = (
            n for n in self.network if
            self.network.out_degree(n) == 0 and self.network.in_degree(n) > 0
        )
        return list(gen)

    def forward_dependencies(self) -> list:
        """Get a list of forward dependency pairs.

        In ODK, typically a row depends on other rows that are defined
        before it. This method lists out rows that depend on rows
        defined after it.
        """
        result = []
        for node in self.ordered_nodes:
            for dependency in node.dependencies:
                if node.rowx < dependency.rowx:
                    found = (node, dependency)
                    result.append(found)
        return result

    def __getitem__(self, key):
        """Support custom indexing.

        Args:
            key: If integer, then treated as array index. If string,
                then treated as an ODK name for the row. If slice,
                then further processing is done for the slice.

        Returns:
            If key is an integer, returns the item at that array index.
            If key is a string, returns the XlsFormRow with that ODK
            name. If a slice, then returns a list for that slice.
        """
        if isinstance(key, int):
            return self.ordered_nodes[key]
        elif isinstance(key, str):
            return self.node_lookup[key]
        elif isinstance(key, slice):
            slicer = self._get_slicer(key)
            return self.ordered_nodes[slicer]
        else:
            raise TypeError(key)

    def _get_slicer(self, key: slice) -> slice:
        """Take an uncleaned input slice and return a cleaned slice.

        Can handle integers and strings, not a mix. If strings, then
        step attribute must be None.

        Args:
            key: A slice with all integer or all string components.

        Returns:
            A slice with integer components.
        """
        attributes = (key.start, key.stop, key.step)
        non_null = filter(None, attributes)
        if all(isinstance(i, int) for i in non_null):
            return key
        elif all(isinstance(i, str) for i in non_null):
            start = self.node_lookup.get(key.start)
            if start:
                start = self.ordered_nodes.index(start)
            stop = self.node_lookup.get(key.stop)
            if stop:
                stop = self.ordered_nodes.index(stop)
            slicer = slice(start, stop)
            return slicer
        else:
            raise TypeError(key)

    def __iter__(self):
        """Iterate over nodes in order of the XlsForm rows."""
        return iter(self.ordered_nodes)

    def __len__(self):
        """Return the length as the number of nodes in this graph."""
        return len(self.ordered_nodes)

    def __repr__(self):
        """Get a representation of this object."""
        this_repr = f'<OdkGraph: {len(self.ordered_nodes)} nodes>'
        return this_repr


def cli():
    """Run a CLI for this module."""
    prog_desc = 'Generate a directed graph from an XlsForm.'
    parser = argparse.ArgumentParser(description=prog_desc)
    parser.add_argument('xlsform', help='The XlsForm to analyze.')
    args = parser.parse_args()
    odkgraph = OdkGraph(args.xlsform)
    # TODO: Do something with the graph
    print(odkgraph)
