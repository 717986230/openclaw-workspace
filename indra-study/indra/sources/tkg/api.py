__all__ = ["process_json_file", "process_json", "process_pmc"]
"""
This module implements an API for the textToKnowledgeGraph
method which extracts BEL statements from publications via an LLM.

This module provides two integration modes:

Offline processing
    In this mode, a JSON file output from textToKnowledgeGraph
    is used as the starting point from which INDRA Statements are produced.

Live processing
    If the `texttoknowledgegraph` package is installed, calls
    the LLM extraction pipeline, processes the returned BEL relations
    and produces INDRA Statements.

Both modes produce an TkgProcessor instance containing INDRA
Statements derived from BEL expressions.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Union

from indra import get_config
from .processor import TkgProcessor

logger = logging.getLogger(__name__)



def process_json_file(path: Union[str, Path]):
    """Process a single textToKnowledgeGraph JSON results file.

    Parameters
    ----------
    path : str or Path
        Path to a JSON file containing BEL relations.

    Returns
    -------
    TkgProcessor
        Processor containing the converted INDRA Statements.
    """
    path = Path(path)
    logger.debug("Processing LLM-BEL results file: %s", path)

    with open(path, "r") as fh:
        data = json.load(fh)

    return process_json(data)


def process_json(data: Dict):
    """Process BEL relations returned directly from the LLM engine.

    Parameters
    ----------
    data : dict
        Dictionary containing at least a ``"relations"`` field.

    Returns
    -------
    TkgProcessor
        Processor with INDRA Statements derived from BEL.
    """
    processor = TkgProcessor(data)
    processor.extract_statements()
    return processor


def process_pmc(pmc_id: str, output_base_path, **kwargs):
    """Run live BEL extraction using textToKnowledgeGraph, if installed.

    Parameters
    ----------
    pmc_id : str
        PMCID such as 'PMC3898398'.
    kwargs :
        Additional keyword arguments passed to textToKnowledgeGraph.main().

    Returns
    -------
    TkgProcessor
        Processor containing INDRA Statements derived from live BEL output.

    Raises
    ------
    ImportError
        If textToKnowledgeGraph is not installed.
    ValueError
        If the returned data structure is unexpected.
    """
    try:
        from textToKnowledgeGraph import main as tkg_main
    except ImportError:
        raise ImportError(
            "The 'textToKnowledgeGraph' package is not installed. "
            "Install it or run textToKnowledgeGraph separately to "
            "produce output files and then use one of the functions like "
            "process_json_file to process the outputs."
        )

    api_key = get_config('OPENAI_API_KEY', failure_ok=False)

    logger.debug("Running live textToKnowledgeGraph extraction for %s", pmc_id)

    success = tkg_main(
        api_key=api_key,
        pmc_ids=[pmc_id],
        upload_to_ndex=False,
        # Note: this assumes https://github.com/ndexbio/llm-text-to-knowledge-graph/pull/27
        # will be merged
        output_base_path=output_base_path,
        **kwargs,
    )

    if success:
        # TKG doesn't explicitly say where the results will be put so we need to
        # construct this path ourselves
        output_path = os.path.join(output_base_path, 'results', pmc_id,
                                   'llm_results.json')

        return process_json_file(output_path)
    return None
