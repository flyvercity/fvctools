## 2024-05-20 - Manna ISO-8601 parsing optimization
**Learning:** `dateutil.parser.parse` is significantly slower than `datetime.fromisoformat` for ISO-8601 date strings. In large loops, such as parsing CSV rows in Manna format, this creates a major bottleneck.
**Action:** Used the fast path built in `datestring_to_ts` utility which first tries `datetime.fromisoformat` to significantly improve parsing time.

## 2024-05-21 - PyParsing overhead
**Learning:** Instantiating pyparsing grammar objects dynamically inside a function is incredibly slow compared to creating them once at module level. Time per string parse drops from ~1.12s to ~0.11s for 10000 strings when the grammar is constructed once.
**Action:** Move `grammar()` construction in `datcon.py` to the module level.

## $(date +%Y-%m-%d) - Benedict dictionary wrapper overhead
**Learning:** Automatically wrapping every parsed JSON line into a `benedict` object inside `JsonlinesIO` introduces enormous overhead (approx. 25x slower than raw dicts) when processing large files.
**Action:** Use the `raw=True` parameter in `JsonlinesIO` when deep dictionary traversal is not needed, such as when merely reading a timestamp and shuffling records to new files.
