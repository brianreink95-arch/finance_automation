from __future__ import annotations

from pathlib import Path

import openpyxl
import pandas as pd

from tarea2.reporter import _encontrar_columna_mes, _encontrar_fila_por_texto


def _load_sheet(path: Path):
    workbook = openpyxl.load_workbook(path)
    return workbook, workbook["P&L ARG"]


def _build_rollup_row_map(sheet, rollups: list[str]) -> dict[str, int]:
    row_map: dict[str, int] = {}
    missing_rollups: list[str] = []

    for rollup in rollups:
        row_number = _encontrar_fila_por_texto(sheet, rollup)
        if row_number is None:
            missing_rollups.append(rollup)
            continue
        row_map[rollup] = row_number

    if missing_rollups:
        raise ValueError(
            "❌ No se encontraron Roll Ups del forecast en el P&L base. "
            f"Ejemplos: {missing_rollups[:10]}"
        )

    return row_map


def validate_actual_months_against_pl(
    ruta_base_pl: Path,
    monthly_rollup: pd.DataFrame,
    actual_months: list[int],
    tolerance: float = 1e-6,
) -> None:
    workbook, sheet = _load_sheet(ruta_base_pl)
    try:
        row_map = _build_rollup_row_map(sheet, monthly_rollup.index.tolist())
        mismatches: list[str] = []

        for month_number in actual_months:
            column_letter = _encontrar_columna_mes(sheet, month_number)
            for rollup_name, expected_value in monthly_rollup[month_number].items():
                current_value = sheet[f"{column_letter}{row_map[rollup_name]}"].value
                current_numeric = 0.0 if current_value in (None, "") else float(current_value)
                if abs(current_numeric - float(expected_value)) > tolerance:
                    mismatches.append(
                        f"- mes={month_number} roll_up={rollup_name} pl={current_numeric} forecast={float(expected_value)}"
                    )

        if mismatches:
            raise ValueError(
                "❌ Los actuals del forecast no coinciden con el P&L base para los meses históricos.\n"
                + "\n".join(mismatches[:50])
            )
    finally:
        workbook.close()


def write_forecast_rollups_to_pl(
    ruta_template: Path,
    ruta_salida: Path,
    monthly_rollup: pd.DataFrame,
    forecast_months: list[int],
) -> None:
    workbook, sheet = _load_sheet(ruta_template)
    try:
        row_map = _build_rollup_row_map(sheet, monthly_rollup.index.tolist())

        for month_number in forecast_months:
            column_letter = _encontrar_columna_mes(sheet, month_number)
            for rollup_name, value in monthly_rollup[month_number].items():
                sheet[f"{column_letter}{row_map[rollup_name]}"] = round(float(value), 2)

        ruta_salida.parent.mkdir(parents=True, exist_ok=True)
        workbook.save(ruta_salida)
    finally:
        workbook.close()