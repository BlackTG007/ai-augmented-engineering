# Conversion Plan: ingest.pl to ingest.py

Target: `perl/ingest.pl` → `src/ingest.py`
Tests: `tests/test_ingest.py` (written and committed before implementation)
Reuse: `src/figi_client.py` (already converted). Tests mock `FigiClient.do_request`.

Rules applied without being restated in every step: `.cursor/rules/de-standards.mdc`
and `.cursor/rules/perl-to-python.mdc` (type hints, `pathlib.Path`, `collections.Counter`,
entry/exit `logger.info`, no line-by-line Perl translation).

## Clarifications (match Perl behaviour, idiomatic Python)

- Rows with a missing `instrument_id` stay in the output with `figi=UNKNOWN`.
  They are omitted from the OpenFIGI batch only.
- Tied exchange counts: sort by count descending, then `exchange_code` ascending.
  Do not try to reproduce Perl hash-key order.

## Library substitutions

| Perl | Python |
|------|--------|
| `FigiClient.pm` | `src.figi_client.FigiClient` |
| `LWP::UserAgent` | already inside `FigiClient` (`requests.Session`) |
| `JSON::from_json` / `to_json` | `json` (inside the client) |
| `open` + `split /,/` | `pathlib.Path.open` + `csv.DictReader` / `csv.DictWriter` |
| Manual `%exchange_counts` increment | `collections.Counter` |
| `reverse sort { $a <=> $b } keys %hash` | `sorted(counts, key=lambda e: (-counts[e], e))` |
| `die` on missing input | raise `FileNotFoundError` / `ValueError`; no `exit()` in library functions |
| `$ENV{OPENFIGI_API_KEY} \|\| 'DEMO_KEY'` | `FigiClient()` (fixture mode when no live key) |

## Function signatures

```python
def load_records(input_path: Path) -> list[dict]: ...
def resolve_figis(records: list[dict], client: FigiClient) -> dict[str, str]: ...
def rank_exchanges(records: list[dict]) -> tuple[Counter, dict[str, int]]: ...
def write_output(
    records: list[dict],
    figi_map: dict[str, str],
    exchange_counts: Counter,
    exchange_rank: dict[str, int],
) -> None: ...
def main(input_file: str) -> None: ...
```

Every function logs on entry and exit:

`logger.info(f'Starting {function_name} with {len(records)} records')`

## Implementation steps

1. **Analyse data flow** — CSV in, FIGI map, exchange counts/ranks, CSV out.
   Empty lines skipped. Missing `instrument_id` kept in output as `UNKNOWN`.

2. **`load_records`** — `Path.open` + `csv.DictReader`. Validate expected
   column names before processing (schema drift). Raise `FileNotFoundError`
   if the path is missing, `ValueError` if there are no rows. Check critical
   fields (`record_id`, `instrument_id`, `exchange_code`, `price`, `volume`)
   for `None` and log a warning; do not drop the row.

3. **`resolve_figis`** — Build the OpenFIGI payload with a list comprehension.
   Default `id_type` to `TICKER`. Skip empty `instrument_id` in the batch.
   Call `client.do_request`. Map each id to `data[0]["figi"]` or `UNKNOWN`.
   On `FigiClientError` or a `None` result, every looked-up id is `UNKNOWN`.

4. **`rank_exchanges`** — `Counter(r.get("exchange_code") or "UNKNOWN" for r in records)`.
   Rank with `sorted(counts, key=lambda e: (-counts[e], e))`.

5. **`write_output`** — `csv.DictWriter` to stdout with `lineterminator="\n"`.
   Every pipeline field uses `.get(..., default)` (or `or ""` / `or "UNKNOWN"`).
   Missing FIGI → `UNKNOWN`. Missing exchange → `UNKNOWN`.

6. **`main`** — `Path(input_file)` → load → `FigiClient()` → resolve → rank → write.

7. **Verify** — `pytest tests/test_ingest.py -v`, then
   `python -m src.ingest data/sample_input.csv` vs `data/perl_output_reference.csv`.
   Diff must be empty after the tie-break is in place.

## Out of scope

- Do not convert `transform.pl` or `validate.pl` in this change.
- Do not call the live OpenFIGI API from tests.
