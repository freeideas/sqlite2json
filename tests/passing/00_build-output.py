#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

"""
Test for reqs/00_build-output.md

This requirement file explicitly states: "No requirements can be written for this concern."

The README.md and specs/*.md do not document:
- What specific files must exist in `./released/`
- What build strategy must be used
- That `./released/` must be emptied and re-written with each build

Per the minimal viable project philosophy: if it's not specified in requirements,
we don't test it. This test exists only to document that no testable requirements
exist for this concern.
"""

import sys

# Fix Windows console encoding for Unicode characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

def main():
    # No requirements exist for build output.
    # Therefore, there is nothing to test.
    # This test passes by definition.

    # The requirement file explicitly states no requirements can be written,
    # so there are no requirement tags to mark.

    print("✓ Test passes: No requirements to verify (as documented in reqs/00_build-output.md)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
