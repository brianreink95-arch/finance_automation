from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from tarea5.raw_extract_loader import get_value_columns
from tarea5.stage1_account_cleaning import (
    ACCOUNT_CODE_FIELD,
    apply_stage1_account_cleaning,
    derived_column,
    validate_and_filter_stage1,
)


MONTH_NAME_TO_NUMBER = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12,
}


@dataclass
class Task5ProcessingResult:
    cleaned_dataframe: pd.DataFrame
    filtered_dataframe: pd.DataFrame
    rollup_by_month: pd.DataFrame
    actual_months: list[int]
    forecast_months: list[int]


def _month_number_from_column(column: tuple[str, ...]) -> int:
    month_name = str(column[1])
    if month_name not in MONTH_NAME_TO_NUMBER:
        raise ValueError(f"Mes no soportado en el forecast: {month_name}")
    return MONTH_NAME_TO_NUMBER[month_name]


def _scenario_from_column(column: tuple[str, ...]) -> str:
    return str(column[3])


def build_task5_rollup_forecast(
    raw_dataframe: pd.DataFrame,
    df_filtros: pd.DataFrame,
    account_metadata: dict[str, dict[str, str | None]],
    current_month: int,
) -> Task5ProcessingResult:
    cleaned_dataframe = apply_stage1_account_cleaning(raw_dataframe, account_metadata)
    filtered_dataframe = validate_and_filter_stage1(cleaned_dataframe)

    value_columns = get_value_columns(filtered_dataframe)
    rollup_map = (
        df_filtros.loc[:, ["Cuenta", "Roll Up"]]
        .dropna(subset=["Cuenta"])
        .drop_duplicates(subset=["Cuenta"])
        .assign(Cuenta=lambda df: df["Cuenta"].astype(str))
        .set_index("Cuenta")["Roll Up"]
    )

    rollup_series = filtered_dataframe[derived_column(ACCOUNT_CODE_FIELD)].astype("string").map(rollup_map)
    missing_rollup_rows = rollup_series.isna()
    if bool(missing_rollup_rows.any()):
        sample_accounts = (
            filtered_dataframe.loc[missing_rollup_rows, derived_column(ACCOUNT_CODE_FIELD)]
            .dropna()
            .astype(str)
            .drop_duplicates()
            .tolist()[:10]
        )
        raise ValueError(
            "❌ Hay cuentas válidas sin Roll Up en Filtros Consolidado. "
            f"Ejemplos: {sample_accounts}"
        )

    rollup_source = filtered_dataframe.loc[:, value_columns].copy()
    rollup_source["Roll Up"] = rollup_series.to_numpy()
    rollup_source = rollup_source.groupby("Roll Up")[value_columns].sum()
    rollup_by_month = pd.DataFrame(index=rollup_source.index)
    actual_months: list[int] = []
    forecast_months: list[int] = []

    for column in value_columns:
        month_number = _month_number_from_column(column)
        scenario = _scenario_from_column(column)
        rollup_by_month[month_number] = rollup_source[column].astype(float)

        if scenario == "Actual":
            actual_months.append(month_number)
        else:
            forecast_months.append(month_number)

    actual_months = sorted(month for month in set(actual_months) if month <= current_month)
    forecast_months = sorted(month for month in set(forecast_months) if month > current_month)

    return Task5ProcessingResult(
        cleaned_dataframe=cleaned_dataframe,
        filtered_dataframe=filtered_dataframe,
        rollup_by_month=rollup_by_month,
        actual_months=actual_months,
        forecast_months=forecast_months,
    )