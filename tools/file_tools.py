from typing import Any

from mcp.server.fastmcp import FastMCP

from config import get_settings
from core.analysis import aggregate_dataframe, describe_dataframe, get_column_summary, get_top_n
from core.files import list_available_files, load_dataframe
from core.models import FileAggregateRequest, FileDescribeRequest, FileLoadRequest


def register_tools(mcp: FastMCP) -> None:
    settings = get_settings()

    @mcp.tool()
    def file_list() -> dict[str, list[str]]:
        """Return all CSV and Excel files available in the staging directory."""
        return {"files": list_available_files()}

    @mcp.tool()
    def file_load(filename: str) -> dict[str, Any]:
        """Load a file and return its schema, shape, sample rows, and null counts.

        Args:
            filename: Name of the file in the staging directory (e.g. 'sales.csv').
        """
        req = FileLoadRequest(filename=filename)
        df = load_dataframe(req.filename)

        sample = df.head(5).where(df.head(5).notna(), other=None).to_dict(orient="records")
        null_counts = df.isna().sum().to_dict()

        return {
            "filename": req.filename,
            "columns": list(df.columns),
            "shape": list(df.shape),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "sample_rows": sample,
            "null_counts": {k: int(v) for k, v in null_counts.items()},
        }

    @mcp.tool()
    def file_describe(filename: str, columns: list[str] | None = None) -> dict[str, Any]:
        """Return descriptive statistics for numeric columns.

        Args:
            filename: Name of the file in the staging directory.
            columns: Optional list of column names to describe. Defaults to all numeric columns.
        """
        req = FileDescribeRequest(filename=filename, columns=columns)
        df = load_dataframe(req.filename)
        stats = describe_dataframe(df, req.columns)
        return {"filename": req.filename, "statistics": stats}

    @mcp.tool()
    def file_aggregate(
        filename: str,
        group_by: list[str],
        metrics: dict[str, str],
    ) -> dict[str, Any]:
        """Perform a grouped aggregation on a file.

        Args:
            filename: Name of the file in the staging directory.
            group_by: List of columns to group by.
            metrics: Mapping of column name to aggregation function.
                     Supported functions: sum, mean, median, count, min, max.
        """
        req = FileAggregateRequest(filename=filename, group_by=group_by, metrics=metrics)
        df = load_dataframe(req.filename)
        rows = aggregate_dataframe(df, req.group_by, req.metrics)
        return {"filename": req.filename, "rows": rows[: settings.max_result_rows]}
