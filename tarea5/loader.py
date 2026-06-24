from __future__ import annotations

import pandas as pd

from tarea2 import loader as task2_loader
from tarea5 import settings
from tarea5.raw_extract_loader import load_raw_extract
from tarea5.stage1_account_cleaning import load_account_metadata_map


def validate_required_inputs() -> None:
    if not settings.INPUT_DIR.exists():
        raise FileNotFoundError(f"❌ No existe la carpeta de inputs de Task 5: {settings.INPUT_DIR}")

    if not settings.FILE_FORECAST.exists():
        raise FileNotFoundError(f"❌ No existe el forecast de Task 5: {settings.FILE_FORECAST}")

    if not settings.FILE_TASK2_REPORT_PL.exists():
        raise FileNotFoundError(f"❌ No existe el P&L base de Task 2: {settings.FILE_TASK2_REPORT_PL}")

    if not settings.FILE_FILTROS.exists():
        raise FileNotFoundError(f"❌ No existe Filtros Consolidado.xlsx: {settings.FILE_FILTROS}")

    if not settings.FILE_ACCOUNTS_CONFIG.exists():
        raise FileNotFoundError(f"❌ No existe accounts_config.yml: {settings.FILE_ACCOUNTS_CONFIG}")


def load_task5_inputs() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, dict[str, str | None]]]:
    raw_forecast = load_raw_extract(settings.FILE_FORECAST)
    df_filtros = task2_loader.cargar_excel_exacto(settings.FILE_FILTROS, sheet_name="Accounts", header=1)
    account_metadata = load_account_metadata_map(settings.FILE_ACCOUNTS_CONFIG)
    return raw_forecast, df_filtros, account_metadata