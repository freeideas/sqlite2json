# Value Mapping

Documents how SQLite data types are converted to JSON types.

## $REQ_INTEGER_TO_NUMBER: SQLite INTEGER maps to JSON number
**Source:** ./specs/behavior.md (Section: "Value mapping")

SQLite INTEGER values are converted to JSON numbers.

## $REQ_REAL_TO_NUMBER: SQLite REAL maps to JSON number
**Source:** ./specs/behavior.md (Section: "Value mapping")

SQLite REAL values are converted to JSON numbers.

## $REQ_TEXT_TO_STRING: SQLite TEXT maps to JSON string
**Source:** ./specs/behavior.md (Section: "Value mapping")

SQLite TEXT values are converted to JSON strings.

## $REQ_NULL_TO_NULL: SQLite NULL maps to JSON null
**Source:** ./specs/behavior.md (Section: "Value mapping")

SQLite NULL values are converted to JSON null.
