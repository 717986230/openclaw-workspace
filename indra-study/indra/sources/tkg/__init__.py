"""
This module implements an input API and processor for the
textToKnowledgeGraph method which uses LLMs to extract BEL statements
from publications:

textToKnowledgeGraph: Generation of Molecular Interaction Knowledge Graphs Using
Large Language Models for Exploration in Cytoscape
Favour James, Christopher Churas, Dexter Pratt, Augustin Luna
bioRxiv https://doi.org/10.1101/2025.07.17.664328
"""

from .api import *
from .processor import TkgProcessor

__all__ = [
    "process_json_file",
    "process_json",
    "process_pmc",
    "TkgProcessor",
]
