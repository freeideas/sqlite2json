# sqlite2json

Simple Rust command-line tool that reads a SQLite database and writes JSON to stdout.

## Usage

```
sqlite2json --db-file PATH [--sql "SELECT ..."]
```

Use `--help` to see usage information. Help is also shown for any command-line errors.

## Output

- With `--sql`: writes a JSON list, with `[` on its own line, one row per line, and `]` on the last line.
- Without `--sql`: writes a JSON list of tables. It starts with `[` on its own line and ends with `]` on its own line. Each table object has attributes `TABLE_NAME` and `ROWS`. `ROWS` is the same list format as `SELECT * FROM [TABLE_NAME]`, including `[` and `]` on their own lines. Each table object starts with `{` on its own line and ends with `}` on its own line.

Each row is a JSON object with keys as column names and values as the field values. Row and column order are whatever SQLite returns; you can control both with `--sql`.

Both outputs are valid JSON in a line-oriented style similar to NDJSON.
