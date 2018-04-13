PYTHON=./env/bin/python3
SRC=./odkgraph


.PHONY: lint

lint:
	${PYTHON} -m pylint --output-format=colorized --reports=n ${SRC}

test:
	${PYTHON} -m unittest discover -v
