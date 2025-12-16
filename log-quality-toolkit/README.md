# Log Quality Toolkit

## Purpose

Tools to load, validate and clean authentication / security logs (CSV or JSON), including messy inputs, and produce a clean dataframe, a data-quality report, and charts.

## Key features

- Loads auth/security logs from CSV or JSON (handles irregular or "messy" formatting).
- Validates schema and timestamps (detects missing/extra fields, wrong types, and invalid/ambiguous timestamps).
- Gracefully handles bad rows and files (bad rows captured separately; unreadable files logged and skipped without failing the pipeline).
- Outputs a cleaned `pandas.DataFrame`, a machine-readable "data quality report" (JSON) and visual charts (PNG/HTML) summarizing issues and quality metrics.

## Typical pipeline

1. Load logs (CSV/JSON) from a folder or stream.
2. Run schema and timestamp validation.
3. Separate or quarantine bad rows/files for review.
4. Produce a cleaned dataframe plus a data-quality report and charts.

## Outputs

- Clean dataframe: a `pandas.DataFrame` ready for analysis.
- Data quality report: JSON summarizing record counts, validation failures, timestamp issues, and per-field metrics.
- Charts: visualizations (PNG/HTML) showing distribution of issues, missingness, and timestamp coverage.
- Bad rows file(s): CSV/JSON with original rows that failed validation for inspection and re-processing.

## Error handling

- Row-level failures are captured and written to a `bad_rows` file rather than aborting execution.
- Corrupted or unreadable files are logged and skipped; the pipeline continues with remaining inputs.

## Example usage (conceptual)

```py
# load files
# df_raw = load_logs(path_or_files)

# validate and clean
# df_clean, report = validate_and_clean(df_raw)

# save results
# report.to_json('quality_report.json')
# df_clean.to_csv('clean_logs.csv', index=False)
```

Want this README expanded? I can add concrete API examples, CLI usage, or sample outputs next.
