from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


DEFAULT_EXTRACT_PATH = Path(__file__).resolve().parent.parent / "auxiliar" / "Book1.xlsx"
HEADER_ROW_COUNT = 14
METADATA_COLUMN_COUNT = 3
HEADER_LEVEL_NAMES = [
    "measure",
    "month",
    "year",
    "scenario",
    "status",
    "distribution_channel_tree",
    "accounting_basis",
    "product",
    "country_scope",
    "currency_scope",
    "reporting_relationship",
    "segment",
    "function",
    "activity_setid",
]
METADATA_EMPTY_SUFFIX = ("",) * (HEADER_ROW_COUNT - 2)


def _build_metadata_tuple(name: str) -> tuple[str, ...]:
    return ("metadata", name, *METADATA_EMPTY_SUFFIX)


def metadata_column(name: str) -> tuple[str, ...]:
    return ("metadata", name, *METADATA_EMPTY_SUFFIX)


def _normalize_columns(columns: pd.MultiIndex) -> pd.MultiIndex:
    normalized_columns = []
    metadata_names = ["entity_scope", "accounting_base", "cost_center"]

    for index, column in enumerate(columns):
        if index < METADATA_COLUMN_COUNT:
            normalized_columns.append(_build_metadata_tuple(metadata_names[index]))
            continue

        normalized_columns.append(tuple("" if str(value).startswith("Unnamed:") else value for value in column))

    return pd.MultiIndex.from_tuples(normalized_columns, names=HEADER_LEVEL_NAMES)


def load_raw_extract(path: Path = DEFAULT_EXTRACT_PATH) -> pd.DataFrame:
    dataframe = pd.read_excel(path, header=list(range(HEADER_ROW_COUNT)))
    dataframe.columns = _normalize_columns(dataframe.columns)
    return dataframe


def get_metadata_columns(dataframe: pd.DataFrame) -> list[tuple[str, ...]]:
    return [column for column in dataframe.columns if column[0] == "metadata"]


def get_value_columns(dataframe: pd.DataFrame) -> list[tuple[str, ...]]:
    return [column for column in dataframe.columns if column[0] == "MTD"]


def describe_extract(dataframe: pd.DataFrame) -> str:
    metadata_columns = get_metadata_columns(dataframe)
    value_columns = get_value_columns(dataframe)

    preview_lines = [
        f"rows={len(dataframe)}",
        f"metadata_columns={len(metadata_columns)}",
        f"value_columns={len(value_columns)}",
        "metadata_names=" + ", ".join(column[1] for column in metadata_columns),
        "first_value_headers=",
    ]
    preview_lines.extend(
        f"- {column[1]} {column[2]} | {column[3]} | {column[4]}" for column in value_columns[:5]
    )
    return "\n".join(preview_lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Carga la extracción cruda de Task 5 con MultiIndex de 14 niveles")
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_EXTRACT_PATH,
        help="Ruta al Excel crudo extraído desde el sistema",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    dataframe = load_raw_extract(args.input)
    print(describe_extract(dataframe))
    print("\nPrimeras filas:")
    print(dataframe.head(5).to_string())


if __name__ == "__main__":
    main()