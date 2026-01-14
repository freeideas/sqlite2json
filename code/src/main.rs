use rusqlite::{Connection, Result, Row};
use serde_json::{json, Map, Value};
use std::env;
use std::process;

// $REQ_CLI_013: Exact Help Text Format
const HELP_TEXT: &str = "sqlite2json - Read a SQLite database and write JSON to stdout

USAGE:
    sqlite2json --db-file <PATH> [--sql <QUERY>]

OPTIONS:
    --db-file <PATH>    Path to the SQLite database file (required)
    --sql <QUERY>       SQL SELECT query to execute
    --help              Print this help message

OUTPUT:
    With --sql:     JSON list with one row object per line
    Without --sql:  JSON object tree with all tables
";

// $REQ_CLI_001: Database File Argument
// $REQ_CLI_002: Optional SQL Query Argument
struct Args {
    db_file: String,
    sql: Option<String>,
}

enum ParseResult {
    Args(Args),
    Help,
    Error(String),
}

// $REQ_CLI_008: Help Argument
// $REQ_CLI_009: Help on No Arguments
// $REQ_CLI_010: Help on Unrecognized Arguments
// $REQ_CLI_011: Help on Missing or Invalid Required Arguments
fn parse_args() -> ParseResult {
    let args: Vec<String> = env::args().collect();

    // $REQ_CLI_009: Help on No Arguments
    if args.len() == 1 {
        return ParseResult::Help;
    }

    // $REQ_CLI_008: Help Argument
    if args.iter().any(|arg| arg == "--help") {
        return ParseResult::Help;
    }

    let mut db_file = None;
    let mut sql = None;

    let mut i = 1;
    while i < args.len() {
        match args[i].as_str() {
            "--db-file" => {
                if i + 1 < args.len() {
                    db_file = Some(args[i + 1].clone());
                    i += 2;
                } else {
                    // $REQ_CLI_011: Help on Missing or Invalid Required Arguments
                    return ParseResult::Error("Missing value for --db-file".to_string());
                }
            }
            "--sql" => {
                if i + 1 < args.len() {
                    sql = Some(args[i + 1].clone());
                    i += 2;
                } else {
                    // $REQ_CLI_011: Help on Missing or Invalid Required Arguments
                    return ParseResult::Error("Missing value for --sql".to_string());
                }
            }
            _ => {
                // $REQ_CLI_010: Help on Unrecognized Arguments
                return ParseResult::Error(format!("Unrecognized argument: {}", args[i]));
            }
        }
    }

    // $REQ_CLI_011: Help on Missing or Invalid Required Arguments
    if db_file.is_none() {
        return ParseResult::Error("Missing required argument: --db-file".to_string());
    }

    ParseResult::Args(Args {
        db_file: db_file.unwrap(),
        sql,
    })
}

// $REQ_CLI_006: Row Shape
// $REQ_CLI_007: Value Type Mapping
// $REQ_JSON_006: Row Shape
// $REQ_INTEGER_TO_NUMBER: SQLite INTEGER maps to JSON number
// $REQ_REAL_TO_NUMBER: SQLite REAL maps to JSON number
// $REQ_TEXT_TO_STRING: SQLite TEXT maps to JSON string
// $REQ_NULL_TO_NULL: SQLite NULL maps to JSON null
// $REQ_JSON_009: INTEGER and REAL Value Mapping
// $REQ_JSON_010: TEXT Value Mapping
// $REQ_JSON_011: NULL Value Mapping
fn row_to_json(row: &Row) -> Result<Value> {
    let mut map = Map::new();
    let column_count = row.as_ref().column_count();

    for i in 0..column_count {
        let column_name = row.as_ref().column_name(i)?.to_string();
        let value = match row.get_ref(i)? {
            rusqlite::types::ValueRef::Null => Value::Null,  // $REQ_NULL_TO_NULL, $REQ_JSON_011
            rusqlite::types::ValueRef::Integer(n) => json!(n),  // $REQ_INTEGER_TO_NUMBER, $REQ_JSON_009
            rusqlite::types::ValueRef::Real(f) => json!(f),  // $REQ_REAL_TO_NUMBER, $REQ_JSON_009
            rusqlite::types::ValueRef::Text(s) => {  // $REQ_TEXT_TO_STRING, $REQ_JSON_010
                json!(String::from_utf8_lossy(s))
            }
            rusqlite::types::ValueRef::Blob(_) => Value::Null,
        };
        map.insert(column_name, value);
    }

    Ok(Value::Object(map))
}

// $REQ_CLI_003: SQL Mode Output
// $REQ_CLI_005: Row and Column Order
// $REQ_JSON_001: SQL Mode List Structure
// $REQ_JSON_007: Row and Column Order
// $REQ_JSON_008: Valid JSON Output
fn output_sql_mode(conn: &Connection, query: &str) -> Result<()> {
    // $REQ_JSON_001: `[` on its own line
    println!("[");

    let mut stmt = conn.prepare(query)?;
    let mut rows = stmt.query([])?;

    let mut json_rows = Vec::new();
    // $REQ_CLI_005, $REQ_JSON_007: Row and column order are whatever SQLite returns
    while let Some(row) = rows.next()? {
        json_rows.push(row_to_json(row)?);
    }

    // $REQ_JSON_001: one row per line
    for (i, json_row) in json_rows.iter().enumerate() {
        let json_str = serde_json::to_string(json_row).unwrap();
        if i < json_rows.len() - 1 {
            println!("{},", json_str);
        } else {
            println!("{}", json_str);
        }
    }

    // $REQ_JSON_001: `]` on the last line
    println!("]");

    Ok(())
}

// $REQ_CLI_004: Default Mode Output
// $REQ_JSON_002: Dump Mode List Structure
// $REQ_JSON_003: Dump Mode Table Entry Attributes
// $REQ_JSON_004: Dump Mode ROWS Format
// $REQ_JSON_005: Dump Mode Table Object Line Structure
// $REQ_JSON_008: Valid JSON Output
fn output_dump_mode(conn: &Connection) -> Result<()> {
    let mut stmt = conn.prepare(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    )?;
    let table_names: Vec<String> = stmt
        .query_map([], |row| row.get(0))?
        .collect::<Result<Vec<String>>>()?;

    // $REQ_JSON_002: `[` on its own line
    println!("[");

    for (table_idx, table_name) in table_names.iter().enumerate() {
        // $REQ_JSON_005: Each table object starts with `{` on its own line
        println!("{{");

        // $REQ_JSON_003: TABLE_NAME attribute
        println!("\"TABLE_NAME\":\"{}\",", table_name);

        // $REQ_JSON_003: ROWS attribute
        println!("\"ROWS\":");

        // $REQ_JSON_004: ROWS is a list with `[` and `]` on their own lines
        println!("[");

        let query = format!("SELECT * FROM \"{}\"", table_name);
        let mut stmt = conn.prepare(&query)?;
        let mut rows = stmt.query([])?;

        let mut json_rows = Vec::new();
        while let Some(row) = rows.next()? {
            json_rows.push(row_to_json(row)?);
        }

        // One row per line with commas
        for (i, json_row) in json_rows.iter().enumerate() {
            let json_str = serde_json::to_string(json_row).unwrap();
            if i < json_rows.len() - 1 {
                println!("{},", json_str);
            } else {
                println!("{}", json_str);
            }
        }

        // $REQ_JSON_004: `]` on its own line
        println!("]");

        // $REQ_JSON_005: Each table object ends with `}` on its own line
        if table_idx < table_names.len() - 1 {
            println!("}},");
        } else {
            println!("}}");
        }
    }

    // $REQ_JSON_002: `]` on its own line
    println!("]");

    Ok(())
}

fn main() {
    // $REQ_CLI_008-013: Parse arguments and handle help/errors
    let args = match parse_args() {
        ParseResult::Args(a) => a,
        ParseResult::Help => {
            // $REQ_CLI_008, $REQ_CLI_009: Print help text
            print!("{}", HELP_TEXT);
            process::exit(0);
        }
        ParseResult::Error(err) => {
            // $REQ_CLI_010, $REQ_CLI_011, $REQ_CLI_012: Print help then error
            print!("{}", HELP_TEXT);
            eprintln!("Error: {}", err);
            process::exit(1);
        }
    };

    let conn = match Connection::open(&args.db_file) {
        Ok(c) => c,
        Err(e) => {
            // $REQ_CLI_012: Error after help
            print!("{}", HELP_TEXT);
            eprintln!("Error: {}", e);
            process::exit(1);
        }
    };

    let result = match args.sql {
        Some(query) => output_sql_mode(&conn, &query),  // $REQ_CLI_003
        None => output_dump_mode(&conn),  // $REQ_CLI_004
    };

    if let Err(e) = result {
        // $REQ_CLI_012: Error after help
        print!("{}", HELP_TEXT);
        eprintln!("Error: {}", e);
        process::exit(1);
    }
}
