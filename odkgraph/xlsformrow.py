"""This module creates and analyzes XlsForm rows.

A row represents a single question or calculate, or in other words, a
data collection unit.

Module attributes:
    ODK_VAR_REGEX: A regex string to parse ODK variable references
    ODK_VAR_REGEX_PROG: A compiled regex based on ODK_VAR_REGEX
    XlsFormRow: A class for representing an XlsForm row
"""
import re


ODK_VAR_REGEX = r'\$\{(.*?)\}'
ODK_VAR_REGEX_PROG = re.compile(ODK_VAR_REGEX)


class XlsFormRow:
    """Class to hold information associated with a row in an XlsForm.

    The instance attributes `dependency_names` and `dependencies` are
    calculated. The `dependency_names` is a list of alphabetically
    sorted names discovered through parsing the fields of this row. The
    `dependencies` are the XlsFormRows, sorted according to the rowx
    attribute.

    Instance attributes:
        rowx: The 0-indexed row in the survey tab where this row is
        row_type: The value in the 'type' column
        row_name: The value in the 'name' column
        row_dict: The survey tab header is the keys, the row entries
            are the values
        ancestors: The names of the groups and repeats that this entry
            is nested under, in order
        dependency_names: The row_names of this row's dependencies
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

        self.dependency_names = self.parse_dependencies()
        self.dependencies = []

    def parse_dependencies(self) -> list:
        """Parse out dependency names from the fields of this row.

        Returns:
            A list of the unique dependency names. It is sorted
            alphabetically.
        """
        dependencies = set()
        for value in self.row_dict.values():
            found = ODK_VAR_REGEX_PROG.findall(value)
            dependencies |= set(found)
        if self.ancestors:
            dependencies.add(self.ancestors[-1])
        sorted_list = sorted(list(dependencies))
        return sorted_list

    def dependency_pair_iter(self, self_first: bool = False):
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
