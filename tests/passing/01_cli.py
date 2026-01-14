#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

import sys
# Fix Windows console encoding for Unicode characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

import json
import os
import subprocess
import sqlite3
from pathlib import Path

def main():
    # Get project root (tests/failing/01_cli.py -> ../../)
    project_root = Path(__file__).resolve().parent.parent.parent
    exe_path = project_root / "released" / "sqlite2json.exe"
    tmp_dir = project_root / "tmp"

    # Create tmp directory for test database
    tmp_dir.mkdir(exist_ok=True)
    test_db = tmp_dir / "test_cli.db"

    # Clean up any existing test database
    if test_db.exists():
        test_db.unlink()

    # Create a test database with sample data
    conn = sqlite3.connect(str(test_db))
    cursor = conn.cursor()

    # Create test table with various data types
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER,
            name TEXT,
            score REAL,
            active INTEGER,
            notes TEXT
        )
    """)

    cursor.execute("""
        INSERT INTO users (id, name, score, active, notes)
        VALUES (1, 'Alice', 95.5, 1, 'First user')
    """)

    cursor.execute("""
        INSERT INTO users (id, name, score, active, notes)
        VALUES (2, 'Bob', 87.3, 0, NULL)
    """)

    # Create another table for dump mode testing
    cursor.execute("""
        CREATE TABLE products (
            product_id INTEGER,
            product_name TEXT,
            price REAL
        )
    """)

    cursor.execute("""
        INSERT INTO products (product_id, product_name, price)
        VALUES (100, 'Widget', 19.99)
    """)

    conn.commit()
    conn.close()

    # $REQ_CLI_001: Database File Argument
    # Test that --db-file argument is accepted
    result = subprocess.run(
        [str(exe_path), "--db-file", str(test_db), "--sql", "SELECT 1"],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    assert result.returncode == 0, f"Tool should accept --db-file argument, got exit code {result.returncode}"

    # $REQ_CLI_002: Optional SQL Query Argument
    # Test SQL mode with --sql argument
    result = subprocess.run(
        [str(exe_path), "--db-file", str(test_db), "--sql", "SELECT id, name FROM users WHERE id = 1"],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    assert result.returncode == 0, f"Tool should accept --sql argument, got exit code {result.returncode}"

    # $REQ_CLI_003: SQL Mode Output
    # Verify SQL mode output format: [ on its own line, rows, ] on last line
    lines = result.stdout.strip().split('\n')
    assert lines[0] == "[", "SQL mode output should start with [ on its own line"
    assert lines[-1] == "]", "SQL mode output should end with ] on its own line"

    # $REQ_CLI_006: Row Shape
    # Each row should be a JSON object with column names as keys
    row_json = json.loads(lines[1])
    assert isinstance(row_json, dict), "Each row should be a JSON object"
    assert "id" in row_json, "Row should have 'id' column"
    assert "name" in row_json, "Row should have 'name' column"

    # $REQ_CLI_007: Value Type Mapping
    # INTEGER maps to JSON number
    assert isinstance(row_json["id"], int), "INTEGER should map to JSON number"
    assert row_json["id"] == 1, "INTEGER value should be correct"

    # TEXT maps to JSON string
    assert isinstance(row_json["name"], str), "TEXT should map to JSON string"
    assert row_json["name"] == "Alice", "TEXT value should be correct"

    # Test REAL and NULL mapping
    result = subprocess.run(
        [str(exe_path), "--db-file", str(test_db), "--sql", "SELECT score, notes FROM users WHERE id = 2"],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    lines = result.stdout.strip().split('\n')
    row_json = json.loads(lines[1])

    # REAL maps to JSON number
    assert isinstance(row_json["score"], float), "REAL should map to JSON number"
    assert abs(row_json["score"] - 87.3) < 0.01, "REAL value should be correct"

    # NULL maps to JSON null
    assert row_json["notes"] is None, "NULL should map to JSON null"

    # $REQ_CLI_004: Default Mode Output
    # Test default mode (no --sql argument)
    result = subprocess.run(
        [str(exe_path), "--db-file", str(test_db)],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    assert result.returncode == 0, f"Default mode should work, got exit code {result.returncode}"

    lines = result.stdout.strip().split('\n')
    # $REQ_CLI_004: It starts with [ on its own line and ends with ] on its own line
    assert lines[0] == "[", "Default mode output should start with [ on its own line"
    assert lines[-1] == "]", "Default mode output should end with ] on its own line"

    # Verify TABLE_NAME and ROWS attributes are present
    output = result.stdout
    assert "TABLE_NAME" in output, "Default mode should include TABLE_NAME attribute"
    assert "ROWS" in output, "Default mode should include ROWS attribute"

    # $REQ_CLI_004: Each table object has attributes TABLE_NAME and ROWS
    # ROWS uses the same list format as SQL mode
    assert "[" in output, "ROWS should use list format with ["
    assert "]" in output, "ROWS should use list format with ]"

    # Verify formatting: Each table object starts with { on its own line and ends with } on its own line
    has_table_object_open = False
    has_table_object_close = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Skip the root level [ and ]
        if i == 0 or i == len(lines) - 1:
            continue
        # Look for table object boundaries
        if stripped == "{":
            has_table_object_open = True
        if stripped == "}":
            has_table_object_close = True

    assert has_table_object_open, "Each table object should start with { on its own line"
    assert has_table_object_close, "Each table object should end with } on its own line"

    # $REQ_CLI_005: Row and Column Order
    # Not reasonably testable: Row and column order are determined by SQLite

    # Read expected help text
    specs_dir = project_root / "specs"
    help_file = specs_dir / "HELP.txt"
    with open(help_file, 'r', encoding='utf-8') as f:
        expected_help = f.read()

    # $REQ_CLI_008: Help Argument
    result = subprocess.run(
        [str(exe_path), "--help"],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    assert result.returncode == 0, "Tool should exit with 0 when --help is provided"
    # $REQ_CLI_013: Exact Help Text Format
    assert result.stdout == expected_help, "Help text should match HELP.txt exactly"

    # $REQ_CLI_009: Help on No Arguments
    result = subprocess.run(
        [str(exe_path)],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    assert result.returncode == 0, "Tool should exit with 0 when no arguments provided"
    # $REQ_CLI_013: Exact Help Text Format
    assert result.stdout == expected_help, "Help text should match HELP.txt exactly when no args"

    # $REQ_CLI_010: Help on Unrecognized Arguments
    result = subprocess.run(
        [str(exe_path), "--invalid-arg"],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    assert result.returncode != 0, "Tool should exit with non-zero when unrecognized arguments present"
    # $REQ_CLI_012: Error Message After Help
    assert result.stdout == expected_help, "Help text should be printed first"
    assert result.stderr != "", "Error message should be printed to stderr"
    assert "Error:" in result.stderr or "error" in result.stderr.lower(), "Error message should be printed"

    # $REQ_CLI_011: Help on Missing or Invalid Required Arguments
    result = subprocess.run(
        [str(exe_path), "--sql", "SELECT 1"],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    assert result.returncode != 0, "Tool should exit with non-zero when required --db-file is missing"
    # $REQ_CLI_012: Error Message After Help
    assert result.stdout == expected_help, "Help text should be printed first when args missing"
    assert result.stderr != "", "Error message should be printed to stderr when args missing"

    # Test invalid value for --db-file (missing value)
    result = subprocess.run(
        [str(exe_path), "--db-file"],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    assert result.returncode != 0, "Tool should exit with non-zero when --db-file has no value"
    # $REQ_CLI_012: Error Message After Help
    assert result.stdout == expected_help, "Help text should be printed when argument value missing"
    assert result.stderr != "", "Error message should be printed when argument value missing"

    print("All tests passed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
