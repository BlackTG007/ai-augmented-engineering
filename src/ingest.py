"""
ingest.py -- Market data identifier ingestion pipeline

Reads a CSV of market data records, resolves each instrument identifier
to an OpenFIGI code, counts rows by exchange, and writes enriched CSV
to stdout.

Usage:
    python -m src.ingest data/sample_input.csv > data/python_output.csv
"""

from __future__ import annotations

import csv
import logging
import sys
from collections import Counter
from pathlib import Path

from src.figi_client import FigiClient, FigiClientError

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

EXPECTED_COLUMNS = {
    "record_id",
    "instrument_id",
    "id_type",
    "exchange_code",
    "price",
    "volume",
    "timestamp",
}
CRITICAL_FIELDS = {"record_id", "instrument_id", "exchange_code", "price", "volume"}
OUTPUT_COLUMNS = [
    "record_id",
    "instrument_id",
    "id_type",
    "exchange_code",
    "figi",
    "price",
    "volume",
    "timestamp",
    "lookup_count",
    "exchange_rank",
]


def load_records(input_path: Path) -> list[dict]:
    """Load market data records from a CSV file.

    Args:
        input_path: Path to the input CSV file.

    Returns:
        List of record dicts with string values for all columns.

    Raises:
        FileNotFoundError: If input_path does not exist.
        ValueError: If the header is missing required columns or there are no rows.
    """
    logger.info(f"Starting load_records with {input_path} records")

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with input_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        missing = EXPECTED_COLUMNS - set(fieldnames)
        if missing:
            raise ValueError(f"Input schema missing columns: {sorted(missing)}")
        records: list[dict] = [dict(row) for row in reader]

    for record in records:
        record_id = record.get("record_id", "") or "?"
        for field in CRITICAL_FIELDS:
            value = record.get(field, None)
            if value is None or value == "":
                logger.warning(
                    f"Record {record_id}: missing critical field {field}"
                )

    if not records:
        raise ValueError(f"No records found in {input_path}")

    logger.info(f"Completed load_records with {len(records)} records")
    return records


def resolve_figis(records: list[dict], client: FigiClient) -> dict[str, str]:
    """Resolve instrument identifiers to OpenFIGI codes.

    Rows with an empty instrument_id are omitted from the API batch and
    left out of the returned map so write_output can emit figi=UNKNOWN.

    Args:
        records: List of market data record dicts.
        client: Configured FigiClient instance.

    Returns:
        Mapping of instrument_id to FIGI string (or 'UNKNOWN' on failure).
    """
    logger.info(f"Starting resolve_figis with {len(records)} records")

    identifiers = [
        {
            "idType": row.get("id_type") or "TICKER",
            "idValue": instrument_id,
            "exchCode": row.get("exchange_code") or None,
        }
        for row in records
        if (instrument_id := row.get("instrument_id") or "")
    ]

    figi_map: dict[str, str] = {}
    if not identifiers:
        logger.info(f"Completed resolve_figis with {len(figi_map)} records")
        return figi_map

    try:
        results = client.do_request(identifiers)
    except FigiClientError as exc:
        logger.error(f"FigiClient request failed: {exc}")
        results = None

    if results:
        for index, item in enumerate(results):
            instrument_id = identifiers[index].get("idValue") or ""
            payload = item.get("data", None) if item else None
            first = payload[0] if payload else None
            figi = first.get("figi", None) if isinstance(first, dict) else None
            figi_map[instrument_id] = figi or "UNKNOWN"
    else:
        figi_map = {ident.get("idValue") or "": "UNKNOWN" for ident in identifiers}

    logger.info(f"Completed resolve_figis with {len(figi_map)} records")
    return figi_map


def rank_exchanges(records: list[dict]) -> tuple[Counter, dict[str, int]]:
    """Count and rank exchanges by lookup frequency.

    Args:
        records: List of market data record dicts.

    Returns:
        Tuple of (exchange_counts Counter, exchange_rank dict).
    """
    logger.info(f"Starting rank_exchanges with {len(records)} records")

    exchange_counts: Counter = Counter(
        row.get("exchange_code") or "UNKNOWN" for row in records
    )
    sorted_exchanges = sorted(
        exchange_counts, key=lambda exchange: exchange_counts[exchange], reverse=True
    )
    exchange_rank = {
        exchange: rank for rank, exchange in enumerate(sorted_exchanges, start=1)
    }

    logger.info(f"Completed rank_exchanges with {len(records)} records")
    return exchange_counts, exchange_rank


def write_output(
    records: list[dict],
    figi_map: dict[str, str],
    exchange_counts: Counter,
    exchange_rank: dict[str, int],
) -> None:
    """Write enriched records to stdout as CSV.

    Args:
        records: Original market data records.
        figi_map: instrument_id -> FIGI mapping.
        exchange_counts: Count of records per exchange.
        exchange_rank: Rank of each exchange by frequency.
    """
    logger.info(f"Starting write_output with {len(records)} records")

    writer = csv.DictWriter(sys.stdout, fieldnames=OUTPUT_COLUMNS, lineterminator="\n")
    writer.writeheader()

    for row in records:
        instrument_id = row.get("instrument_id") or ""
        exchange_code = row.get("exchange_code") or "UNKNOWN"
        writer.writerow(
            {
                "record_id": row.get("record_id") or "",
                "instrument_id": instrument_id,
                "id_type": row.get("id_type") or "",
                "exchange_code": exchange_code,
                "figi": figi_map.get(instrument_id, "UNKNOWN"),
                "price": row.get("price") or "",
                "volume": row.get("volume") or "",
                "timestamp": row.get("timestamp") or "",
                "lookup_count": exchange_counts.get(exchange_code, 0),
                "exchange_rank": exchange_rank.get(exchange_code, 0),
            }
        )

    logger.info(f"Completed write_output with {len(records)} records")


def main(input_file: str) -> None:
    """Run the ingest pipeline.

    Args:
        input_file: Path string to the input CSV file.
    """
    input_path = Path(input_file)
    logger.info(f"Starting main with {input_path} records")
    records = load_records(input_path)
    figi_map = resolve_figis(records, FigiClient())
    exchange_counts, exchange_rank = rank_exchanges(records)
    write_output(records, figi_map, exchange_counts, exchange_rank)

    logger.info(f"Completed main with {len(records)} records")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <input_csv>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])
