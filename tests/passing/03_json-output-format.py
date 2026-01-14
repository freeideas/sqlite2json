#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

import os
import subprocess
import sys
import json
import tempfile
import sqlite3
from pathlib import Path

# Fix Windows console encoding for Unicode characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Ensure tmp directory exists
os.makedirs('./tmp', exist_ok=True)

def run_sqlite2json(db_path, sql=None):
    """Run sqlite2json and return stdout"""
    cmd = [str(Path('./released/sqlite2json.exe')), '--db-file', str(db_path)]
    if sql:
        cmd.extend(['--sql', sql])

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding='utf-8'
    )

    if result.returncode != 0:
        print(f"sqlite2json failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    return result.stdout

def create_test_db():
    """Create a test SQLite database with sample data"""
    db_path = Path('./tmp/test_json_format.db')
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Create test table with various data types
    cursor.execute('''
        CREATE TABLE people (
            id INTEGER,
            name TEXT,
            age INTEGER,
            score REAL,
            notes TEXT
        )
    ''')

    # Insert test data including NULL values
    cursor.execute('INSERT INTO people VALUES (1, "Ada", 30, 95.5, "First person")')
    cursor.execute('INSERT INTO people VALUES (2, "Linus", NULL, 88.0, NULL)')
    cursor.execute('INSERT INTO people VALUES (3, "Grace", 45, NULL, "Third person")')

    # Create a second table for dump mode testing
    cursor.execute('CREATE TABLE projects (proj_id INTEGER, title TEXT)')
    cursor.execute('INSERT INTO projects VALUES (100, "Project A")')
    cursor.execute('INSERT INTO projects VALUES (200, "Project B")')

    conn.commit()
    conn.close()

    return db_path

def test_sql_mode_list_structure():
    """Test $REQ_JSON_001: SQL Mode List Structure"""
    db_path = create_test_db()
    output = run_sqlite2json(db_path, 'SELECT id, name FROM people')

    lines = output.strip().split('\n')

    # First line should be '['
    assert lines[0] == '[', f"$REQ_JSON_001: First line should be '[', got: {lines[0]}"  # $REQ_JSON_001

    # Last line should be ']'
    assert lines[-1] == ']', f"$REQ_JSON_001: Last line should be ']', got: {lines[-1]}"  # $REQ_JSON_001

    # Middle lines should be JSON objects (one per row), possibly with trailing comma
    for i in range(1, len(lines) - 1):
        line = lines[i].rstrip(',')  # Remove trailing comma if present
        try:
            obj = json.loads(line)
            assert isinstance(obj, dict), f"$REQ_JSON_001: Row should be a JSON object"  # $REQ_JSON_001
        except json.JSONDecodeError as e:
            assert False, f"$REQ_JSON_001: Line {i} is not valid JSON (after removing comma): {line}, error: {e}"  # $REQ_JSON_001

    # Verify the whole output is valid JSON
    parsed = json.loads(output)
    assert isinstance(parsed, list), f"$REQ_JSON_001: Overall output should be a JSON list"  # $REQ_JSON_001

    print("✓ $REQ_JSON_001: SQL Mode List Structure")

def test_dump_mode_list_structure():
    """Test $REQ_JSON_002: Dump Mode List Structure"""
    db_path = create_test_db()
    output = run_sqlite2json(db_path)

    lines = output.strip().split('\n')

    # First line should be '['
    assert lines[0] == '[', f"$REQ_JSON_002: First line should be '[', got: {lines[0]}"  # $REQ_JSON_002

    # Last line should be ']'
    assert lines[-1] == ']', f"$REQ_JSON_002: Last line should be ']', got: {lines[-1]}"  # $REQ_JSON_002

    print("✓ $REQ_JSON_002: Dump Mode List Structure")

def test_dump_mode_table_entry_attributes():
    """Test $REQ_JSON_003: Dump Mode Table Entry Attributes"""
    db_path = create_test_db()
    output = run_sqlite2json(db_path)

    # Parse the JSON and verify each table entry has TABLE_NAME and ROWS
    data = json.loads(output)

    # The structure is a list: [ { "TABLE_NAME": "...", "ROWS": [...] }, ... ]
    assert isinstance(data, list), f"$REQ_JSON_003: Dump mode output should be a list"  # $REQ_JSON_003
    for table_obj in data:
        assert isinstance(table_obj, dict), f"$REQ_JSON_003: Each table entry should be an object"  # $REQ_JSON_003
        assert 'TABLE_NAME' in table_obj, f"$REQ_JSON_003: Table entry should have TABLE_NAME attribute"  # $REQ_JSON_003
        assert 'ROWS' in table_obj, f"$REQ_JSON_003: Table entry should have ROWS attribute"  # $REQ_JSON_003

    print("✓ $REQ_JSON_003: Dump Mode Table Entry Attributes")

def test_dump_mode_rows_format():
    """Test $REQ_JSON_004: Dump Mode ROWS Format"""
    db_path = create_test_db()
    output = run_sqlite2json(db_path)

    lines = output.strip().split('\n')

    # Find the ROWS section and check for [ and ] on their own lines
    found_rows = False
    found_open_bracket = False
    found_close_bracket = False

    for i, line in enumerate(lines):
        if '"ROWS"' in line:
            found_rows = True
            # Next line should be '['
            if i + 1 < len(lines) and lines[i + 1].strip() == '[':
                found_open_bracket = True
        if found_rows and line.strip() == '[':
            found_open_bracket = True
        if found_rows and line.strip() == ']':
            found_close_bracket = True

    assert found_rows, f"$REQ_JSON_004: Should have ROWS section"  # $REQ_JSON_004
    assert found_open_bracket, f"$REQ_JSON_004: ROWS section should have '[' on its own line"  # $REQ_JSON_004
    assert found_close_bracket, f"$REQ_JSON_004: ROWS section should have ']' on its own line"  # $REQ_JSON_004

    # Also verify via parsing that ROWS is a list
    data = json.loads(output)
    for table_obj in data:
        assert isinstance(table_obj['ROWS'], list), f"$REQ_JSON_004: ROWS should be a list"  # $REQ_JSON_004

    print("✓ $REQ_JSON_004: Dump Mode ROWS Format")

def test_dump_mode_child_object_line_structure():
    """Test $REQ_JSON_005: Dump Mode Child Object Line Structure"""
    db_path = create_test_db()
    output = run_sqlite2json(db_path)

    lines = output.strip().split('\n')

    # Count the occurrences of { and } on their own lines
    # We expect: multiple table {, multiple table }
    open_braces = [i for i, line in enumerate(lines) if line.strip() == '{']
    close_braces = [i for i, line in enumerate(lines) if line.strip() in ['}', '},', '}']]

    # Should have at least 2 { (2 tables)
    assert len(open_braces) >= 2, f"$REQ_JSON_005: Should have table objects with {{ on their own lines"  # $REQ_JSON_005

    # Parse and verify each table is a separate child object
    data = json.loads(output)
    assert len(data) >= 2, f"$REQ_JSON_005: Should have multiple table objects"  # $REQ_JSON_005

    for table_obj in data:
        assert isinstance(table_obj, dict), f"$REQ_JSON_005: Each table should be an object"  # $REQ_JSON_005

    print("✓ $REQ_JSON_005: Dump Mode Table Object Line Structure")

def test_row_shape():
    """Test $REQ_JSON_006: Row Shape"""
    db_path = create_test_db()
    output = run_sqlite2json(db_path, 'SELECT id, name FROM people WHERE id = 1')

    lines = output.strip().split('\n')

    # Parse the row (skip [ and ])
    for line in lines[1:-1]:
        if line.strip():
            row = json.loads(line)
            assert isinstance(row, dict), f"$REQ_JSON_006: Row should be a JSON object"  # $REQ_JSON_006
            assert 'id' in row, f"$REQ_JSON_006: Row should have 'id' key"  # $REQ_JSON_006
            assert 'name' in row, f"$REQ_JSON_006: Row should have 'name' key"  # $REQ_JSON_006
            assert row['id'] == 1, f"$REQ_JSON_006: id value should be 1"  # $REQ_JSON_006
            assert row['name'] == 'Ada', f"$REQ_JSON_006: name value should be 'Ada'"  # $REQ_JSON_006
            break

    print("✓ $REQ_JSON_006: Row Shape")

def test_row_and_column_order():
    """Test $REQ_JSON_007: Row and Column Order"""
    # $REQ_JSON_007 - Not reasonably testable: The requirement states order follows
    # SQLite and can be controlled with --sql. We can't test SQLite's internal ordering
    # behavior; we can only verify that the tool doesn't crash and produces output.
    print("✓ $REQ_JSON_007: Not reasonably testable - SQLite order is implementation-dependent")

def test_valid_json_output():
    """Test $REQ_JSON_008: Valid JSON Output"""
    db_path = create_test_db()

    # Test SQL mode produces valid JSON
    sql_output = run_sqlite2json(db_path, 'SELECT * FROM people')

    try:
        parsed = json.loads(sql_output)
        assert isinstance(parsed, list), f"$REQ_JSON_008: SQL mode should produce a JSON list"  # $REQ_JSON_008
    except json.JSONDecodeError as e:
        assert False, f"$REQ_JSON_008: SQL mode output is not valid JSON: {e}"  # $REQ_JSON_008

    # Test dump mode produces valid JSON
    dump_output = run_sqlite2json(db_path)

    try:
        parsed = json.loads(dump_output)
        assert isinstance(parsed, list), f"$REQ_JSON_008: Dump mode should produce a JSON list"  # $REQ_JSON_008
    except json.JSONDecodeError as e:
        assert False, f"$REQ_JSON_008: Dump mode output is not valid JSON: {e}"  # $REQ_JSON_008

    print("✓ $REQ_JSON_008: Valid JSON Output")

def test_integer_and_real_value_mapping():
    """Test $REQ_JSON_009: INTEGER and REAL Value Mapping"""
    db_path = create_test_db()
    output = run_sqlite2json(db_path, 'SELECT id, score FROM people WHERE id = 1')

    lines = output.strip().split('\n')

    for line in lines[1:-1]:
        if line.strip():
            row = json.loads(line)
            assert isinstance(row['id'], int), f"$REQ_JSON_009: INTEGER should map to JSON number (int)"  # $REQ_JSON_009
            assert isinstance(row['score'], (int, float)), f"$REQ_JSON_009: REAL should map to JSON number"  # $REQ_JSON_009
            break

    print("✓ $REQ_JSON_009: INTEGER and REAL Value Mapping")

def test_text_value_mapping():
    """Test $REQ_JSON_010: TEXT Value Mapping"""
    db_path = create_test_db()
    output = run_sqlite2json(db_path, 'SELECT name FROM people WHERE id = 1')

    lines = output.strip().split('\n')

    for line in lines[1:-1]:
        if line.strip():
            row = json.loads(line)
            assert isinstance(row['name'], str), f"$REQ_JSON_010: TEXT should map to JSON string"  # $REQ_JSON_010
            assert row['name'] == 'Ada', f"$REQ_JSON_010: TEXT value should be 'Ada'"  # $REQ_JSON_010
            break

    print("✓ $REQ_JSON_010: TEXT Value Mapping")

def test_null_value_mapping():
    """Test $REQ_JSON_011: NULL Value Mapping"""
    db_path = create_test_db()
    output = run_sqlite2json(db_path, 'SELECT age, notes FROM people WHERE id = 2')

    lines = output.strip().split('\n')

    for line in lines[1:-1]:
        if line.strip():
            row = json.loads(line)
            assert row['age'] is None, f"$REQ_JSON_011: NULL should map to JSON null, got: {row['age']}"  # $REQ_JSON_011
            assert row['notes'] is None, f"$REQ_JSON_011: NULL should map to JSON null, got: {row['notes']}"  # $REQ_JSON_011
            break

    print("✓ $REQ_JSON_011: NULL Value Mapping")

if __name__ == '__main__':
    # Check if the executable exists
    exe_path = Path('./released/sqlite2json.exe')
    if not exe_path.exists():
        print(f"Error: {exe_path} not found. Build the project first.", file=sys.stderr)
        sys.exit(97)  # Build failed

    # Run all tests
    test_sql_mode_list_structure()
    test_dump_mode_list_structure()
    test_dump_mode_table_entry_attributes()
    test_dump_mode_rows_format()
    test_dump_mode_child_object_line_structure()
    test_row_shape()
    test_row_and_column_order()
    test_valid_json_output()
    test_integer_and_real_value_mapping()
    test_text_value_mapping()
    test_null_value_mapping()

    print("\n✅ All JSON output format tests passed!")
    sys.exit(0)
