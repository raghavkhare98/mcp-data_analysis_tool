from typing import Any

import pandas as pd

SUPPORTED_AGGS = {"sum", "mean", "median", "count", "min", "max"}


def describe_dataframe(df: pd.DataFrame, columns: list[str] | None = None) -> dict[str, Any]:
    target = df[columns] if columns else df
    numeric = target.select_dtypes(include="number")

    result: dict[str, Any] = {}
    for col in numeric.columns:
        s = numeric[col].dropna()
        mode_vals = s.mode()
        result[col] = {
            "count": int(s.count()),
            "mean": float(s.mean()) if len(s) else None,
            "median": float(s.median()) if len(s) else None,
            "mode": float(mode_vals.iloc[0]) if not mode_vals.empty else None,
            "min": float(s.min()) if len(s) else None,
            "max": float(s.max()) if len(s) else None,
            "std": float(s.std()) if len(s) > 1 else None,
            "null_count": int(numeric[col].isna().sum()),
        }
    return result