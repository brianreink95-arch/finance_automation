import sys
import os
import argparse

# Como 'tarea2' está en la raíz, ya no hace falta sys.path.append raros
from tarea2 import settings, loader, processor, reporter

def main():
    # 1. Definición de Argumentos OBLIGATORIOS
    parser = argparse.ArgumentParser(description="Automatización P&L Finanzas")
    
    # required=True obliga al usuario a pasar estos datos
    parser.add_argument("--year", type=int, required=True, help="Año del proceso (ej: 2025)")
    parser.add_argument("--month", type=int, required=True, choices=range(1, 13), help="Mes numérico (1-12)")
    
    args = parser.parse_args()

    # 2. Configurar Rutas Dinámicas
    try:
        settings.setup(year=args.year, month=args.month)
    except Exception as e:
        print(e)
        return

    print("="*60)
    print(f"🚀 PROYECTO PLANNING 2.0 - Tarea 2 para: {settings.MONTH} {settings.YEAR}")
    print(f"📂 Inputs: {settings.INPUT_DIR}")
    print("="*60)

    try:
        # 3. Validaciones Iniciales
        if not settings.INPUT_DIR.exists():
            raise FileNotFoundError(f"❌ No existe la carpeta de inputs: {settings.INPUT_DIR}")
        
        # --- CARGA DE ARCHIVOS ---
        print("\n📥 Cargando archivos y validando su existencia...")
        
        # Se asume que este archivo está en la raíz o en una ubicación fija (no en la carpeta del mes)
        df_filtros = loader.cargar_excel_exacto(settings.FILE_FILTROS, sheet_name="Accounts", header=1) 
        # 2. Archivos dentro de la carpeta del mes:
        df_nii = loader.cargar_excel_por_prefijo(settings.INPUT_DIR, settings.PREFIX_NII, header=1)
        df_exp = loader.cargar_excel_por_prefijo(settings.INPUT_DIR, settings.PREFIX_EXP, header=1)
        df_tax = loader.cargar_excel_por_prefijo(settings.INPUT_DIR, settings.PREFIX_TAX, header=1)

        print("\n✅ Todos los archivos necesarios cargados correctamente.")

        # 4. PROCESAMIENTO (Cálculos de Pandas)
        print("\n🧮 Ejecutando lógica de negocio...")
        nii_total = processor.calcular_suma_total(df_nii)
        tax_total = processor.calcular_suma_total(df_tax)
        grp_rollup, grp_um, total_expenses = processor.procesar_expenses(df_exp, df_filtros)

        # 5. REPORTE Y SALVADO DE ARCHIVOS
        print("\n📝 Generando reportes de salida...")
        
        # A. Actualizar Template P&L (Openpyxl)
        reporter.actualizar_pl_excel_local(
            ruta_template=settings.FILE_TEMPLATE_PL,
            ruta_salida=settings.FILE_OUTPUT_PL,
            nii=nii_total,
            taxes=tax_total,
            gastos_rollup=grp_rollup,
            mes_objetivo=settings.MONTH_NUM # Usamos el entero para openpyxl
        )
        
        # B. Generar Reporte UM (Pandas save)
        df_reporte = processor.preparar_reporte_um(grp_um, nii_total, tax_total, total_expenses)
        reporter.guardar_reporte_um_local(df_reporte, settings.FILE_OUTPUT_UM)

        print("\n✅ Proceso finalizado correctamente.")

    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")

if __name__ == "__main__":
    main()