# Project Guidelines

## Scope
- This repository is evolving into a single finance automation program for Planning 2.0.
- Today it contains Task 2 reporting automation, and the next implementation target is Task 5 forecast integration.
- The target direction is one program where Facu can choose whether to run Task 2 or Task 5.

## First Files To Read
- Start with [README.md](README.md) for setup and execution examples.
- Read [main.py](main.py) to understand the CLI flow.
- Read [config.yml](config.yml) before changing paths, file names, or output behavior.
- Existing business logic lives under [tarea2/](tarea2).
- When implementing Task 5, keep new logic isolated from Task 2 internals unless it is truly shared.

## Architecture
- [main.py](main.py) is the current entrypoint and should become the shared CLI dispatcher for Task 2 and Task 5.
- [tarea2/settings.py](tarea2/settings.py) loads `config.yml` once and exposes module-level globals such as `INPUT_DIR`, `OUTPUT_DIR`, and output paths.
- [tarea2/loader.py](tarea2/loader.py) resolves required Excel inputs by exact file name or prefix.
- [tarea2/processor.py](tarea2/processor.py) owns the Pandas merge, grouping, totals, and UM report assembly.
- [tarea2/reporter.py](tarea2/reporter.py) owns workbook writes with `openpyxl` and final Excel export.
- For Task 5, prefer a sibling package and shared orchestration instead of growing `tarea2` into a mixed-responsibility module.

## Working Conventions
- Preserve the current separation of concerns: config and path resolution in `settings`, I/O in `loader` and `reporter`, business rules in `processor`.
- Prefer small changes in the owning module instead of adding business logic directly to `main.py`.
- Keep Spanish business labels and existing Excel-facing strings unchanged unless the task requires a business mapping change.
- Treat `config.yml` as environment-specific. Do not hardcode user-specific paths in Python files.
- Be careful with module globals from `settings.py`; most runtime paths are only valid after `settings.setup(year, month)` runs.
- For the Task 2 plus Task 5 convergence, share only orchestration, common validation utilities, and config conventions. Keep task-specific transformations in separate modules.
- Task 5 must preserve financial control checks: cleaned totals must reconcile against source totals before downstream integration.

## Inputs And Assumptions
- The process requires `--year` and `--month` on the CLI.
- The configured `paths.root` must point to the local synced OneDrive structure described in [README.md](README.md).
- Input discovery depends on these prefixes from [config.yml](config.yml): `ARG_NII_HYP`, `ARG_EXPENSES_HYP`, and `ARG_INCOMETAX_HYP`.
- Report generation assumes the P&L workbook keeps the current sheet name, month header layout, and row anchors used in [tarea2/reporter.py](tarea2/reporter.py).
- Task 5 input will come from a monthly Planning or SmartView export with inconsistent row structure, noisy labels, account codes, cost centers, and value columns that require cleaning before mapping.
- Task 5 raw input is produced by Facundo from an Excel workbook connected to Oracle Hyperion; that workbook opens all accounting bases and then all cost centers before exporting the initial forecast extract used by this repo.
- In the raw Task 5 extract, column B represents the accounting base and column C represents the cost center.
- Task 5 processing must strip formatting noise, retain only valid mapped accounts, standardize cost centers, handle known exceptions, and fail loudly on reconciliation mismatches.

## Validation
- Install dependencies with `pip install -r requirements.txt` inside the project virtual environment.
- Preferred end-to-end check should remain a single CLI entrypoint, currently `python main.py --year <YYYY> --month <M>`, and should evolve to include task selection without breaking Task 2.
- Only run the end-to-end command when the local OneDrive inputs and templates exist; otherwise validate with narrower file-scoped checks.
- When changing business logic, validate the touched slice first before widening scope.
- For Task 5, always validate reconciliation between raw source totals and cleaned totals before integrating with forecast or actual outputs.

## Custom Agent
- Use [.github/agents/finance-automation.agent.md](.github/agents/finance-automation.agent.md) when the task is about Task 2, Task 5, shared CLI design, finance mappings, reconciliation checks, or monthly input handling.