import sys
import os
import argparse

# Como 'tarea2' está en la raíz, ya no hace falta sys.path.append raros
from tarea2 import settings, loader, processor, reporter
from tarea5.accounts_config import generate_accounts_config
from tarea5 import settings as task5_settings
from tarea5 import loader as task5_loader
from tarea5 import processor as task5_processor
from tarea5 import reporter as task5_reporter


def run_task2(args: argparse.Namespace) -> None:
    try:
        settings.setup(
            year=args.year,
            month=args.month,
            use_previous_report_template=args.use_previous_report_template,
        )
    except Exception as e:
        print(e)
        return

    if args.use_previous_report_template and not settings.FILE_TEMPLATE_PL.exists():
        print(
            "❌ No existe el P&L del mes anterior para usar como template: "
            f"{settings.FILE_TEMPLATE_PL}"
        )
        return

    if not settings.FILE_ACCOUNTS_CONFIG.exists():
        print(f"🧩 No existe el config de cuentas. Generándolo desde: {settings.FILE_FILTROS.name}")
        generate_accounts_config(
            source_path=settings.FILE_FILTROS,
            output_path=settings.FILE_ACCOUNTS_CONFIG,
        )

    print("="*60)
    print(f"🚀 PROYECTO PLANNING 2.0 - Tarea 2 para: {settings.MONTH} {settings.YEAR}")
    print(f"📂 Inputs: {settings.INPUT_DIR}")
    print(f"📄 Template P&L: {settings.FILE_TEMPLATE_PL}")
    print("="*60)

    try:
        if not settings.INPUT_DIR.exists():
            raise FileNotFoundError(f"❌ No existe la carpeta de inputs: {settings.INPUT_DIR}")

        print("\n📥 Cargando archivos y validando su existencia...")
        df_filtros = loader.cargar_excel_exacto(settings.FILE_FILTROS, sheet_name="Accounts", header=1)
        df_nii = loader.cargar_excel_por_prefijo(settings.INPUT_DIR, settings.PREFIX_NII, header=1)
        df_exp = loader.cargar_excel_por_prefijo(settings.INPUT_DIR, settings.PREFIX_EXP, header=1)
        df_tax = loader.cargar_excel_por_prefijo(settings.INPUT_DIR, settings.PREFIX_TAX, header=1)

        print("\n✅ Todos los archivos necesarios cargados correctamente.")

        print("\n🧮 Ejecutando lógica de negocio...")
        nii_total = processor.calcular_suma_total(df_nii)
        tax_total = processor.calcular_suma_total(df_tax)
        grp_rollup, grp_um, total_expenses = processor.procesar_expenses(df_exp, df_filtros)

        print("\n📝 Generando reportes de salida...")
        reporter.actualizar_pl_excel_local(
            ruta_template=settings.FILE_TEMPLATE_PL,
            ruta_salida=settings.FILE_OUTPUT_PL,
            nii=nii_total,
            taxes=tax_total,
            gastos_rollup=grp_rollup,
            mes_objetivo=settings.MONTH_NUM,
        )

        df_reporte = processor.preparar_reporte_um(grp_um, nii_total, tax_total, total_expenses)
        reporter.guardar_reporte_um_local(df_reporte, settings.FILE_OUTPUT_UM)

        print("\n✅ Proceso finalizado correctamente.")

    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")


def run_task5(args: argparse.Namespace) -> None:
    try:
        task5_settings.setup(year=args.year, month=args.month)
    except Exception as e:
        print(e)
        return

    if not settings.FILE_ACCOUNTS_CONFIG.exists():
        print(f"🧩 No existe el config de cuentas. Generándolo desde: {settings.FILE_FILTROS.name}")
        generate_accounts_config(
            source_path=settings.FILE_FILTROS,
            output_path=settings.FILE_ACCOUNTS_CONFIG,
        )

    print("="*60)
    print(f"🚀 PROYECTO PLANNING 2.0 - Tarea 5 para: {task5_settings.MONTH} {task5_settings.YEAR}")
    print(f"📂 Forecast Input: {task5_settings.FILE_FORECAST}")
    print(f"📄 P&L Base: {task5_settings.FILE_TASK2_REPORT_PL}")
    print(f"📄 Output P&L: {task5_settings.FILE_OUTPUT_PL}")
    print("="*60)

    try:
        task5_loader.validate_required_inputs()

        print("\n📥 Cargando forecast, filtros y metadata...")
        raw_forecast, df_filtros, account_metadata = task5_loader.load_task5_inputs()

        print("\n🧮 Ejecutando limpieza, validaciones y agregación por Roll Up...")
        processing_result = task5_processor.build_task5_rollup_forecast(
            raw_forecast,
            df_filtros,
            account_metadata,
            current_month=args.month,
        )

        print("\n🔎 Validando actuals contra el P&L base de Task 2...")
        task5_reporter.validate_actual_months_against_pl(
            ruta_base_pl=task5_settings.FILE_TASK2_REPORT_PL,
            monthly_rollup=processing_result.rollup_by_month,
            actual_months=processing_result.actual_months,
        )

        print("\n📝 Escribiendo forecast en el nuevo P&L de Task 5...")
        task5_reporter.write_forecast_rollups_to_pl(
            ruta_template=task5_settings.FILE_TASK2_REPORT_PL,
            ruta_salida=task5_settings.FILE_OUTPUT_PL,
            monthly_rollup=processing_result.rollup_by_month,
            forecast_months=processing_result.forecast_months,
        )

        print("\n✅ Proceso finalizado correctamente.")

    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")

def main():
    # 1. Definición de Argumentos OBLIGATORIOS
    parser = argparse.ArgumentParser(description="Automatización P&L Finanzas")
    
    # required=True obliga al usuario a pasar estos datos
    parser.add_argument("--year", type=int, required=True, help="Año del proceso (ej: 2025)")
    parser.add_argument("--month", type=int, required=True, choices=range(1, 13), help="Mes numérico (1-12)")
    parser.add_argument(
        "--task",
        choices=["task2", "task5"],
        default="task2",
        help="Selecciona qué flujo ejecutar.",
    )
    parser.add_argument(
        "--use-previous-report-template",
        action="store_true",
        help="Usa como template P&L el archivo generado en Reportes del mes anterior.",
    )
    
    args = parser.parse_args()

    if args.task == "task2":
        run_task2(args)
        return

    if args.use_previous_report_template:
        print("⚠️ El flag --use-previous-report-template aplica solo a Task 2 y será ignorado en Task 5.")

    run_task5(args)

if __name__ == "__main__":
    main()