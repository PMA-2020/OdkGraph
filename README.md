![ODK graph](static/odk-graph.png)

# Description

Analyze your XlsForms as directed graphs. The nodes of the graph are the 
individual XlsForm questions (rows in an XlsForm). The edges are dependencies 
on other questions.

If question B depends on question A being answered a specific way, then an edge
points from A to B.

# Installation

All dependencies are on PyPI. To install, a single `pip` call on the command 
line suffices:

```
python3 -m pip install https://github.com/jkpr/OdkGraph/zipball/master
```

# Usage

:white_check_mark: _First, make sure the ODK Xlsform converts cleanly to XML._ 

Import the `OdkGraph` class with

```python
from odkgraph import OdkGraph
```

Next, create an `OdkGraph` object. The `__init__` method accepts a path to the 
file:

```python
odk_graph = OdkGraph('/path/to/odk/xlsform.xlsx')
```

Some useful things this code does now that we have an `OdkGraph` object:

```python
odk_graph.size()                    # The number of edges (dependencies)
odk_graph.order()                   # The number of nodes (survey elements)
odk_graph.forward_dependencies()    # The ODK elements that depend on things that are defined after them in the Xlsform
odk_graph.terminal_nodes()          # The ODK elements that depend on other elements, but nothing depends on them
odk_graph.isolates()                # The ODK elements that depend on nothing else, and nothing depends on them
```

The underlying `networkx` network ([documentation here](https://networkx.github.io/documentation/stable/index.html)) can be accessed with

```python
odk_graph.network
```


See all methods and attributes on `OdkGraph` and their docstrings with

```python
help(OdkGraph)
```
or by reading the [source code](https://github.com/jkpr/OdkGraph/blob/master/odkgraph/odkgraph.py).

# Bugs

Submit bug reports to James K. Pringle at jpringleBEAR@jhu.edu minus the bear.
