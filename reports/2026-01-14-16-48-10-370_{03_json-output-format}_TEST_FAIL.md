# Test Report: 03_json-output-format
**Timestamp:** 2026-01-14-16-48-10-370
**Status:** FAIL
**Test File:** tests\passing\03_json-output-format.py

---

## Output

```
Traceback (most recent call last):
  File "C:\Users\Human\Desktop\prjx\sqlite2json\tests\passing\03_json-output-format.py", line 301, in <module>
    test_sql_mode_list_structure()
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "C:\Users\Human\Desktop\prjx\sqlite2json\tests\passing\03_json-output-format.py", line 100, in test_sql_mode_list_structure
    parsed = json.loads(output)
  File "C:\Users\Human\AppData\Roaming\uv\python\cpython-3.13.7-windows-x86_64-none\Lib\json\__init__.py", line 346, in loads
    return _default_decoder.decode(s)
           ~~~~~~~~~~~~~~~~~~~~~~~^^^
  File "C:\Users\Human\AppData\Roaming\uv\python\cpython-3.13.7-windows-x86_64-none\Lib\json\decoder.py", line 345, in decode
    obj, end = self.raw_decode(s, idx=_w(s, 0).end())
               ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Human\AppData\Roaming\uv\python\cpython-3.13.7-windows-x86_64-none\Lib\json\decoder.py", line 361, in raw_decode
    obj, end = self.scan_once(s, idx)
               ~~~~~~~~~~~~~~^^^^^^^^
json.decoder.JSONDecodeError: Expecting ',' delimiter: line 3 column 1 (char 24)

```

---

**Result:** ✗ FAIL
