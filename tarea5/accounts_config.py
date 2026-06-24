from __future__ import annotations

import argparse
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml

from tarea2 import settings


DEFAULT_SOURCE_PATH = settings.FILE_FILTROS
DEFAULT_OUTPUT_PATH = settings.FILE_ACCOUNTS_CONFIG
ACCOUNT_METADATA_COLUMNS = [
    "Descripcion Cuenta",
    "Agrupacion P&L",
    "Roll Up",
    "Agrupación UM",
]


def _normalize_account(value: object) -> str | None:
    if pd.isna(value):
        return None

    if isinstance(value, float) and value.is_integer():
        text = str(int(value))
    else:
        text = str(value).strip()

    if not text or text.lower() == "cuenta":
        return None

    return text


def _normalize_text(value: object) -> str | None:
    if pd.isna(value):
        return None

    text = str(value).strip()
    return text or None


def _build_account_record(row: pd.Series) -> dict[str, str | None]:
    return {column: _normalize_text(row.get(column)) for column in ACCOUNT_METADATA_COLUMNS}


def extract_unique_accounts(source_path: Path, sheet_name: str = "Accounts", usecols: str = "B") -> list[str]:
    source_df = pd.read_excel(source_path, sheet_name=sheet_name, header=None, usecols=usecols)
    accounts = OrderedDict()

    for raw_value in source_df.iloc[:, 0].tolist():
        account = _normalize_account(raw_value)
        if account is not None:
            accounts.setdefault(account, None)

    if not accounts:
        raise ValueError(f"No se encontraron cuentas válidas en {source_path} [{sheet_name}:{usecols}].")

    return list(accounts.keys())


def extract_account_descriptions(source_path: Path, sheet_name: str = "Accounts") -> OrderedDict[str, str | None]:
    source_df = pd.read_excel(source_path, sheet_name=sheet_name, header=1, usecols=["Cuenta", "Descripcion Cuenta"])
    account_descriptions: OrderedDict[str, str | None] = OrderedDict()

    for _, row in source_df.iterrows():
        account = _normalize_account(row.get("Cuenta"))
        if account is None:
            continue

        description = row.get("Descripcion Cuenta")
        normalized_description = None if pd.isna(description) else (str(description).strip() or None)
        account_descriptions.setdefault(account, normalized_description)

    if not account_descriptions:
        raise ValueError(f"No se encontraron descripciones de cuentas válidas en {source_path} [{sheet_name}].")

    return account_descriptions


def extract_account_metadata(source_path: Path, sheet_name: str = "Accounts") -> OrderedDict[str, dict[str, str | None]]:
    source_df = pd.read_excel(
        source_path,
        sheet_name=sheet_name,
        header=1,
        usecols=["Cuenta", *ACCOUNT_METADATA_COLUMNS],
    )
    account_metadata: OrderedDict[str, dict[str, str | None]] = OrderedDict()

    for _, row in source_df.iterrows():
        account = _normalize_account(row.get("Cuenta"))
        if account is None:
            continue

        account_metadata.setdefault(account, _build_account_record(row))

    if not account_metadata:
        raise ValueError(f"No se encontró metadata de cuentas válida en {source_path} [{sheet_name}].")

    return account_metadata


def generate_accounts_config(source_path: Path, output_path: Path) -> Path:
    source_path = Path(source_path)
    output_path = Path(output_path)

    account_metadata = extract_account_metadata(source_path)
    payload = {"accounts": dict(account_metadata)}

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as config_file:
        yaml.safe_dump(payload, config_file, allow_unicode=False, sort_keys=False)

    print(f"✅ Config de cuentas generado: {output_path}")
    print(f"   Total de cuentas únicas: {len(account_metadata)}")
    return output_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Genera el config local de cuentas únicas desde Filtros Consolidado.xlsx")
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE_PATH,
        help="Ruta al archivo Filtros Consolidado.xlsx",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Ruta del archivo de salida YAML",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    generate_accounts_config(args.source, args.output)


if __name__ == "__main__":
    main()