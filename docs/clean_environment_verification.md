# Clean-environment verification

Verification date: 2026-09-21

## Scope

A separate virtual environment named `.verify_venv` was created from the bundled Python runtime. The existing project `.venv` was not reused. The package was installed only from the dependency declaration in `pyproject.toml`; no API call and no frozen test-set run was performed.

## Environment

| Component | Version |
|---|---:|
| Python | 3.12.14 |
| OpenAI Python package | 3.16.2 |
| Pydantic | 2.13.5 |
| ReportLab | 5.0.1 |
| Streamlit | 1.64.0 |

`pip check` reported: `No broken requirements found.`

## Checks performed

1. Installed the local project in editable mode from `pyproject.toml`.
2. Ran all 15 `unittest` tests in the clean environment: all passed.
3. Ran dry-run preparation for B0, M1, M2, and H1 on the validation split: all four artifacts were produced without API calls.
4. Started the Streamlit application on temporary port 8502 using the clean environment.
5. Queried `/_stcore/health`: HTTP 200 with body `ok`.
6. Stopped the temporary server after the health check.
7. Compared the generated dataset hashes with `data/generated/manifest.json`; all six tracked data files match the manifest.

## Result

**Pass.** The README installation path, automated tests, experiment dry-run, dataset integrity, and application startup are reproducible in a newly created environment. The final test split was not rerun and the frozen prompt, threshold, model configuration, and test artifacts were not changed.

The temporary `.verify_venv` and `.verify_tmp` directories are disposable and excluded from version control.

## Final submission re-verification

Re-verification date: 2026-10-01

The complete current test suite was rerun from submission commit `de2a35081a92cc8e6b42aa46fac7cac26fc4a8e9` with:

```powershell
python -m unittest discover -s tests -v
```

Result: **24 tests run, 24 passed, 0 failures and 0 errors** in 0.382 seconds. This run used no API call, did not execute the frozen test set again, and did not change saved model results, prompts, thresholds or evaluation metrics.
