import yaml
from pathlib import Path

# --- Carga del YAML Estático ---
BASE_PROJECT_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_PROJECT_DIR / "config.yml"

if not CONFIG_FILE.exists():
    raise FileNotFoundError(f"❌ Falta config.yaml en: {CONFIG_FILE}")

with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    _CFG = yaml.safe_load(f)

# --- Constantes Estáticas (Se cargan al iniciar) ---
ROOT_DIR = Path(_CFG["paths"]["root"])
TASK_DIR = ROOT_DIR / _CFG["paths"]["task_folder"]

# Archivos Fijos
FILE_FILTROS = ROOT_DIR / _CFG["files"]["filtros_exact_name"]
FILE_TEMPLATE_PL = TASK_DIR / _CFG["files"]["template_pl_name"]

# Prefijos
PREFIX_NII = _CFG["files"]["nii_prefix"]
PREFIX_EXP = _CFG["files"]["expenses_prefix"]
PREFIX_TAX = _CFG["files"]["taxes_prefix"]

# Nombres Salida
NAME_OUTPUT_PL = _CFG["files"]["output_pl_name"]
NAME_OUTPUT_UM = _CFG["files"]["output_um_name"]

# --- Variables Dinámicas (Empiezan vacías) ---
YEAR = None
MONTH = None
INPUT_DIR = None
OUTPUT_DIR = None
FILE_OUTPUT_PL = None
FILE_OUTPUT_UM = None

def setup(year: int, month: int):
    """
    Configura las rutas dinámicas.
    Debe ser llamado con argumentos obligatorios antes de procesar nada.
    """
    if not year or not month:
        raise ValueError("❌ Error de Configuración: Debes especificar 'year' y 'month'.")

    global YEAR, MONTH, MONTH_NUM, INPUT_DIR, OUTPUT_DIR
    global FILE_OUTPUT_PL, FILE_OUTPUT_UM

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
        12: "Diciembre"
        }

    YEAR = str(year)
    MONTH_NUM = month
    MONTH = f"{str(month).zfill(2)} - {MESES_ESPANOL[month]}"

    # Construcción de rutas: Root / Tarea / Año / Mes
    INPUT_DIR = TASK_DIR / YEAR / MONTH
    
    # Output dentro de la carpeta del mes
    OUTPUT_DIR = INPUT_DIR / _CFG["paths"]["output_subfolder"]

    # Rutas finales de salida
    FILE_OUTPUT_PL = OUTPUT_DIR / NAME_OUTPUT_PL
    FILE_OUTPUT_UM = OUTPUT_DIR / NAME_OUTPUT_UM