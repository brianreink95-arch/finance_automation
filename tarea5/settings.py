from __future__ import annotations

from pathlib import Path

import yaml


BASE_PROJECT_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_PROJECT_DIR / "config.yml"

if not CONFIG_FILE.exists():
    raise FileNotFoundError(f"❌ Falta config.yaml en: {CONFIG_FILE}")

with CONFIG_FILE.open("r", encoding="utf-8") as config_file:
    _CFG = yaml.safe_load(config_file)


ROOT_DIR = Path(_CFG["paths"]["root"])
TASK2_DIR = ROOT_DIR / _CFG["paths"]["task_folder"]
TASK5_DIR = ROOT_DIR / _CFG["paths"]["task5_folder"]

FILE_FILTROS = ROOT_DIR / _CFG["files"]["filtros_exact_name"]
FILE_ACCOUNTS_CONFIG = BASE_PROJECT_DIR / _CFG["files"]["accounts_config_name"]
NAME_FORECAST_INPUT = _CFG["files"]["forecast_input_name"]
NAME_OUTPUT_PL = _CFG["files"]["output_pl_name"]

YEAR = None
MONTH = None
MONTH_NUM = None
INPUT_DIR = None
OUTPUT_DIR = None
FILE_FORECAST = None
FILE_TASK2_REPORT_PL = None
FILE_OUTPUT_PL = None


MESES_ESPANOL = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre",
}


def _month_folder_name(month: int) -> str:
    return f"{str(month).zfill(2)} - {MESES_ESPANOL[month]}"


def setup(year: int, month: int) -> None:
    if not year or not month:
        raise ValueError("❌ Error de Configuración: Debes especificar 'year' y 'month'.")

    global YEAR, MONTH, MONTH_NUM, INPUT_DIR, OUTPUT_DIR
    global FILE_FORECAST, FILE_TASK2_REPORT_PL, FILE_OUTPUT_PL

    YEAR = str(year)
    MONTH_NUM = month
    MONTH = _month_folder_name(month)

    INPUT_DIR = TASK5_DIR / YEAR / MONTH
    OUTPUT_DIR = INPUT_DIR / _CFG["paths"]["output_subfolder"]
    FILE_FORECAST = INPUT_DIR / NAME_FORECAST_INPUT
    FILE_TASK2_REPORT_PL = TASK2_DIR / YEAR / MONTH / _CFG["paths"]["output_subfolder"] / NAME_OUTPUT_PL
    FILE_OUTPUT_PL = OUTPUT_DIR / NAME_OUTPUT_PL