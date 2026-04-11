#!/usr/bin/env python3
"""Run GBrain integration test."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Run the complete test
if __name__ == "__main__":
    from integrate_to_erbing import run_complete_integration_test
    run_complete_integration_test()
