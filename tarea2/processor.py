import pandas as pd
from . import settings

# Definiciones de Constantes para el Reporte UM (Se necesitan aquí para construir el DF)
# Esta lista fue extraída de tu notebook original.
CUENTAS_REPORTE_UM = [
    "Año", "Consolidado", "Canal", "Producto", "Contabilidad", "Moneda", 
    "Tipo", "Version", "Mes", "Pais_Moneda", "I41100 - Premiums", 
    "I41210 - COI", "I41220 - Annual Management Charges", "I41230 - Loads", 
    "I41240 - Surrender Charges", "I41250 - UNREV", "I41260 - Other (Unassigned)", 
    "I41300 - Other revenues", "I42000 - Net investment income", "I51100 - Total Benefits", 
    "I51200 - Change in Reserve Excl. Int. Cred. to PAB", "I52000 - Interest credited to policyholder account balances", 
    "I6000000 - Commissions", "I54000 - Capitalization of DAC", "I55110 - Amortization of DAC", 
    "I55120 - Amortization of VOBA", "EMPLOYEE_COSTS - Employee Comp, Benefit & Other", 
    "OPEXP60145 - Corporate Incentive", "OPEXP60147 - COLI & Deferred Comp", "OPEXP66000 - GOSC Services SLA", 
    "DISCRETIONARY_EXP - Total Discretionary Expenses", "OPEXP60126 - Consultants & Programmers", 
    "6462200000 - Third Party Admin", "6469000000 - Contracted Services Total 1", "OPEXP60127 - Other Professional Service", 
    "RENT_RELATED - Rent & Related Expenses", "6480000000 - Legal Settlements-Reserve Chg", "OPEXP61100 - AD Cap & Amort", 
    "OTHER_GEN - Other Gen Admin Exp", "OTH_NON_CONTROL - Oth Non Controllable", "OTHER_DIRECT - Other Miscell Direct Exp", 
    "GTO_SLA - GTO_SLA", "6800000000 - Direct & Alloc Investment Exp", "PREMIUM_TAXES - Premium & Other Taxes", 
    "PPRB - Pension&Post Retirement Benef", "TOT_COMM_OTHVAR - Total Commissions & Oth Var Exp", 
    "I60000 - Provision for income tax expense (benefit)", "OP_EARN - Adjusted earnings",
]

MESES_ABREVIADOS = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec"
}


def calcular_suma_total(df: pd.DataFrame, columna: str = 'Sum Amount') -> float:
    """Calcula la suma total de una columna específica (usado para NII y Taxes)."""
    return df[columna].sum()


def procesar_expenses(df_expenses: pd.DataFrame, df_filtros: pd.DataFrame) -> tuple[pd.Series, pd.Series, float]:
    """
    Procesa el archivo de gastos: une con filtros, aplica agrupaciones Roll Up y UM, y calcula el total.
    """
    # Merge de datos de Expenses con Filtros (por columna 'Cuenta')
    merged_df = df_expenses.merge(df_filtros, on="Cuenta", how="left")
    # 1. Agrupación por Roll Up (Para el P&L)
    grp_rollup = merged_df.groupby("Roll Up")['Sum Amount'].sum()
    # 2. Agrupación por Agrupación UM (Para el Reporte UM)
    grp_um = merged_df.groupby("Agrupación UM")['Sum Amount'].sum()
    # 3. Suma total
    total_expenses = merged_df['Sum Amount'].sum()
    
    return grp_rollup, grp_um, total_expenses


def preparar_reporte_um(grp_um: pd.Series, nii_total: float, tax_total: float, total_expenses: float) -> pd.DataFrame:
    """
    Genera el DataFrame final para el Reporte UM insertando los totales calculados y metadata.
    """
    # Metadata Fija (Según tu notebook original)
    METADATA_UM = {
        "Año": settings.YEAR,
        "Mes": MESES_ABREVIADOS[settings.MONTH_NUM],
        "Consolidado": "ARGCONS-Argentina Consolidated",
        "Canal": "DistributionChannel",
        "Producto": "ALL PRODUCTS - ALL PRODUCTS",
        "Contabilidad": "USGAAP - Normalized",
        "Moneda": "Local Currency",
        "Tipo": "Actual",
        "Version": "No Version",
        "Pais_Moneda": "Argentina - USD -",
    }
    # 1. Crear esqueleto del Reporte UM basado en la lista estática
    reporte = pd.DataFrame(index=CUENTAS_REPORTE_UM)
    # 2. Aplicar ajustes de lógica y renombrado (Según tu notebook original)
    # Sumar TOTAL_SLA al RENT_RELATED (ajuste de lógica)
    if "TOTAL_SLA - Total SLA" in grp_um and "RENT_RELATED - Rent & Related Expenses" in grp_um:
        grp_um["RENT_RELATED - Rent & Related Expenses"] += grp_um["TOTAL_SLA - Total SLA"]

    # Limpieza/Re-mapeo de Índices (Según tu notebook)
    def clean_index(idx):
        if str(idx).startswith("EMPLOYEE_COSTS"):
            return "EMPLOYEE_COSTS - Employee Comp, Benefit & Other"
        if str(idx).startswith("OPEXP61100"):
            return "OPEXP61100 - AD Cap & Amort"
        return idx
            
    grp_um.index = [clean_index(x) for x in grp_um.index]  

    # 3. Merge de datos calculados con el Reporte
    # Creamos una columna 'Sum Amount' que contendrá los valores
    reporte = reporte.merge(grp_um, left_index=True, right_index=True, how='left')

    # Forzar el tipo a 'object' para que acepte float (valores) y str/int (metadata) sin warning
    if 'Sum Amount' in reporte.columns:
        reporte['Sum Amount'] = reporte['Sum Amount'].astype(object)

    # 4. Inserción de Totales y Cálculo Final
    # NII (Net Investment Income)
    reporte.loc["I42000 - Net investment income", "Sum Amount"] = nii_total * -1 
    # Taxes
    reporte.loc["I60000 - Provision for income tax expense (benefit)", "Sum Amount"] = tax_total 
    # Cálculo de la Ganancia Operativa (OP. EARN AFTER TAX)
    # OP_EARN = -NII_TOTAL - EXPENSES_TOTAL - TAXES_TOTAL
    reporte.loc["OP_EARN - Adjusted earnings", "Sum Amount"] = -nii_total - total_expenses - tax_total
    
    # 5. Inserción de Metadatos
    for key, value in METADATA_UM.items():
        if key in reporte.index:
            reporte.loc[key, "Sum Amount"] = value  
    
    return reporte.fillna(0)