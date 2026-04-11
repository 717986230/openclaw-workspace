__all__ = ["TkgProcessor"]

import re
import logging
from typing import Dict, List

from indra.sources.bel import process_bel_stmt

logger = logging.getLogger(__name__)


class TkgProcessor:
    """Processor extracting INDRA Statments from textToKnowledgeGraph output.

    After parsing BEL to INDRA Statements via PyBEL, this processor attaches
    metadata (confidence, text, pmid, pmcid, etc.) to Evidence objects.

    Parameters
    ----------
    results : Dict
        Output data structure of textToKnowledgeGraph to be processed

    Attributes
    ----------
    statements : List[indra.statements.Statement]
        A list of INDRA Statements extracted from the results.
    """

    def __init__(self, results):
        self.results = results
        self.statements = []
        self.skipped = []

    # Alternative processing mode (not used by V1 tests but available)
    def extract_statements(self):
        """Run BEL to INDRA pipeline for all entries in llm_results."""
        extractions = self.results.get('LLM_extractions', [])
        for extraction in extractions:
            results = extraction.get('Results', [])
            for entry in results:
                raw_bel_stmt = entry['bel_statement']
                bel_stmt = normalize_bel(raw_bel_stmt)
                try:
                    pp = process_bel_stmt(bel_stmt)
                except Exception as e:
                    self.skipped.append(bel_stmt)
                    continue
                if pp and pp.statements:
                    self.statements += pp.statements
                else:
                    self.skipped.append(bel_stmt)

        logger.debug(
            "textToKnowledgeGraph processor finished: extracted=%d "
            "skipped=%d total=%d", len(self.statements), len(self.skipped),
            len(self.results)
        )


# Fix GO Biological Process names that contain spaces
GO_BP_PATTERN = re.compile(r'GO:([A-Za-z0-9\-\s]+)')


def normalize_go_terms(bel: str) -> str:
    """Normalize GO terms like:
        GO:DNA-templated transcription
    into:
        GO:"DNA-templated transcription"
    so PyBEL can parse them.
    """
    def replacer(match):
        content = match.group(1)
        # If already quoted or no spaces in string, we can return as is
        if '"' in content or "'" in content or ' ' not in content:
            return f'GO:{content}'
        return f'GO:"{content}"'

    return GO_BP_PATTERN.sub(replacer, bel)


def normalize_bel(bel: str) -> str:
    """Apply all normalization steps."""
    # For now just normalizing GO terms which appears to be an existing issue.
    # Can be extended with other processing steps later.
    bel = normalize_go_terms(bel)
    return bel
