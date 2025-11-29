import pandas as pd
from pathlib import Path
from typing import Union

# El tipo Path se usa porque config.py construye los paths como objetos Path de pathlib

def cargar_excel_exacto(ruta_completa: Path, header: int = 1, sheet_name: str | int | list[str | int] | None = None) -> pd.DataFrame:
    """
    Carga un archivo Excel desde una ruta local completa y exacta (usado para Filtros/Templates).

    Args:
        ruta_completa (Path): Ruta absoluta al archivo.
        header (int): Índice de la fila de encabezado (0-indexed).
        sheet_name (str | int | list[str | int] | None): El nombre o índice de la hoja a cargar. 
                                                         (ej: 'Sheet1', 0, ['Sheet1', 'Sheet2']).
    
    Returns:
        pd.DataFrame: DataFrame(s) cargado(s).
    """
    print(f"   📄 Cargando archivo exacto: {ruta_completa.name}")
    if not ruta_completa.exists():
        raise FileNotFoundError(f"❌ Error: No se encontró el archivo fijo: {ruta_completa}")
    
    # Si se especifica el sheet_name, lo incluimos en la llamada a pd.read_excel
    if sheet_name is not None:
        print(f"   -> Usando hoja: {sheet_name}")
    
    return pd.read_excel(ruta_completa, header=header, sheet_name=sheet_name)


def cargar_excel_por_prefijo(carpeta: Path, prefijo: str, header: int = 1) -> pd.DataFrame:
    """
    Busca un archivo en 'carpeta' que comience con 'prefijo' (ej. ARG_NII_HYP) y lo carga.

    Args:
        carpeta (Path): Carpeta donde buscar (ej: .../2025/08 - Agosto).
        prefijo (str): Prefijo del nombre de archivo (ej: ARG_NII_HYP).
        header (int): Índice de la fila de encabezado.

    Returns:
        pd.DataFrame: DataFrame cargado.
    """
    print(f"   🔎 Buscando prefijo: '{prefijo}' en {carpeta.name}...")

    # Usamos glob para encontrar archivos que cumplan el patrón (startswith + extensión)
    # Ejemplo: busca 'ARG_NII_HYP*.xlsx'
    candidatos = list(carpeta.glob(f"{prefijo}*.xlsx"))

    if not candidatos:
        raise FileNotFoundError(f"❌ No encontré archivos con el prefijo '{prefijo}' en {carpeta}")
    
    if len(candidatos) > 1:
        print(f"⚠️ Advertencia: Se encontraron {len(candidatos)} archivos. Usando el primero: {candidatos[0].name}")

    archivo_final = candidatos[0]
    print(f"   ✅ Encontrado: {archivo_final.name}")
    
    return pd.read_excel(archivo_final, header=header)