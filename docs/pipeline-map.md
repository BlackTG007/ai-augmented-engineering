# Market Data Pipeline Map

Generated from the Perl source in `perl/`. The pipeline is a three-stage batch
job that reads end-of-day market data, enriches identifiers, derives trade
metrics, and validates the result against a registered schema.

## End-to-end data flow

```
data/sample_input.csv
        |
        v
   ingest.pl / ingest.py     OpenFIGI mapping (FigiClient)
        |                    100 req / 60s, retry up to 5 times on HTTP 429
        v
   enriched CSV (stdout)
        |
        v
   transform.pl / transform.py
        |
        v
   transformed CSV (stdout)
        |
        v
   validate.pl / validate.py
        |
        v
   validation report (stdout)
   exit 0 PASS / exit 1 FAIL
```

## Stage 1: Ingest (`perl/ingest.pl`)

**Purpose:** Read raw market data records from CSV and enrich each instrument
with an OpenFIGI identifier. Count and rank exchanges by how often they appear.

**Inputs:** CSV file path as argv[0]. Columns:

`record_id, instrument_id, id_type, exchange_code, price, volume, timestamp`

**External calls:** OpenFIGI `https://api.openfigi.com/v2/mapping` via
`FigiClient` (`perl/FigiClient.pm` / `src/figi_client.py`). API key from
`OPENFIGI_API_KEY`, falling back to `DEMO_KEY` in the Perl (fixture mode in
Python when no live key is set).

**Transformations:**

- Skip blank lines. Die if the file has no records.
- Rows with a missing `instrument_id` are **not** sent to OpenFIGI (Perl warns
  "skipping"), but they **stay in the output** with `figi=UNKNOWN`.
- Default `id_type` to `TICKER` when empty.
- Map each `instrument_id` to the first FIGI in the API `data` array, or
  `UNKNOWN` when the lookup is empty or the request fails.
- Count rows by `exchange_code` (missing codes count as `UNKNOWN`).
- Rank exchanges by count descending. The Perl uses `reverse sort` on hash
  keys, which does not define a tie order.
- Append `figi`, `lookup_count`, and `exchange_rank`.

**Outputs:** CSV on stdout with columns:

`record_id, instrument_id, id_type, exchange_code, figi, price, volume, timestamp, lookup_count, exchange_rank`

**Downstream:** transform reads this CSV.

## Stage 2: Transform (`perl/transform.pl`)

**Purpose:** Normalise prices, compute notional, classify trade size, and flag
FIGI / timestamp quality.

**Inputs:** Stage 1 CSV (file argument or STDIN).

**Transformations:**

- Skip rows with missing or non-numeric `price` / `volume`.
- `price` formatted to 4 decimal places.
- `notional = price * volume`.
- Size bucket: `BLOCK >= 1,000,000`, `LARGE >= 100,000`, `MID >= 10,000`,
  otherwise `SMALL`.
- `figi_resolved = 1` when `figi` is present and not `UNKNOWN`, else `0`.
- `ts_valid = 1` when timestamp matches `YYYY-MM-DD HH:MM:SS`.

**Outputs:** Stage 1 columns plus `notional, size_bucket, figi_resolved, ts_valid`.

**Downstream:** validate reads this CSV.

## Stage 3: Validate (`perl/validate.pl`)

**Purpose:** Check every transformed row against the registered rules. Print a
report and exit non-zero on any critical violation.

**Inputs:** Stage 2 CSV (file argument or STDIN).

**Critical checks:** `record_id` present and unique; `instrument_id` present;
`price` positive with exactly 4 decimal places; `volume` a positive integer;
`figi_resolved = 1`.

**Warning checks:** `ts_valid = 1`; `notional > 0`.

**Info:** `size_bucket` in `{SMALL, MID, LARGE, BLOCK}`.

**Outputs:** Validation report on stdout. Exit `0` (PASS) or `1` (FAIL).

## Known issue: exchange rank ties

All five exchange codes in `data/sample_input.csv` appear exactly four times.
Perl's `reverse sort { $counts{$a} <=> $counts{$b} } keys %counts` has no
secondary key, and hash key order is randomised per process. Python's
`sorted(..., reverse=True)` is stable and keeps first-seen order. The two
outputs disagree on `exchange_rank` whenever counts tie. The conversion should
**define** a tie-break (count descending, then `exchange_code` ascending)
rather than reproduce Perl's accidental order.
