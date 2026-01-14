# JSON Output Format

Documents the line-oriented JSON output structure for both SQL query mode and full database dump mode.

## $REQ_JSON_001: SQL Mode List Structure
**Source:** ./README.md (Section: "Output")

With `--sql`, output is a JSON list with `[` on its own line, one row per line, and `]` on the last line.

## $REQ_JSON_002: Dump Mode List Structure
**Source:** ./README.md (Section: "Output")

Without `--sql`, output is a JSON list of tables starting with `[` on its own line and ending with `]` on its own line.

## $REQ_JSON_003: Dump Mode Table Entry Attributes
**Source:** ./README.md (Section: "Output")

Each table entry in dump mode has attributes `TABLE_NAME` and `ROWS`.

## $REQ_JSON_004: Dump Mode ROWS Format
**Source:** ./README.md (Section: "Output")

In dump mode, `ROWS` is a list in the same format as `SELECT * FROM [TABLE_NAME]`, including `[` and `]` on their own lines.

## $REQ_JSON_005: Dump Mode Table Object Line Structure
**Source:** ./README.md (Section: "Output")

In dump mode, each table object starts with `{` on its own line and ends with `}` on its own line.

## $REQ_JSON_006: Row Shape
**Source:** ./specs/behavior.md (Section: "Row shape and ordering")

Each row is a JSON object where keys are column names and values are field values.

## $REQ_JSON_007: Row and Column Order
**Source:** ./README.md (Section: "Output")

Row and column order are whatever SQLite returns; the user can control both with `--sql`.

## $REQ_JSON_008: Valid JSON Output
**Source:** ./README.md (Section: "Output")

Both outputs (SQL mode and dump mode) are valid JSON in a line-oriented style similar to NDJSON.

## $REQ_JSON_009: INTEGER and REAL Value Mapping
**Source:** ./specs/behavior.md (Section: "Value mapping")

INTEGER and REAL SQLite types map to JSON numbers.

## $REQ_JSON_010: TEXT Value Mapping
**Source:** ./specs/behavior.md (Section: "Value mapping")

TEXT SQLite type maps to JSON strings.

## $REQ_JSON_011: NULL Value Mapping
**Source:** ./specs/behavior.md (Section: "Value mapping")

NULL SQLite value maps to JSON null.
