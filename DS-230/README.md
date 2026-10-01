# DS-230 Semester Project: NHTSA Vehicle Recall Analysis

## Executive Summary
The [DS230_Semester_Project.ipynb](https://github.com/Coin010/Projects/blob/main/DS-230/DS230_Semester_Project.ipynb) notebook focuses on gathering, organizing, and analyzing vehicle recall data provided by the National Highway Traffic Safety Administration (NHTSA) API over a 10-year period (2016–2025).

### Key Workflow Stages
1. **Data Acquisition:** Executes Bash scripts to query NHTSA endpoints, retrieving raw JSON payloads for vehicle makes, models, and specific recalls.
2. **Data Organization:** Structures raw API responses into organized, multi-tier directory trees categorized by year (`data/YYYY/makes/`, `models/`, `recalls/`).
3. **Data Aggregation & Cleaning:** Unzips, parses, and aggregates individual JSON outputs into a single consolidated file (`all_recalls.json`), subsequently exporting cleaned tabular datasets (`df_all_exported.csv`, `makes_df.csv`, `recalls_df.csv`) for downstream statistical modeling.

---

## Technical Skills & Technologies Demonstrated

* **Bash Scripting & Automation:** Executing multi-stage shell scripts via Jupyter cell magics (`%%bash`) to automate large-scale batch downloads.
* **REST API Integration:** Querying dynamic API endpoints, handling request parameters (`modelYear`, `make`, `issueType`), and handling HTTP requests using `curl`.
* **JSON Parsing & Data Extraction:** Utilizing command-line JSON processors (`jq`) alongside Python modules to extract key-value pairs from nested data structures.
* **File & Directory Management:** Implementing structured directory trees using shell commands (`mkdir -p`, `mv`) and archiving utilities (`unzip`) for efficient data storage.
* **Python Data Processing:** Cleaning, structuring, and exporting tabular datasets into standardized CSV files for analytical workflows.
