# pyspark-databricks-example

Przykładowy pipeline PySpark wdrażany do Databricks za pomocą
[Databricks Asset Bundles](https://docs.databricks.com/dev-tools/bundles/index.html).

Job `tmb_analysis_job` czyta tabelę `workspace.default.tmb`, liczy zestawienie
wagi sprzętu per kategoria i zapisuje dwie tabele Delta:

- `workspace.default.tmb_gear_summary` – liczba pozycji, łączna i średnia waga per kategoria
- `workspace.default.tmb_gear_top_per_category` – najcięższa pozycja w każdej kategorii

## Struktura

```
tmb-pipeline/
├── databricks.yml          # definicja bundla + target dev
├── resources/
│   └── jobs.yml            # definicja joba (serverless)
└── src/
    └── tmb_analysis.py     # logika PySpark
```

## Wymagania

- [Databricks CLI](https://docs.databricks.com/dev-tools/cli/install.html) v0.205+ (testowane na v1.4.0)
- Dostęp do workspace Databricks z włączonym serverless compute
- Tabela źródłowa `workspace.default.tmb` z kolumnami: `Item Name`, `Category`, `weight`

## Konfiguracja uwierzytelniania

Najprostszy sposób – profil w `~/.databrickscfg`:

```ini
[DEFAULT]
host  = https://<twoj-workspace>.cloud.databricks.com
token = <personal-access-token>
```

CLI dopasuje profil po `host` zdefiniowanym w `databricks.yml`.
Alternatywnie: `databricks auth login --host https://<twoj-workspace>.cloud.databricks.com`.

## Uruchamianie jobów

Wszystkie komendy wykonuj z katalogu `tmb-pipeline/`:

```bash
cd tmb-pipeline
```

### 1. Walidacja konfiguracji

```bash
databricks bundle validate
```

### 2. Wdrożenie zasobów do workspace

```bash
databricks bundle deploy
```

Wgrywa pliki źródłowe i tworzy job w workspace (target `dev`).

### 3. Uruchomienie joba

```bash
databricks bundle run tmb_analysis_job
```

Komenda czeka na zakończenie i wypisuje link do runu oraz logi.
Po sukcesie zobaczysz: `Done. Wrote tmb_gear_summary and tmb_gear_top_per_category.`

### 4. Podgląd wdrożonych zasobów

```bash
databricks bundle summary
```

### 5. Usunięcie zasobów z workspace

```bash
databricks bundle destroy
```

## Targety

Domyślny target to `dev` (`mode: development`) – zasoby są prefiksowane nazwą
użytkownika, np. `[dev your_name] tmb-analysis-dev`. Host ustawisz w `databricks.yml`.

## Testowanie lokalne

Logika transformacji jest wydzielona do czystych funkcji w `src/tmb_analysis.py`
(`prepare`, `build_summary`, `build_top_per_category`), niezależnych od I/O
(`spark.table` / `saveAsTable`). Dzięki temu można je testować lokalnym PySparkiem,
bez Databricks i bez Unity Catalog.

### Wymagania

- Java 8, 11 lub 17 (PySpark 3.5 nie działa na nowszych)
- Czyste środowisko **bez** `databricks-connect` — jego wbudowany PySpark
  koliduje z pakietem `pyspark`. Użyj osobnego venv tylko do testów.

```bash
python3 -m venv .venv-test
source .venv-test/bin/activate
pip install -e ".[test]"
```

### Uruchomienie testów

```bash
# wskaż Javę 8/11/17, jeśli masz wiele wersji
export JAVA_HOME=$(/usr/libexec/java_home -v 1.8)   # macOS
pytest
```

Testy (`tmb-pipeline/tests/`) tworzą lokalny `SparkSession` (`local[1]`),
budują sztuczny DataFrame i sprawdzają agregacje oraz ranking — bez zapisu do tabel.

### Test integracyjny (opcjonalnie)

Pełny przepływ z prawdziwą tabelą `workspace.default.tmb` najprościej sprawdzić
w workspace przez `databricks bundle run tmb_analysis_job`. Alternatywą jest
[Databricks Connect](https://docs.databricks.com/dev-tools/databricks-connect/index.html),
który wykonuje kod lokalnie, ale Spark uruchamia w Twoim workspace.
