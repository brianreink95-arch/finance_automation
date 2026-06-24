from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import yaml

from tarea2 import settings


DEFAULT_CONFIG_PATH = settings.FILE_ACCOUNTS_CONFIG


def load_accounts_series(config_path: Path) -> pd.Series:
    config_path = Path(config_path)

    with config_path.open("r", encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file) or {}

    accounts = config.get("accounts", {})
    if isinstance(accounts, dict):
        account_values = list(accounts.keys())
    elif isinstance(accounts, list):
        account_values = accounts
    else:
        raise ValueError(f"El archivo {config_path} no contiene una colección válida en 'accounts'.")

    series = pd.Series(account_values, name="account", dtype="string")
    if series.empty:
        raise ValueError(f"El archivo {config_path} no contiene cuentas para cargar.")

    return series


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Carga accounts_config.yml y genera una Series de Pandas con las cuentas")
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Ruta al archivo accounts_config.yml",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    accounts_series = load_accounts_series(args.config)
    print(accounts_series)
    print(f"\nTotal de cuentas: {len(accounts_series)}")


if __name__ == "__main__":
    main()