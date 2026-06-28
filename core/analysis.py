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


def aggregate_dataframe(
    df: pd.DataFrame,
    group_by: list[str],
    metrics: dict[str, str],
) -> list[dict[str, Any]]:
    missing_group = [c for c in group_by if c not in df.columns]
    if missing_group:
        raise ValueError(f"group_by columns not found: {missing_group}")

    for col, agg in metrics.items():
        if col not in df.columns:
            raise ValueError(f"Metric column not found: {col!r}")
        if agg not in SUPPORTED_AGGS:
            raise ValueError(f"Unsupported aggregation {agg!r}. Supported: {sorted(SUPPORTED_AGGS)}")

    grouped = df.groupby(group_by, as_index=False).agg(metrics)
    return grouped.to_dict(orient="records")


def get_column_summary(df: pd.DataFrame, columns: list[str]) -> dict[str, Any]:
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ValueError(f"Columns not found: {missing}")

    summary: dict[str, Any] = {}
    for col in columns:
        s = df[col]
        info: dict[str, Any] = {
            "dtype": str(s.dtype),
            "null_count": int(s.isna().sum()),
            "unique_count": int(s.nunique()),
        }
        if pd.api.types.is_numeric_dtype(s):
            info.update({"min": float(s.min()), "max": float(s.max()), "mean": float(s.mean())})
        else:
            top = s.value_counts().head(5)
            info["top_values"] = top.index.tolist()
        summary[col] = info
    return summary


def get_top_n(df: pd.DataFrame, column: str, n: int = 10) -> list[dict[str, Any]]:
    if column not in df.columns:
        raise ValueError(f"Column not found: {column!r}")
    top = df[column].value_counts().head(n).reset_index()
    top.columns = [column, "count"]
    return top.to_dict(orient="records")
