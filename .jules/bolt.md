## 2024-05-20 - Manna ISO-8601 parsing optimization
**Learning:** `dateutil.parser.parse` is significantly slower than `datetime.fromisoformat` for ISO-8601 date strings. In large loops, such as parsing CSV rows in Manna format, this creates a major bottleneck.
**Action:** Used the fast path built in `datestring_to_ts` utility which first tries `datetime.fromisoformat` to significantly improve parsing time.

## 2024-05-21 - PyParsing overhead
**Learning:** Instantiating pyparsing grammar objects dynamically inside a function is incredibly slow compared to creating them once at module level. Time per string parse drops from ~1.12s to ~0.11s for 10000 strings when the grammar is constructed once.
**Action:** Move `grammar()` construction in `datcon.py` to the module level.

## 2026-04-26 - Benedict dictionary wrapper overhead in validation
**Learning:** Automatically wrapping every parsed JSON line into a `benedict` object inside `JsonlinesIO` introduces enormous overhead when processing large files. `jsonschema` validation works perfectly with raw dictionaries.
**Action:** Use the `raw=True` parameter in `JsonlinesIO` in `fvc.tools.df.core.validate` to avoid unnecessary object creation overhead.
