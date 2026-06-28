from pydantic import BaseModel, Field


class FileLoadRequest(BaseModel):
    filename: str


class FileDescribeRequest(BaseModel):
    filename: str
    columns: list[str] | None = Field(default=None)


class FileAggregateRequest(BaseModel):
    filename: str
    group_by: list[str]
    metrics: dict[str, str]
