# Command-Line Interface

Documents the command-line arguments and options for the sqlite2json tool.

## $REQ_CLI_001: Database File Argument
**Source:** ./README.md (Section: "Usage")

The tool accepts a `--db-file PATH` argument specifying the SQLite database file to read.

## $REQ_CLI_002: Optional SQL Query Argument
**Source:** ./README.md (Section: "Usage")

The tool accepts an optional `--sql "SELECT ..."` argument to execute a specific SQL query.

## $REQ_CLI_003: SQL Mode Output
**Source:** ./README.md (Section: "Output")

When `--sql` is provided, the tool writes a JSON list to stdout with `[` on its own line, one row per line, and `]` on the last line.

## $REQ_CLI_004: Default Mode Output
**Source:** ./README.md (Section: "Output")

When `--sql` is not provided, the tool writes a JSON list of tables to stdout. It starts with `[` on its own line and ends with `]` on its own line. Each table object has attributes `TABLE_NAME` and `ROWS`. `ROWS` uses the same list format as SQL mode. Each table object starts with `{` on its own line and ends with `}` on its own line.

## $REQ_CLI_005: Row and Column Order
**Source:** ./README.md (Section: "Output")

Row and column order in output are whatever SQLite returns.

## $REQ_CLI_006: Row Shape
**Source:** ./README.md (Section: "Output")

Each row is a JSON object where keys are column names and values are field values.

## $REQ_CLI_007: Value Type Mapping
**Source:** ./specs/behavior.md (Section: "Value mapping")

INTEGER and REAL map to JSON numbers. TEXT maps to JSON strings. NULL maps to JSON null.

## $REQ_CLI_008: Help Argument
**Source:** ./specs/behavior.md (Section: "Command-line handling")

The tool accepts a `--help` argument that prints help text to stdout.

## $REQ_CLI_009: Help on No Arguments
**Source:** ./specs/behavior.md (Section: "Command-line handling")

When no command-line arguments are provided, the help text is printed to stdout.

## $REQ_CLI_010: Help on Unrecognized Arguments
**Source:** ./specs/behavior.md (Section: "Command-line handling")

When unrecognized arguments are present, the help text is printed to stdout.

## $REQ_CLI_011: Help on Missing or Invalid Required Arguments
**Source:** ./specs/behavior.md (Section: "Command-line handling")

When required arguments are missing or invalid, the help text is printed to stdout.

## $REQ_CLI_012: Error Message After Help
**Source:** ./specs/behavior.md (Section: "Command-line handling")

If there is an error, the error message is printed AFTER the help text.

## $REQ_CLI_013: Exact Help Text Format
**Source:** ./specs/behavior.md (Section: "Command-line handling")

The help text output must match the content specified in ./specs/HELP.txt.
