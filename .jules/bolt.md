## 2024-05-20 - Manna ISO-8601 parsing optimization
**Learning:** `dateutil.parser.parse` is significantly slower than `datetime.fromisoformat` for ISO-8601 date strings. In large loops, such as parsing CSV rows in Manna format, this creates a major bottleneck.
**Action:** Used the fast path built in `datestring_to_ts` utility which first tries `datetime.fromisoformat` to significantly improve parsing time.
