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

import os
import json
import sqlite3
import subprocess
from pathlib import Path

def main():
    # Determine paths
    project_root = Path(__file__).resolve().parent.parent.parent
    exe_name = "sqlite2json.exe" if os.name == 'nt' else "sqlite2json"
    exe_path = project_root / "released" / exe_name
    tmp_dir = project_root / "tmp"

    # Ensure tmp directory exists
    tmp_dir.mkdir(parents=True, exist_ok=True)

    # Create test database
    db_path = tmp_dir / "test_value_mapping.db"

    # Remove old test database if it exists
    if db_path.exists():
        db_path.unlink()

    # Create database with various data types
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Create table with different column types
    cursor.execute("""
        CREATE TABLE test_values (
            id INTEGER,
            price REAL,
            name TEXT,
            description TEXT,
            nullable_field INTEGER
        )
    """)

    # Insert test data covering all type mappings
    cursor.execute("""
        INSERT INTO test_values (id, price, name, description, nullable_field)
        VALUES (42, 99.99, 'Product A', 'A sample product', NULL)
    """)

    cursor.execute("""
        INSERT INTO test_values (id, price, name, description, nullable_field)
        VALUES (100, 0.5, 'Product B', 'Another product', 1)
    """)

    conn.commit()
    conn.close()

    # Run sqlite2json with SQL query to get the data
    result = subprocess.run(
        [str(exe_path), "--db-file", str(db_path), "--sql", "SELECT * FROM test_values"],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )

    if result.returncode != 0:
        print(f"Error running sqlite2json: {result.stderr}")
        return 1

    # Parse output
    lines = result.stdout.strip().split('\n')

    # First line should be [
    assert lines[0] == '[', f"Expected '[' but got: {lines[0]}"

    # Last line should be ]
    assert lines[-1] == ']', f"Expected ']' but got: {lines[-1]}"

    # Parse JSON objects (lines between [ and ])
    json_lines = lines[1:-1]

    assert len(json_lines) == 2, f"Expected 2 rows but got {len(json_lines)}"

    # Parse first row (remove trailing comma if present)
    row1 = json.loads(json_lines[0].rstrip(','))

    # $REQ_INTEGER_TO_NUMBER: SQLite INTEGER maps to JSON number
    assert isinstance(row1['id'], int), f"Expected integer for 'id' but got {type(row1['id'])}"
    assert row1['id'] == 42  # $REQ_INTEGER_TO_NUMBER

    # $REQ_REAL_TO_NUMBER: SQLite REAL maps to JSON number
    assert isinstance(row1['price'], (int, float)), f"Expected number for 'price' but got {type(row1['price'])}"
    assert abs(row1['price'] - 99.99) < 0.001  # $REQ_REAL_TO_NUMBER

    # $REQ_TEXT_TO_STRING: SQLite TEXT maps to JSON string
    assert isinstance(row1['name'], str), f"Expected string for 'name' but got {type(row1['name'])}"
    assert row1['name'] == 'Product A'  # $REQ_TEXT_TO_STRING

    assert isinstance(row1['description'], str), f"Expected string for 'description' but got {type(row1['description'])}"
    assert row1['description'] == 'A sample product'  # $REQ_TEXT_TO_STRING

    # $REQ_NULL_TO_NULL: SQLite NULL maps to JSON null
    assert row1['nullable_field'] is None, f"Expected null for 'nullable_field' but got {row1['nullable_field']}"  # $REQ_NULL_TO_NULL

    # Parse second row (remove trailing comma if present)
    row2 = json.loads(json_lines[1].rstrip(','))

    # Verify second row has correct types too
    assert isinstance(row2['id'], int)  # $REQ_INTEGER_TO_NUMBER
    assert row2['id'] == 100

    assert isinstance(row2['price'], (int, float))  # $REQ_REAL_TO_NUMBER
    assert abs(row2['price'] - 0.5) < 0.001

    assert isinstance(row2['name'], str)  # $REQ_TEXT_TO_STRING
    assert row2['name'] == 'Product B'

    assert isinstance(row2['description'], str)  # $REQ_TEXT_TO_STRING
    assert row2['description'] == 'Another product'

    # This one has a non-null integer
    assert isinstance(row2['nullable_field'], int)  # $REQ_INTEGER_TO_NUMBER
    assert row2['nullable_field'] == 1

    print("All value mapping tests passed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
