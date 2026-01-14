# sqlite2json minimal behavior

This spec is intentionally minimal; implement only what is described here and in `README.md`.

## Command-line handling

The help text (see `HELP.txt`) is printed to stdout in these cases:

- `--help` is present on the command-line
- No command-line arguments are provided
- Unrecognized arguments are present
- Required arguments are missing or invalid

If there is an error, the error message is printed AFTER the help text.

## Row shape and ordering

- Each row is a JSON object where keys are column names and values are field values.
- Row order and column order follow whatever SQLite returns.
- The user can control both with `--sql`.

## Value mapping

- INTEGER and REAL map to JSON numbers.
- TEXT maps to JSON strings.
- NULL maps to JSON null.
- Other SQLite types are unspecified.

## Example: `--sql` mode

Given a SQLite database `example.db` with:

```
CREATE TABLE people (id INTEGER, name TEXT);
INSERT INTO people (id, name) VALUES (1, 'Ada'), (2, 'Linus');
```

Command:

```
sqlite2json --db-file example.db --sql "SELECT id, name FROM people"
```

Expected output (line-oriented JSON list):

```
[
{"id":1,"name":"Ada"}
{"id":2,"name":"Linus"}
]
```

## Example: no `--sql` mode

Using the same database as above, command:

```
sqlite2json --db-file example.db
```

Expected output (line-oriented JSON list of tables):

```
[
{
"TABLE_NAME":"people"
"ROWS":
[
{"id":1,"name":"Ada"}
{"id":2,"name":"Linus"}
]
}
]
```
