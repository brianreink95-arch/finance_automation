# 📊 Automatización de Reportes Financieros (P&L y Reporte UM)

Este proyecto automatiza la carga, procesamiento (Pandas) y actualización de reportes financieros mensuales (P&L y Reporte UM) utilizando datos extraídos de Excel, siguiendo el principio de la **separación de lógica** (archivos de entrada separados, lógica de negocio encapsulada).

---

## 1. 📂 Estructura del Proyecto

El código está organizado en el paquete principal **`tarea2`**, con la configuración separada en `config.yml`.

```text
finance_automation/             # (Raíz)
├── config.yml                  # Parámetros estáticos (rutas, nombres de archivos fijos)
├── main.py                     # Ejecutable principal
├── requirements.txt            # Dependencias del entorno
│
├── tarea2/                     # PAQUETE DE CÓDIGO CENTRAL
│   ├── settings.py             # Carga config.yml y construye rutas dinámicas
│   ├── loader.py               # Funciones para buscar Excels por prefijo y cargarlos
│   ├── processor.py            # Contiene toda la lógica de Pandas (Merge, GroupBy, Cálculos)
│   └── reporter.py             # Lógica para Openpyxl y guardar los Outputs
│
├── .venv/                      # Entorno virtual (IGNORADO por Git)
└── data/                       # Carpeta de trabajo local (IGNORADA por Git)


---

## 2. 🚀 Instalación y Ejecución

Para correr el script, necesitas Python 3.9+ y autenticación en tu entorno local.

### 2.1. Preparar el Entorno

Abre tu terminal en la carpeta raíz del proyecto y ejecuta:

1.  **Crear y Activar el Entorno Virtual:**
    
    # Windows (PowerShell)
    python -m venv .venv
    .\.venv\Scripts\activate
    
    # Linux/macOS
    # python3 -m venv .venv
    # source .venv/bin/activate

2.  **Instalar Dependencias:**
    
    pip install -r requirements.txt


### 2.2. Configuración de Rutas (Local)

Antes de ejecutar, debes ajustar la variable `root` en el archivo **`config.yml`** para que apunte a la ruta de tu carpeta sincronizada de OneDrive.

# config.yml
paths:
  # Asegúrate que esta ruta sea la ABSOLUTA de tu carpeta local
  root: "C:/Users/reinkeb/MetLife/Planning - Proyecto Planning 2.0"


### 2.3. Ejecución del Proceso

El script requiere obligatoriamente el **año** y el **mes numérico** como argumentos de línea de comandos. El script buscará automáticamente el archivo dentro de la carpeta `[Año]/[Mes - Nombre]`.

| Parámetro | Tipo | Descripción | Ejemplo |
| :--- | :--- | :--- | :--- |
| `--year` | `str` | Año de procesamiento. | `2025` |
| `--month` | `int` | Mes numérico (1-12). | `8` (para Agosto) |

**Ejemplo de ejecución:**

python main.py --year 2025 --month 8


---

## 3. ⚙️ Flujo del Proceso

El script realiza las siguientes acciones:

1.  **Setup (`settings.py`):** Toma `2025` y `8` y resuelve la ruta completa de la carpeta de Input a: `.../Tarea 2/.../2025/08 - Agosto`.
2.  **Load (`loader.py`):** Escanea la carpeta `08 - Agosto` para encontrar archivos que comiencen con los prefijos definidos (ej: `ARG_NII_HYP`).
3.  **Process (`processor.py`):** Ejecuta la lógica de Merge, GroupBy (Roll Up, UM) y calcula los totales.
4.  **Report (`reporter.py`):**
    * Abre el template P&L (`P&L ARG.xlsx`) usando `openpyxl`.
    * Busca la columna `J` (correspondiente a `mes=8`) y la fila de cada cuenta.
    * Inserta los totales y guarda el resultado.
    * Genera el `Reporte UM.xlsx` desde el DataFrame final.