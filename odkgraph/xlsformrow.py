"""This module creates and analyzes XlsForm rows.

A row represents a single question or calculate, or in other words, a
data collection unit.

Module attributes:
    ODK_VAR_REGEX: A regex string to parse ODK variable references
    ODK_VAR_REGEX_PROG: A compiled regex based on ODK_VAR_REGEX
    XlsFormRow: A class for representing an XlsForm row
"""
from collections import Counter
import re


ODK_VAR_REGEX = r'\$\{(.*?)\}'
ODK_VAR_REGEX_PROG = re.compile(ODK_VAR_REGEX)


class XlsFormRow:
    """Class to hold information associated with a row in an XlsForm.

    The instance attributes `dependency_counter` and `dependencies` are
    calculated. The `dependency_counter` is a Counter dictionary to
    keep track of how many times the dependency appears in this
    instance's data. The `dependencies` are the XlsFormRows, sorted
    according to the rowx attribute.

    Instance attributes:
        rowx: The 0-indexed row in the survey tab where this row is
        row_type: The value in the 'type' column
        row_name: The value in the 'name' column
        row_dict: The survey tab header is the keys, the row entries
            are the values
        ancestors: The names of the groups and repeats that this entry
            is nested under, in order
        dependency_counter: A Counter dictionary of dependencies
        dependencies: The XlsFormRows associated with this row's
            dependencies.
    """

    # pylint: disable=too-many-arguments
    def __init__(self, rowx: int, row_type: str, row_name: str, row_dict: dict,
                 ancestors: list):
        """Initialize an XlsFormRow and parse out dependency names.

        Args:
            rowx: The 0-indexed row in the survey tab where this row is
            row_type: The value in the 'type' column
            row_name: The value in the 'name' column
            row_dict: The survey tab header is the keys, the row entries
                are the values
            ancestors: The names of the groups and repeats that this entry
                is nested under, in order
        """
        self.rowx = rowx
        self.row_type = row_type
        self.row_name = row_name
        self.row_dict = row_dict
        self.ancestors = ancestors

        self.dependency_counter = self.parse_dependencies()
        self.dependencies = []

    def parse_dependencies(self) -> Counter:
        """Parse out dependency names from the fields of this row.

        Returns:
            A Counter dictionary of dependencies.
        """
        dependencies = Counter()
        for value in self.row_dict.values():
            found = ODK_VAR_REGEX_PROG.findall(value)
            this_counter = Counter(found)
            dependencies.update(this_counter)
        if self.ancestors:
            immediate_ancestor = [self.ancestors[-1]]
            dependencies.update(immediate_ancestor)
        return dependencies

    def dependency_pair_iter(self, self_first: bool = False) -> tuple:
        """Iterate through the dependencies of this object.

        Args:
            self_first: If true, self comes first in the tuple,
                otherwise the dependency comes first.

        Yields:
            A tuple of a dependency and self. The order is important
            because it determines the direction of graph edge.
        """
        for dependency in self.dependencies:
            if self_first:
                yield self, dependency
            else:
                yield dependency, self

    def __hash__(self):
        """Generate a hash of this object.

        Input values to the hash are the row number and the ODK name.
        This is to ensure that the same fields are used as in the
        __eq__ routine.
        """
        return hash((self.rowx, self.row_name))

    def __eq__(self, other):
        """Test equality between this object and another.

        Equality is done by comparing the row number and the ODK name.
        """
        return self.rowx == other.rowx and self.row_name == other.row_name

    def __lt__(self, other):
        """Compare two XlsFormRows based on row number."""
        return self.rowx < other.rowx

    def __repr__(self):
        """Get a representation of this object."""
        this_repr = f'<XlsFormRow: row {self.rowx}, name "{self.row_name}">'
        return this_repr
