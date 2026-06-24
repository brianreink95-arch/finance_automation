from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import yaml

from tarea2 import settings
from tarea5.raw_extract_loader import get_value_columns, load_raw_extract, metadata_column


DERIVED_EMPTY_SUFFIX = ("",) * 12
DEFAULT_CONFIG_PATH = settings.FILE_ACCOUNTS_CONFIG
COST_CENTER_EXCEPTIONS = {
    "MNAR_10028399": "34029020",
}
ACCOUNT_METADATA_FIELDS = [
    "Descripcion Cuenta",
    "Agrupacion P&L",
    "Roll Up",
    "Agrupación UM",
]
ACCOUNT_CODE_FIELD = "Cuenta"
COST_CENTER_CODE_FIELD = "DeptID"


def derived_column(name: str) -> tuple[str, ...]:
    return ("derived", name, *DERIVED_EMPTY_SUFFIX)


def load_account_metadata_map(config_path: Path) -> dict[str, dict[str, str | None]]:
    with Path(config_path).open("r", encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file) or {}

    accounts = config.get("accounts", {})
    if not isinstance(accounts, dict):
        raise ValueError(f"El archivo {config_path} no contiene un mapeo válido en 'accounts'.")

    normalized_map: dict[str, dict[str, str | None]] = {}
    for account, value in accounts.items():
        if isinstance(value, dict):
            normalized_map[str(account)] = {field: value.get(field) for field in ACCOUNT_METADATA_FIELDS}
        else:
            normalized_map[str(account)] = {
                "Descripcion Cuenta": value,
                "Agrupacion P&L": None,
                "Roll Up": None,
                "Agrupación UM": None,
            }

    return normalized_map


def load_account_description_map(config_path: Path) -> dict[str, str | None]:
    metadata_map = load_account_metadata_map(config_path)
    return {account: metadata.get("Descripcion Cuenta") for account, metadata in metadata_map.items()}


def apply_stage1_account_cleaning(raw_dataframe: pd.DataFrame, account_metadata: dict[str, dict[str, str | None]]) -> pd.DataFrame:
    cleaned_dataframe = raw_dataframe.copy()

    accounting_base_col = metadata_column("accounting_base")
    cost_center_col = metadata_column("cost_center")

    cleaned_dataframe[accounting_base_col] = cleaned_dataframe[accounting_base_col].astype("string").str.strip()
    cleaned_dataframe[cost_center_col] = cleaned_dataframe[cost_center_col].astype("string").str.strip()

    account_candidate = cleaned_dataframe[accounting_base_col].str.split("-", n=1).str[0].str.strip()
    valid_account = account_candidate.where(account_candidate.isin(account_metadata.keys()), pd.NA)
    account_metadata_frame = pd.DataFrame.from_dict(account_metadata, orient="index")
    account_metadata_frame.index = account_metadata_frame.index.astype("string")
    matched_account_metadata = account_metadata_frame.reindex(valid_account).reset_index(drop=True)
    cost_center_candidate = cleaned_dataframe[cost_center_col].str.split("-", n=1).str[0].str.strip()
    cost_center_candidate = cost_center_candidate.replace(COST_CENTER_EXCEPTIONS)
    valid_cost_center = cost_center_candidate.where(cost_center_candidate.str.fullmatch(r"\d+"), pd.NA)

    cleaned_dataframe[derived_column("account_candidate")] = account_candidate
    cleaned_dataframe[derived_column(ACCOUNT_CODE_FIELD)] = valid_account
    cleaned_dataframe[derived_column("account_description")] = pd.Series(
        matched_account_metadata["Descripcion Cuenta"].to_numpy(),
        index=cleaned_dataframe.index,
        dtype="string",
    )
    for field_name in ACCOUNT_METADATA_FIELDS:
        cleaned_dataframe[derived_column(field_name)] = pd.Series(
            matched_account_metadata[field_name].to_numpy(),
            index=cleaned_dataframe.index,
            dtype="string",
        )
    cleaned_dataframe[derived_column("cost_center_candidate")] = cost_center_candidate
    cleaned_dataframe[derived_column(COST_CENTER_CODE_FIELD)] = valid_cost_center.astype("string")

    return cleaned_dataframe


def filter_rows_with_valid_account_and_cost_center(cleaned_dataframe: pd.DataFrame) -> pd.DataFrame:
    mask = cleaned_dataframe[derived_column(ACCOUNT_CODE_FIELD)].notna() & cleaned_dataframe[derived_column(COST_CENTER_CODE_FIELD)].notna()
    return cleaned_dataframe.loc[mask].copy()


def validate_and_filter_stage1(cleaned_dataframe: pd.DataFrame, tolerance: float = 1e-6) -> pd.DataFrame:
    report = build_reconciliation_report(cleaned_dataframe, tolerance=tolerance)
    if "reconciliation_passed=True" not in report:
        raise ValueError(
            "La validacion previa al filtro fallo. No se eliminaron filas con nulos en Cuenta y DeptID.\n"
            f"{report}"
        )

    return filter_rows_with_valid_account_and_cost_center(cleaned_dataframe)


def build_reconciliation_report(cleaned_dataframe: pd.DataFrame, tolerance: float = 1e-6) -> str:
    value_columns = get_value_columns(cleaned_dataframe)
    total_row = cleaned_dataframe.iloc[0][value_columns].astype(float)
    filtered_dataframe = filter_rows_with_valid_account_and_cost_center(cleaned_dataframe)
    filtered_sum = filtered_dataframe.loc[:, value_columns].astype(float).sum()
    difference = filtered_sum - total_row
    max_abs_diff = float(difference.abs().max())
    passed = bool((difference.abs() <= tolerance).all())

    report_lines = [
        f"reconciliation_passed={passed}",
        f"reconciliation_rows={len(filtered_dataframe)}",
        f"reconciliation_tolerance={tolerance}",
        f"reconciliation_max_abs_diff={max_abs_diff}",
    ]

    if not passed:
        report_lines.append("reconciliation_differences=")
        report_lines.extend(
            f"- {column[1]} {column[2]} | {column[3]} | diff={difference[column]}" for column in value_columns if abs(float(difference[column])) > tolerance
        )

    return "\n".join(report_lines)


def build_stage1_summary(cleaned_dataframe: pd.DataFrame) -> str:
    matched_count = int(cleaned_dataframe[derived_column(ACCOUNT_CODE_FIELD)].notna().sum())
    null_count = int(cleaned_dataframe[derived_column(ACCOUNT_CODE_FIELD)].isna().sum())
    described_count = int(cleaned_dataframe[derived_column("account_description")].notna().sum())
    cost_center_count = int(cleaned_dataframe[derived_column(COST_CENTER_CODE_FIELD)].notna().sum())
    cost_center_null_count = int(cleaned_dataframe[derived_column(COST_CENTER_CODE_FIELD)].isna().sum())

    return "\n".join(
        [
            f"total_rows={len(cleaned_dataframe)}",
            f"rows_with_account={matched_count}",
            f"rows_with_null_account={null_count}",
            f"rows_with_account_description={described_count}",
            f"rows_with_cost_center={cost_center_count}",
            f"rows_with_null_cost_center={cost_center_null_count}",
        ]
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ejecuta la primera limpieza de cuentas sobre la extracción cruda de Task 5")
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Ruta al archivo accounts_config.yml",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    raw_dataframe = load_raw_extract()
    account_metadata = load_account_metadata_map(args.config)
    cleaned_dataframe = apply_stage1_account_cleaning(raw_dataframe, account_metadata)
    filtered_dataframe = validate_and_filter_stage1(cleaned_dataframe)

    print(build_stage1_summary(cleaned_dataframe))
    print("\nValidacion previa al filtro:")
    print(build_reconciliation_report(cleaned_dataframe))
    print("\nFilas luego de eliminar nulos en Cuenta y DeptID:")
    print(f"filtered_rows={len(filtered_dataframe)}")
    print("\nMuestra de columnas derivadas:")
    preview_columns = [
        metadata_column("accounting_base"),
        metadata_column("cost_center"),
        derived_column("account_candidate"),
        derived_column(ACCOUNT_CODE_FIELD),
        derived_column("account_description"),
        derived_column("cost_center_candidate"),
        derived_column(COST_CENTER_CODE_FIELD),
    ]
    print(filtered_dataframe.loc[:, preview_columns].head(12).to_string())


if __name__ == "__main__":
    main()