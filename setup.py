from setuptools import setup, find_packages

from odkgraph import __version__


packages = find_packages()


setup(
    name='odkgraph',
    version=__version__,
    author='James K. Pringle',
    author_email='jpringle@jhu.edu',
    url='http://www.pma2020.org',
    packages=packages,
    license='LICENSE.txt',
    description='Convert an XlsForm into a directed graph and analyze it',
    long_description=open('README.md').read(),
    install_requires=[
        'xlrd>=1.1.0',
        'networkx>=2.1'
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)
