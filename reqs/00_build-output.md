# Build Requirements

Requires the contents of the `./released/` directory to contain the specified files and only the specified files. Requiries (presumably by code inspection of ./code/build.py) that the correct build strategy is used (e.g. ".NET AOT STAND-ALONE" or "Rust" or "Flutter"), and that the ./released/ directory is emptied and re-written with each build.

## Analysis

**No requirements can be written for this concern.**

The README.md and specs/*.md do not document:
- What specific files must exist in `./released/`
- What build strategy must be used
- That `./released/` must be emptied and re-written with each build

The README.md describes the tool as "Simple Rust command-line tool" but this is descriptive context, not a build artifact specification. The usage example shows `sqlite2json` as the command name, but does not specify what files must be produced or where they must be placed.

Per the requirements writing rules:
- Build scripts or build processes are explicitly excluded from requirements
- Only behaviors anchored in README.md or specs/*.md are valid sources
- ./docs/ cannot be used as a source
