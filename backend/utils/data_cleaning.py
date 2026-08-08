import argparse
import csv
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

DATE_FIELD_KEYWORDS = {"date", "issue_date", "complaint_date", "ticket_date"}
DATE_INPUT_FORMATS = ["%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d", "%Y/%m/%d"]
DATE_OUTPUT_FORMAT = "%d-%m-%Y"

MISSING_VALUES = {"", "na", "n/a", "none", "null", "nan"}


def normalize_date(value: str) -> str:
    value = value.strip()
    for fmt in DATE_INPUT_FORMATS:
        try:
            parsed = datetime.strptime(value, fmt)
            return parsed.strftime(DATE_OUTPUT_FORMAT)
        except ValueError:
            continue

    raise ValueError(f"Unsupported date format: {value}")


def parse_number(value: str) -> Any:
    value = value.strip()
    if value == "":
        raise ValueError("Empty numeric value")

    lower = value.lower()
    if lower in MISSING_VALUES:
        raise ValueError(f"Missing numeric value: {value}")

    cleaned = value.replace(",", "").replace("%", "")
    if cleaned == "":
        raise ValueError(f"Missing numeric value: {value}")

    if cleaned.replace("-", "").replace(".", "").isdigit():
        if "." in cleaned:
            return float(cleaned)
        return int(cleaned)

    raise ValueError(f"Not a numeric value: {value}")


def is_date_column(header: str) -> bool:
    header_key = header.strip().lower()
    return any(keyword in header_key for keyword in DATE_FIELD_KEYWORDS)


def normalize_value(header: str, value: str) -> Any:
    if value is None:
        raise ValueError("Missing value")

    text = value.strip()
    if text.lower() in MISSING_VALUES:
        raise ValueError(f"Missing value: {value}")

    if is_date_column(header):
        return normalize_date(text)

    numeric_check = text.replace("-", "").replace(".", "").replace(",", "")
    if numeric_check.isdigit():
        return parse_number(text)

    return text


def clean_csv(input_path: Path, output_path: Optional[Path] = None) -> int:
    input_path = input_path.resolve()
    if output_path is None:
        output_path = input_path.with_name(f"{input_path.stem}_cleaned{input_path.suffix}")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with input_path.open("r", newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        headers = reader.fieldnames or []
        cleaned_rows: List[Dict[str, Any]] = []

        for row_number, row in enumerate(reader, start=2):
            try:
                cleaned_row: Dict[str, Any] = {}
                for header in headers:
                    raw_value = row.get(header)
                    cleaned_row[header] = normalize_value(header, raw_value if raw_value is not None else "")
                cleaned_rows.append(cleaned_row)
            except ValueError:
                continue

    with output_path.open("w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(cleaned_rows)

    return len(cleaned_rows)


def find_csv_files(directory: Path) -> Iterable[Path]:
    for path in sorted(directory.glob("*.csv")):
        if path.is_file():
            yield path


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean CSV data by normalizing dates, converting numeric values, and dropping rows with missing values.")
    parser.add_argument(
        "files",
        nargs="*",
        help="CSV files to clean. If omitted, cleans all CSV files in backend/data.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Optional output directory for cleaned files.",
    )
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parents[1] / "data"
    input_paths: List[Path] = []

    if args.files:
        input_paths = [Path(file).resolve() for file in args.files]
    else:
        input_paths = list(find_csv_files(base_dir))

    if not input_paths:
        raise SystemExit("No CSV files found to clean.")

    total_cleaned = 0
    for input_path in input_paths:
        if not input_path.exists():
            print(f"Skipping missing file: {input_path}")
            continue

        output_path = args.output_dir / input_path.name if args.output_dir else None
        cleaned_count = clean_csv(input_path, output_path)
        total_cleaned += cleaned_count
        print(f"Cleaned {cleaned_count} rows: {input_path.name} -> {output_path or input_path.with_name(input_path.stem + '_cleaned' + input_path.suffix)}")

    print(f"Total cleaned rows written: {total_cleaned}")


if __name__ == "__main__":
    main()
