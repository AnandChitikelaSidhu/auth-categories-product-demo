from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PaginatedMeta(BaseModel):
    model_config = ConfigDict(strict=True)

    total_count: int
    page: int
    page_size: int
    pages: int
